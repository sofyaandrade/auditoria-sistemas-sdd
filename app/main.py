from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response, status

from app.database import get_connection, init_db
from app.schemas import Task, TaskCreate, TaskUpdate


def row_to_task(row) -> Task:
    return Task(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        completed=bool(row["completed"]),
        created_at=row["created_at"],
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Task API - Projeto DevOps SDD",
    version="1.0.0",
    description="API CRUD de tarefas para demonstrar SDD, CI/CD, AWS e segurança.",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks", response_model=list[Task])
def list_tasks():
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM tasks ORDER BY id").fetchall()
    return [row_to_task(row) for row in rows]


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title, description) VALUES (?, ?)",
            (payload.title, payload.description),
        )
        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    return row_to_task(row)


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return row_to_task(row)


@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate):
    changes = payload.model_dump(exclude_unset=True)
    with get_connection() as connection:
        existing = connection.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        values = {
            "title": changes.get("title", existing["title"]),
            "description": changes.get("description", existing["description"]),
            "completed": int(changes.get("completed", bool(existing["completed"]))),
        }
        connection.execute(
            "UPDATE tasks SET title = ?, description = ?, completed = ? WHERE id = ?",
            (values["title"], values["description"], values["completed"], task_id),
        )
        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
    return row_to_task(row)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
