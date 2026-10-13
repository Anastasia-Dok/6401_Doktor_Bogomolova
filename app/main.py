from fastapi import FastAPI

from app.routers import auth, users, lists, notes, subscriptions

app = FastAPI(
    title="Recommendations API",
    version="1.0.0",
    description="ЛР2: FastAPI + JWT + PostgreSQL",
)

# auth — публичный
app.include_router(auth.router, prefix="/api/v1")

# users — /me публичный (по токену), админская часть отдельным роутером
app.include_router(users.router, prefix="/api/v1")
app.include_router(users.admin_router, prefix="/api/v1")

# lists — чтение всем, изменение админу
app.include_router(lists.router, prefix="/api/v1")
app.include_router(lists.admin_router, prefix="/api/v1")

# notes, subscriptions — по токену
app.include_router(notes.router, prefix="/api/v1")
app.include_router(subscriptions.router, prefix="/api/v1")


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}