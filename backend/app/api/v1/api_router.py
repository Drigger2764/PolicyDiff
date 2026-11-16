from fastapi import APIRouter
from app.api.v1.endpoints import health, workspaces, documents, rules, conflicts, reviews, audit

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(workspaces.router, prefix="/workspaces")
api_router.include_router(documents.router, prefix="/documents")
api_router.include_router(rules.router, prefix="/rules")
api_router.include_router(conflicts.router, prefix="/conflicts")
api_router.include_router(reviews.router, prefix="/reviews")
api_router.include_router(audit.router, prefix="/audit")
