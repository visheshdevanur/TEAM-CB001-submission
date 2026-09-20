from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.models.models import Complaint, Evidence, Comparison, VerificationAction, Notification
from app.ai.detection.issue_detector import issue_detector
from app.ai.comparison.semantic_compare import semantic_comparator
from app.ai.alignment.homography import homography_aligner
from app.ai.comparison.relocation_detector import relocation_detector
from app.ai.scoring.evidence_score import scoring_engine, EvidenceVector
from app.ai.models.vlm import vlm_assistant, VLMExplanationRequest
from app.storage.file_storage import storage_service
import cv2
from pathlib import Path
from tempfile import gettempdir
from typing import Dict, Any, Optional, List

class VerificationService:
    @staticmethod
    def _analysis_image_path(evidence: Evidence) -> str:
        """Return a readable local image path, restoring durable DB evidence if needed.

        Render's local uploads directory is ephemeral and disappears on a deploy.
        Evidence bytes are also stored in PostgreSQL, so recreate a short-lived local
        copy for OpenCV and Gemini whenever the original upload file has gone away.
        """
        legacy_path = Path(storage_service.get_path(evidence.file_path))
        if legacy_path.is_file():
            return str(legacy_path)
        if not evidence.file_data:
            raise ValueError("The stored evidence image is unavailable. Please upload the photo again.")

        suffix = Path(evidence.file_path).suffix or ".jpg"
        cache_dir = Path(gettempdir()) / "mysurudrishti-ai-evidence"
        cache_dir.mkdir(parents=True, exist_ok=True)
        restored_path = cache_dir / f"evidence-{evidence.id}{suffix}"
        restored_path.write_bytes(evidence.file_data)
        return str(restored_path)

    async def run_verification(self, db: AsyncSession, complaint_id: int) -> Comparison:
        # 1. Load Complaint
        complaint = await db.get(Complaint, complaint_id)
        if not complaint:
            raise ValueError("Complaint not found")

        # 2. Find most recent Before and After evidence
        result_before = await db.execute(
            select(Evidence).where(Evidence.complaint_id == complaint_id, Evidence.type == "BEFORE").order_by(desc(Evidence.timestamp))
        )
        before_ev = result_before.scalars().first()

        result_after = await db.execute(
            select(Evidence).where(Evidence.complaint_id == complaint_id, Evidence.type == "AFTER").order_by(desc(Evidence.timestamp))
        )
        after_ev = result_after.scalars().first()

        if not before_ev or not after_ev:
            raise ValueError("Insufficient evidence: both BEFORE and AFTER evidence are required for verification.")

        # 3. Geometric Alignment
        before_path = self._analysis_image_path(before_ev)
        after_path = self._analysis_image_path(after_ev)
        img_before = cv2.imread(before_path)
        img_after = cv2.imread(after_path)

        if img_before is None or img_after is None:
            raise ValueError("The uploaded evidence files could not be read. Please upload clear JPEG or PNG photos and try again.")

        aligned_img, alignment_score, success = homography_aligner.align(img_before, img_after)

        # 4. Run Issue Analysis
        before_analysis = issue_detector.analyze_issue(before_path, complaint.issue_type)
        after_analysis = issue_detector.analyze_issue(after_path, complaint.issue_type)

        # 5. Run Semantic Comparison
        comparison_result = semantic_comparator.compare(before_analysis, after_analysis)
        metrics = comparison_result["metrics"]

        # 6. Run Relocation Detection
        reloc_res = relocation_detector.analyze(before_analysis, after_analysis, complaint.issue_type)

        # 7. Construct evidence signals. In demo mode these are advisory only;
        # the final verdict below always requires a live visual model response.
        temporal_score = 1.0 if before_ev.timestamp < after_ev.timestamp else 0.0

        vector = EvidenceVector(
            quality=( (before_ev.quality_score or 0) + (after_ev.quality_score or 0) ) / 200.0,
            alignment=alignment_score,
            issue_before=1.0 if before_analysis["issue_present"] else 0.0,
            reduction=metrics.get("reduction_percent", 0) / 100.0,
            temporal=temporal_score,
            relocation_risk=reloc_res["relocation_score"]
        )

        overall_score = scoring_engine.calculate_score(vector)
        final_verdict = scoring_engine.get_verdict(overall_score)

        # Keep relocation evidence as context, but do not let a filename-driven
        # demo detector decide the final result.
        explanation = comparison_result["explanation"]
        if reloc_res["relocation_possible"]:
            final_verdict = "RELOCATED_POSSIBLE"
            explanation = f"{explanation} {reloc_res['explanation']}"

        # 8. Live visual-model reasoning. This is the authority for the final
        # result because it can reject unrelated images before assessing change.
        vlm_request = VLMExplanationRequest(
            complaint_id=complaint_id,
            issue_type=complaint.issue_type,
            metrics={**metrics, "relocation_possible": reloc_res["relocation_possible"]},
            before_image_path=before_path,
            after_image_path=after_path
        )
        vlm_res = vlm_assistant.generate_explanation(vlm_request)

        verdict_map = {
            "RESOLVED": "RESOLUTION_SUPPORTED",
            "PARTIALLY_RESOLVED": "PARTIALLY_RESOLVED",
            "NOT_RESOLVED": "NOT_RESOLVED",
            "CATEGORY_MISMATCH": "CATEGORY_MISMATCH",
            "DIFFERENT_SCENE": "LOCATION_MISMATCH",
            "INCONCLUSIVE": "INSUFFICIENT_EVIDENCE",
        }
        final_verdict = verdict_map.get(vlm_res.verdict, "INSUFFICIENT_EVIDENCE")
        final_explanation = vlm_res.explanation
        # The displayed score must come from the live visual model, never from
        # demo detector areas or filenames.
        overall_score = float(vlm_res.visual_score if vlm_res.is_real_ai else 0)

        # 9. Create Comparison Record
        db_comparison = Comparison(
            complaint_id=complaint_id,
            before_evidence_id=before_ev.id,
            after_evidence_id=after_ev.id,
            affected_area_before=before_analysis["affected_area_pixels"],
            affected_area_after=after_analysis["affected_area_pixels"],
            affected_area_change=metrics.get("area_change"),
            result=final_verdict,
            explanation=final_explanation,
            landmark_match_score=alignment_score,
            overall_evidence_score=overall_score
        )

        db.add(db_comparison)
        await db.commit()
        await db.refresh(db_comparison)

        # 10. The live visual AI result is final; no separate human-verification
        # queue is used in this workflow.
        complaint.status = {
            "RESOLUTION_SUPPORTED": "VERIFIED_RESOLVED",
            "PARTIALLY_RESOLVED": "PARTIALLY_RESOLVED",
            "NOT_RESOLVED": "NOT_RESOLVED",
            "CATEGORY_MISMATCH": "INSUFFICIENT_EVIDENCE",
            "LOCATION_MISMATCH": "INSUFFICIENT_EVIDENCE",
            "INSUFFICIENT_EVIDENCE": "INSUFFICIENT_EVIDENCE",
        }.get(final_verdict, "INSUFFICIENT_EVIDENCE")
        if final_verdict == "RESOLUTION_SUPPORTED" and overall_score >= 90 and complaint.created_by:
            db.add(Notification(
                user_id=complaint.created_by,
                complaint_id=complaint.id,
                kind="RESOLVED",
                title="Your complaint was resolved",
                message=f"{complaint.complaint_number} received an AI score of {int(overall_score)}/100. The Before/After evidence supports that the issue is resolved.",
            ))
        elif complaint.assigned_worker_id:
            db.add(Notification(
                user_id=complaint.assigned_worker_id,
                complaint_id=complaint.id,
                kind="REWORK",
                title="Further work or clearer evidence is needed",
                message=f"{complaint.complaint_number} received an AI score of {int(overall_score)}/100 ({final_verdict.replace('_', ' ').lower()}). Please revisit the issue and upload a new After photo.",
            ))
        await db.commit()

        return db_comparison

    async def submit_human_decision(self, db: AsyncSession, action_data: Any):
        db_action = VerificationAction(
            comparison_id=action_data.comparison_id,
            reviewer_id=action_data.reviewer_id,
            decision=action_data.decision,
            reason=action_data.reason
        )
        db.add(db_action)

        from sqlalchemy import select
        result = await db.execute(select(Comparison).where(Comparison.id == action_data.comparison_id))
        comparison = result.scalars().first()

        if comparison:
            complaint = await db.get(Complaint, comparison.complaint_id)
            if complaint:
                status_map = {
                    "CONFIRM_FIX": "VERIFIED_RESOLVED",
                    "PARTIAL_FIX": "PARTIALLY_RESOLVED",
                    "NOT_FIXED": "NOT_RESOLVED",
                    "REQUEST_FIELD_INSPECTION": "HUMAN_REVIEW",
                    "INSUFFICIENT_EVIDENCE": "INSUFFICIENT_EVIDENCE"
                }
                complaint.status = status_map.get(action_data.decision, "HUMAN_REVIEW")

        await db.commit()
        await db.refresh(db_action)
        return db_action

    async def get_verification_queue(self, db: AsyncSession):
        from sqlalchemy import select
        result = await db.execute(select(Complaint).where(Complaint.status == "AI_VERIFICATION"))
        return result.scalars().all()

verification_service = VerificationService()
