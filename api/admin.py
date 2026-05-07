from fastapi import APIRouter
from core.tasks import process_current_batch

router = APIRouter()

@router.post("/run-batch")
async def run_batch():

    result = process_current_batch()

    return {"message": result}
