from fastapi import APIRouter

from app.api.v1 import admin, analytics, auth, chat, documents, evaluation, feedback, health, search, users

api_router = APIRouter()

# Core Health & Readiness
api_router.include_router(health.router, tags=["health"])

# Backend Layer APIs per Architecture Plan
api_router.include_router(auth.router)        # Authentication & Authorization (JWT / OAuth)
api_router.include_router(users.router)       # User & Permission Management (Multi-user, RBAC)
api_router.include_router(documents.router)   # Document Processing APIs (PDF, Word, Excel, PPT)
api_router.include_router(search.router)      # RAG / Query APIs (Semantic & Hybrid Retrieval)
api_router.include_router(chat.router)        # Chat History & Conversation Tracking
api_router.include_router(feedback.router)    # Feedback APIs (Thumbs up / down)
api_router.include_router(admin.router)       # Admin APIs
api_router.include_router(analytics.router)   # Dashboard & Analytics APIs
api_router.include_router(evaluation.router)  # Continuous Learning & Evaluation APIs
