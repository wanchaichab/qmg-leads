from fastapi import APIRouter
from core.data_processing import get_current_batch_id
from core.tasks import process_current_batch

router = APIRouter()

@router.post("/run-batch")
async def run_batch():
    batch_id = get_current_batch_id()

    process_current_batch(batch_id)

    return {"message": f"Batch {batch_id} processed successfully."}
