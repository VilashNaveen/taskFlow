from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.src import models, schemas


async def create_task(db: AsyncSession, payload: schemas.TaskCreate) -> models.Task:
    task = models.Task(title=payload.title, description=payload.description)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_task(db: AsyncSession, task_id: int) -> Optional[models.Task]:
    res = await db.get(models.Task, task_id)
    return res


async def list_tasks(db: AsyncSession) -> List[models.Task]:
    q = select(models.Task).order_by(models.Task.id)
    result = await db.execute(q)
    return result.scalars().all()


async def update_task(db: AsyncSession, task_id: int, payload: schemas.TaskUpdate) -> Optional[models.Task]:
    task = await db.get(models.Task, task_id)
    if not task:
        return None
    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.completed is not None:
        task.completed = payload.completed
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task_id: int) -> bool:
    task = await db.get(models.Task, task_id)
    if not task:
        return False
    await db.delete(task)
    await db.commit()
    return True

