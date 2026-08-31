import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.src import crud, schemas
from app.src.db import AsyncSessionLocal, init_db
from app.src.logging_config import configure_logging

configure_logging()


def ensure_inflight_state():
    if not hasattr(app.state, "inflight"):
        app.state.inflight = 0
    if not hasattr(app.state, "inflight_event"):
        app.state.inflight_event = asyncio.Event()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize DB and in-flight tracking
    await init_db()
    app.state.inflight = 0
    app.state.inflight_event = asyncio.Event()
    app.state.inflight_event.set()
    yield
    # Shutdown: wait for in-flight requests to finish
    try:
        await app.state.inflight_event.wait()
    except Exception:
        pass


app = FastAPI(title="TaskFlow", lifespan=lifespan)


@app.middleware("http")
async def inflight_middleware(request, call_next):
    ensure_inflight_state()
    app.state.inflight += 1
    if app.state.inflight > 0:
        app.state.inflight_event.clear()
    try:
        response = await call_next(request)
        return response
    finally:
        app.state.inflight -= 1
        if app.state.inflight == 0:
            app.state.inflight_event.set()


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})


@app.post("/tasks", response_model=schemas.TaskRead)
async def create_task(payload: schemas.TaskCreate, db: AsyncSession = Depends(get_db)):
    task = await crud.create_task(db, payload)
    return task


@app.get("/tasks", response_model=list[schemas.TaskRead])
async def list_tasks(db: AsyncSession = Depends(get_db)):
    return await crud.list_tasks(db)


@app.get("/tasks/{task_id}", response_model=schemas.TaskRead)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Not found")
    return task


@app.put("/tasks/{task_id}", response_model=schemas.TaskRead)
async def update_task(task_id: int, payload: schemas.TaskUpdate, db: AsyncSession = Depends(get_db)):
    task = await crud.update_task(db, task_id, payload)
    if not task:
        raise HTTPException(status_code=404, detail="Not found")
    return task


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    ok = await crud.delete_task(db, task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    return JSONResponse({"deleted": True})

