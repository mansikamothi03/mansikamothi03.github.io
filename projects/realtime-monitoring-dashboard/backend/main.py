"""
Real-Time Monitoring Dashboard — FastAPI Backend
Streams KPI metrics to React frontend via WebSocket.
"""

import asyncio
import json
import random
from datetime import datetime
from typing import List

import redis.asyncio as aioredis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from anomaly_detector import AnomalyDetector

app = FastAPI(title="Real-Time Monitoring Dashboard", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connected WebSocket clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.active_connections.remove(conn)


manager = ConnectionManager()
detector = AnomalyDetector()

# KPI definitions with thresholds
KPI_CONFIG = {
    "revenue_per_hour": {"baseline": 5000, "unit": "$", "alert_threshold": 0.3},
    "active_users":     {"baseline": 1200, "unit": "",  "alert_threshold": 0.2},
    "conversion_rate":  {"baseline": 0.045,"unit": "%", "alert_threshold": 0.25},
    "error_rate":       {"baseline": 0.01, "unit": "%", "alert_threshold": 0.5},
    "avg_response_ms":  {"baseline": 120,  "unit": "ms","alert_threshold": 0.4},
    "orders_per_min":   {"baseline": 85,   "unit": "",  "alert_threshold": 0.3},
}


def generate_metric(kpi_name: str, config: dict) -> dict:
    """Simulate a real-time metric value with occasional anomalies."""
    baseline = config["baseline"]
    noise = random.gauss(0, baseline * 0.05)
    # Inject anomaly 5% of the time
    if random.random() < 0.05:
        noise = baseline * random.choice([-0.4, 0.6])
    value = max(0, baseline + noise)
    return {
        "name": kpi_name,
        "value": round(value, 4),
        "unit": config["unit"],
        "baseline": baseline,
        "timestamp": datetime.utcnow().isoformat(),
    }


async def metrics_broadcaster():
    """Background task: generate and broadcast metrics every second."""
    history = {kpi: [] for kpi in KPI_CONFIG}

    while True:
        payload = {"metrics": [], "alerts": [], "timestamp": datetime.utcnow().isoformat()}

        for kpi_name, config in KPI_CONFIG.items():
            metric = generate_metric(kpi_name, config)
            history[kpi_name].append(metric["value"])
            if len(history[kpi_name]) > 60:
                history[kpi_name].pop(0)

            # Anomaly detection
            is_anomaly, score = detector.detect(history[kpi_name])
            metric["is_anomaly"] = is_anomaly
            metric["anomaly_score"] = round(score, 3)

            if is_anomaly:
                payload["alerts"].append({
                    "kpi": kpi_name,
                    "value": metric["value"],
                    "score": score,
                    "severity": "high" if abs(score) > 3 else "medium",
                    "message": f"{kpi_name} anomaly detected (z-score: {score:.2f})"
                })

            payload["metrics"].append(metric)

        if manager.active_connections:
            await manager.broadcast(payload)

        await asyncio.sleep(1)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(metrics_broadcaster())


@app.websocket("/ws/metrics")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/api/kpis")
async def get_kpi_config():
    """Return KPI configuration."""
    return KPI_CONFIG


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "connections": len(manager.active_connections)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)