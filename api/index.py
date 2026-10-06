from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
import statistics
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("q-vercel-latency.json", "r") as f:
    data = json.load(f)

class RequestData(BaseModel):
    regions: List[str]
    threshold_ms: float

@app.post("/api/latency")
def latency(request: RequestData):
    result = {}

    for region in request.regions:
        rows = [r for r in data if r["region"] == region]

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime"] for r in rows]

        latencies_sorted = sorted(latencies)
        n = len(latencies_sorted)

        index = max(0, math.ceil(0.95 * n) - 1)
        p95 = latencies_sorted[index]

        result[region] = {
            "avg_latency": statistics.mean(latencies),
            "p95_latency": p95,
            "avg_uptime": statistics.mean(uptimes),
            "breaches": sum(
                1 for x in latencies
                if x > request.threshold_ms
            )
        }

    return result
