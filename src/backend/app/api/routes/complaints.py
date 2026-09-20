from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.database import get_db
from app.services.complaint_service import complaint_service, evidence_service
from app.services.video_service import video_service
from app.schemas.complaint import ComplaintCreate, ComplaintResponse
from app.schemas.evidence import EvidenceCreate, EvidenceResponse
from app.storage.file_storage import storage_service
from app.ai.quality.image_quality import quality_engine
from app.ai.detection.issue_detector import issue_detector
from app.core.security import current_user
from app.db.models.models import User, Complaint, Evidence
from app.api.routes.areas import assign_by_location
from app.db.models.models import Comparison
from sqlalchemy import select
from datetime import datetime, timezone, timedelta
import json

router = APIRouter(tags=["Complaints"])
optional_bearer = HTTPBearer(auto_error=False)

def service_area_for(latitude: float) -> str:
    if latitude >= 12.33:
        return "NORTH"
    if latitude <= 12.28:
        return "SOUTH"
    return "CENTRAL"

async def optional_user(credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer), db: AsyncSession = Depends(get_db)):
    if not credentials:
        return None
    # Reuse the strict auth check only when a bearer token was supplied.
    return await current_user(credentials, db)

async def process_video_background(complaint_id: int, evidence_id: int, file_path: str):
    """
    Background task to extract frames and add them to the database.
    """
    from app.db.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        frames = video_service.extract_key_frames(file_path, evidence_id)
        for i, frame_path in enumerate(frames):
            await evidence_service.add_extracted_frame(
                db, complaint_id, evidence_id, frame_path, float(i)
            )

@router.post("/", response_model=ComplaintResponse)
async def create_complaint(
    complaint_data: ComplaintCreate,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_user)
):
    complaint = await complaint_service.create_complaint(db, complaint_data)
    if user and user.role == "PUBLIC":
        complaint.created_by = user.id
    await assign_by_location(db, complaint)
    await db.commit()
    await db.refresh(complaint)
    return complaint

@router.get("/mine", response_model=List[ComplaintResponse])
async def my_complaints(db: AsyncSession = Depends(get_db), user: User = Depends(current_user)):
    if user.role != "PUBLIC":
        raise HTTPException(403, "Public account required")
    result = await db.execute(select(Complaint).where(Complaint.created_by == user.id).order_by(Complaint.created_at.desc()))
    return result.scalars().all()

@router.get("/worker/inbox", response_model=List[ComplaintResponse])
async def worker_inbox(db: AsyncSession = Depends(get_db), user: User = Depends(current_user)):
    if user.role != "WORKER":
        raise HTTPException(403, "Worker account required")
    result = await db.execute(select(Complaint).where(Complaint.assigned_worker_id == user.id).order_by(Complaint.created_at.desc()))
    return result.scalars().all()

@router.get("/workers/{worker_id}/complaints")
async def worker_complaint_status(worker_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)):
    if user.role != "ADMIN":
        raise HTTPException(403, "MCC administrator access required")
    worker = await db.get(User, worker_id)
    if not worker or worker.role != "WORKER":
        raise HTTPException(404, "Worker not found")
    complaints = (await db.execute(select(Complaint).where(Complaint.assigned_worker_id == worker_id).order_by(Complaint.created_at.desc()))).scalars().all()
    now = datetime.now(timezone.utc)
    return {"worker": {"id": worker.id, "name": worker.name, "email": worker.email}, "complaints": [{
        "id": complaint.id, "complaint_number": complaint.complaint_number, "address": complaint.address, "issue_type": complaint.issue_type, "status": complaint.status, "created_at": complaint.created_at, "worker_acknowledged_at": complaint.worker_acknowledged_at,
        "overdue": complaint.worker_acknowledged_at is None and complaint.status in {"ASSIGNED", "OPEN"} and now - complaint.created_at > timedelta(days=3),
    } for complaint in complaints]}

@router.post("/{id}/acknowledge", response_model=ComplaintResponse)
async def acknowledge_assignment(id: int, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)):
    if user.role != "WORKER":
        raise HTTPException(403, "Worker account required")
    complaint = await complaint_service.get_complaint(db, id)
    if not complaint or complaint.assigned_worker_id != user.id:
        raise HTTPException(404, "Assigned complaint not found")
    if not complaint.worker_acknowledged_at:
        complaint.worker_acknowledged_at = datetime.now(timezone.utc)
    if complaint.status == "ASSIGNED":
        complaint.status = "IN_PROGRESS"
    await db.commit(); await db.refresh(complaint)
    return complaint

@router.get("/dashboard")
async def dashboard_summary(db: AsyncSession = Depends(get_db), user: User = Depends(current_user)):
    if user.role != "ADMIN":
        raise HTTPException(403, "MCC administrator access required")
    complaints = (await db.execute(select(Complaint))).scalars().all()
    comparisons = (await db.execute(select(Comparison).order_by(Comparison.created_at.desc()))).scalars().all()
    latest_by_complaint = {}
    for comparison in comparisons:
        latest_by_complaint.setdefault(comparison.complaint_id, comparison)
    latest = list(latest_by_complaint.values())
    resolved = sum(c.result == "RESOLUTION_SUPPORTED" for c in latest)
    partial = sum(c.result == "PARTIALLY_RESOLVED" for c in latest)
    not_resolved = sum(c.result == "NOT_RESOLVED" for c in latest)
    needs_review = sum(c.result in {"INSUFFICIENT_EVIDENCE", "CATEGORY_MISMATCH", "LOCATION_MISMATCH"} for c in latest)
    location_counts = {}
    for complaint in complaints:
        key = (round(complaint.latitude, 5), round(complaint.longitude, 5), complaint.issue_type)
        location_counts[key] = location_counts.get(key, 0) + 1
    recurring = sum(1 for count in location_counts.values() if count > 1)
    by_id = {complaint.id: complaint for complaint in complaints}
    recent = [{
        "complaint_number": by_id[comparison.complaint_id].complaint_number,
        "issue_type": by_id[comparison.complaint_id].issue_type,
        "score": comparison.overall_evidence_score or 0,
        "result": comparison.result or "PENDING",
    } for comparison in latest[:8] if comparison.complaint_id in by_id]
    return {"total": len(complaints), "verified": resolved, "needs_review": needs_review, "not_resolved": not_resolved, "partial": partial, "recurring": recurring, "recent": recent}

@router.get("/{id}/portal")
async def portal_complaint_detail(id: int, db: AsyncSession = Depends(get_db), user: User = Depends(current_user)):
    complaint = await complaint_service.get_complaint(db, id)
    if not complaint:
        raise HTTPException(404, "Complaint not found")
    if user.role == "PUBLIC" and complaint.created_by != user.id:
        raise HTTPException(403, "You can view only your own complaints")
    if user.role == "WORKER" and complaint.assigned_worker_id != user.id:
        raise HTTPException(403, "This complaint is not allocated to you")
    evidence = await evidence_service.get_evidence_by_complaint(db, id)
    comparison_result = await db.execute(
        select(Comparison).where(Comparison.complaint_id == id).order_by(Comparison.created_at.desc())
    )
    comparison = comparison_result.scalars().first()
    # Do not put the persisted image bytes into the JSON detail response.
    # The browser requests each image through the dedicated evidence-file URL.
    evidence_payload = [{
        "id": item.id,
        "complaint_id": item.complaint_id,
        "type": item.type,
        "file_path": item.file_path,
        "mime_type": item.mime_type,
        "timestamp": item.timestamp,
        "latitude": item.latitude,
        "longitude": item.longitude,
        "device_id": item.device_id,
        "quality_score": item.quality_score,
        "created_at": item.created_at,
    } for item in evidence]
    return {"complaint": complaint, "evidence": evidence_payload, "comparison": comparison}

@router.get("/", response_model=List[ComplaintResponse])
async def list_complaints(db: AsyncSession = Depends(get_db)):
    return await complaint_service.list_complaints(db)

@router.get("/{id}", response_model=ComplaintResponse)
async def get_complaint(id: int, db: AsyncSession = Depends(get_db)):
    complaint = await complaint_service.get_complaint(db, id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint

@router.post("/{id}/evidence", response_model=EvidenceResponse)
async def upload_evidence(
    id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    evidence_metadata: str = Form(...), # JSON string of EvidenceCreate
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(optional_user)
):
    complaint = await complaint_service.get_complaint(db, id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    try:
        metadata_dict = json.loads(evidence_metadata)
        evidence_data = EvidenceCreate(**metadata_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid metadata: {str(e)}")

    if user and user.role == "PUBLIC":
        if complaint.created_by != user.id or evidence_data.type != "BEFORE":
            raise HTTPException(403, "Public users may upload only the Before photo for their own complaint")
    if user and user.role == "WORKER":
        if complaint.assigned_worker_id != user.id or evidence_data.type != "AFTER":
            raise HTTPException(403, "Workers may upload an After photo only for complaints allocated to them")
        complaint.status = "IN_PROGRESS"
        if not complaint.worker_acknowledged_at:
            complaint.worker_acknowledged_at = datetime.now(timezone.utc)
        await db.commit()

    file_extension = file.filename.split(".")[-1].lower()
    filename = f"{id}_{evidence_data.type}_{datetime.now().timestamp()}.{file_extension}"
    file_content = await file.read()
    if len(file_content) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Images must be 25 MB or smaller")
    file_path = storage_service.save_file(
        file_content,
        filename,
        subfolder=f"complaints/{id}"
    )

    is_video = file_extension in video_service.SUPPORTED_EXTENSIONS
    quality_score = 0.0

    if not is_video:
        quality_result = quality_engine.analyze(file_path)
        quality_score = quality_result.quality_score

    evidence = await evidence_service.add_evidence_with_quality(
        db, id, evidence_data, file_path, quality_score, file_content, file.content_type
    )

    if not is_video:
        analysis = issue_detector.analyze_issue(file_path, complaint.issue_type, evidence.id)
        await evidence_service.add_detections(db, evidence.id, analysis["detections"])
    else:
        background_tasks.add_task(process_video_background, id, evidence.id, file_path)

    if user and user.role == "WORKER" and evidence_data.type == "AFTER" and not is_video:
        # Run in the request so the worker sees a real success or failure rather
        # than a silent background-task error. The comparison is persisted before
        # the UI reloads its complaint detail.
        from app.services.verification_service import verification_service
        await verification_service.run_verification(db, id)

    return evidence

@router.get("/{id}/evidence", response_model=List[EvidenceResponse])
async def get_evidence(id: int, db: AsyncSession = Depends(get_db)):
    return await evidence_service.get_evidence_by_complaint(db, id)

@router.get("/evidence/{evidence_id}/file")
async def get_evidence_file(evidence_id: str, path: str | None = None, db: AsyncSession = Depends(get_db)):
    if evidence_id == "by-path":
        evidence = (await db.execute(select(Evidence).where(Evidence.file_path == (path or "")))).scalars().first()
    elif evidence_id.isdigit():
        evidence = await db.get(Evidence, int(evidence_id))
    else:
        evidence = None
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    if evidence.file_data:
        return Response(content=evidence.file_data, media_type=evidence.mime_type or "application/octet-stream")
    # Files uploaded before durable storage was enabled may still be available
    # until Render next clears its temporary filesystem.
    from pathlib import Path
    legacy = Path(storage_service.get_path(evidence.file_path))
    if legacy.is_file():
        return Response(content=legacy.read_bytes(), media_type=evidence.mime_type or "application/octet-stream")
    raise HTTPException(status_code=404, detail="This older upload was removed during a deployment. Please upload it again.")

@router.delete("/{id}/evidence/{evidence_id}")
async def delete_evidence(id: int, evidence_id: int, db: AsyncSession = Depends(get_db)):
    success = await evidence_service.delete_evidence(db, evidence_id)
    if not success:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return {"message": "Evidence deleted successfully"}
