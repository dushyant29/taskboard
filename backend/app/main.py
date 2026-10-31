import json, logging, os
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
import redis

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("taskboard")

engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///./local.db"), pool_pre_ping=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False)
cache = redis.from_url(os.environ["REDIS_URL"], decode_responses=True) if os.getenv("REDIS_URL") else None


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    done: Mapped[bool] = mapped_column(default=False)


class TaskIn(BaseModel):
    title: str


def get_db():
    with SessionLocal() as db:
        yield db


def invalidate():
    try:
        cache and cache.delete("tasks")
    except redis.RedisError:
        log.warning("redis unavailable")


app = FastAPI(title="taskboard")
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ready"}


@app.get("/api/tasks")
def list_tasks(db: Session = Depends(get_db)):
    try:
        if cache and (hit := cache.get("tasks")):
            return json.loads(hit)
    except redis.RedisError:
        log.warning("redis unavailable")
    data = [{"id": t.id, "title": t.title, "done": t.done} for t in db.scalars(select(Task).order_by(Task.id))]
    try:
        cache and cache.setex("tasks", 10, json.dumps(data))
    except redis.RedisError:
        pass
    return data


@app.post("/api/tasks", status_code=201)
def create_task(body: TaskIn, db: Session = Depends(get_db)):
    t = Task(title=body.title)
    db.add(t); db.commit(); invalidate()
    return {"id": t.id, "title": t.title, "done": t.done}


@app.patch("/api/tasks/{task_id}")
def toggle_task(task_id: int, db: Session = Depends(get_db)):
    t = db.get(Task, task_id)
    if not t:
        raise HTTPException(404, "not found")
    t.done = not t.done
    db.commit(); invalidate()
    return {"id": t.id, "title": t.title, "done": t.done}


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    t = db.get(Task, task_id)
    if not t:
        raise HTTPException(404, "not found")
    db.delete(t); db.commit(); invalidate()
