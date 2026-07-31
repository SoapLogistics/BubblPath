from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "Bezalel Foundry Gateway"}

@router.get("/projects")
async def get_mock_projects():
    return {
        "projects": [
            {"id": "proj-1", "name": "Sample Android App", "status": "active"},
            {"id": "proj-2", "name": "Backend Services", "status": "planning"}
        ]
    }
