import os
import socket
from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(title="Backend demo")

# Each container has its own hostname. We show it in every response,
# so you can SEE which backend answered (this proves load balancing works).
HOSTNAME = socket.gethostname()
BACKEND_NAME = os.getenv("BACKEND_NAME", "backend")


@app.get("/api/hello")
def hello():
    return {
        "message": "Pershendetje nga backend-i!",
        "served_by": BACKEND_NAME,
        "container_id": HOSTNAME,
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "served_by": BACKEND_NAME}
