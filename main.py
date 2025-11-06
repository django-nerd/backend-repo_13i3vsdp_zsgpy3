import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Task, TaskUpdate

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COLLECTION = "task"

# Helpers

def to_public(doc):
    if not doc:
        return doc
    doc["id"] = str(doc.pop("_id"))
    return doc

@app.get("/")
def read_root():
    return {"message": "FastAPI backend running"}

@app.get("/test")
def test_database():
    status = {
        "backend": "✅ Running",
        "database": "❌ Not Available"
    }
    try:
        if db is not None:
            status["database"] = "✅ Connected"
            status["collections"] = db.list_collection_names()
        else:
            status["database"] = "❌ Not Configured"
    except Exception as e:
        status["database"] = f"⚠️ {str(e)[:120]}"
    return status

# Tasks API

@app.get("/api/tasks", response_model=List[dict])
def list_tasks(status: Optional[str] = None):
    filt = {}
    if status:
        filt["status"] = status
    docs = get_documents(COLLECTION, filt)
    return [to_public(d) for d in docs]

@app.post("/api/tasks", response_model=dict)
def create_task(task: Task):
    inserted_id = create_document(COLLECTION, task)
    doc = db[COLLECTION].find_one({"_id": ObjectId(inserted_id)})
    return to_public(doc)

@app.put("/api/tasks/{task_id}", response_model=dict)
def update_task(task_id: str, payload: TaskUpdate):
    try:
        oid = ObjectId(task_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid task id")

    update_data = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_data["updated_at"] = __import__("datetime").datetime.utcnow()

    res = db[COLLECTION].update_one({"_id": oid}, {"$set": update_data})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")

    doc = db[COLLECTION].find_one({"_id": oid})
    return to_public(doc)

@app.delete("/api/tasks/{task_id}", response_model=dict)
def delete_task(task_id: str):
    try:
        oid = ObjectId(task_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid task id")

    doc = db[COLLECTION].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Task not found")

    db[COLLECTION].delete_one({"_id": oid})
    return {"id": str(doc["_id"]), "deleted": True}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
