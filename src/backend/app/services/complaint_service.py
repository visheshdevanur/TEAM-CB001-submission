from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.models import Complaint, Evidence
from app.schemas.complaint import ComplaintCreate
from app.schemas.evidence import EvidenceCreate
import uuid
from datetime import datetime, timezone
from typing import List, Any

class ComplaintService:
    async def create_complaint(self, db: AsyncSession, complaint_data: ComplaintCreate):
        complaint_number = f"MYS-{uuid.uuid4().hex[:6].upper()}"
        db_complaint = Complaint(
            **complaint_data.model_dump(),
            complaint_number=complaint_number
        )
        db.add(db_complaint)
        await db.commit()
        await db.refresh(db_complaint)
        return db_complaint

    async def get_complaint(self, db: AsyncSession, complaint_id: int):
        return await db.get(Complaint, complaint_id)

    async def list_complaints(self, db: AsyncSession):
        from sqlalchemy import select
        result = await db.execute(select(Complaint).order_by(Complaint.created_at.desc()))
        return result.scalars().all()

class EvidenceService:
    async def add_evidence(self, db: AsyncSession, complaint_id: int, evidence_data: EvidenceCreate, file_path: str):
        db_evidence = Evidence(
            **evidence_data.model_dump(),
            complaint_id=complaint_id,
            file_path=file_path
        )
        db.add(db_evidence)
        await db.commit()
        await db.refresh(db_evidence)
        return db_evidence

    async def add_evidence_with_quality(self, db: AsyncSession, complaint_id: int, evidence_data: EvidenceCreate, file_path: str, quality_score: float, file_data: bytes | None = None, mime_type: str | None = None):
        db_evidence = Evidence(
            **evidence_data.model_dump(),
            complaint_id=complaint_id,
            file_path=file_path,
            quality_score=quality_score,
            file_data=file_data,
            mime_type=mime_type,
        )
        db.add(db_evidence)
        await db.commit()
        await db.refresh(db_evidence)
        return db_evidence

    async def add_extracted_frame(self, db: AsyncSession, complaint_id: int, parent_evidence_id: int, file_path: str, timestamp: float):
        db_frame = Evidence(
            complaint_id=complaint_id,
            type="WORK_PROOF",
            file_path=file_path,
            timestamp=datetime.now(timezone.utc),
            sha256=f"frame_{parent_evidence_id}_{timestamp}"
        )
        db.add(db_frame)
        await db.commit()
        await db.refresh(db_frame)
        return db_frame

    async def add_detections(self, db: AsyncSession, evidence_id: int, detections: List[Any]):
        from app.db.models.models import Detection
        for d in detections:
            db_det = Detection(
                evidence_id=evidence_id,
                object_type=d.object_type,
                confidence=d.confidence,
                bbox_x1=d.bbox[0],
                bbox_y1=d.bbox[1],
                bbox_x2=d.bbox[2],
                bbox_y2=d.bbox[3],
                area_pixels=d.area_pixels
            )
            db.add(db_det)
        await db.commit()

    async def get_evidence_by_complaint(self, db: AsyncSession, complaint_id: int):
        from sqlalchemy import select
        result = await db.execute(select(Evidence).where(Evidence.complaint_id == complaint_id))
        return result.scalars().all()

    async def delete_evidence(self, db: AsyncSession, evidence_id: int):
        from app.storage.file_storage import storage_service
        evidence = await db.get(Evidence, evidence_id)
        if not evidence:
            return None

        file_path = evidence.file_path
        await db.delete(evidence)
        await db.commit()

        # Attempt to delete physical file
        try:
            storage_service.delete_file(file_path)
        except Exception as e:
            print(f"Warning: Failed to delete file {file_path}: {e}")

        return True

complaint_service = ComplaintService()
evidence_service = EvidenceService()
