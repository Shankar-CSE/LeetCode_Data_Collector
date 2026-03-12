import os
import json

from fastapi import FastAPI, Query, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# --------------- Config ---------------
MONGODB_URI = os.getenv("MONGODB_URI")
REDIS_HOST = os.getenv("HOST")
REDIS_PORT = int(os.getenv("PORT", 6379))
REDIS_USERNAME = os.getenv("USERNAME")
REDIS_PASSWORD = os.getenv("PASSWORD")
DB_NAME = "leetcodedata"
COLLECTION_NAME = "validusers"
CACHE_TTL = 1800  # 30 minutes

ALLOWED_GROUP_BY = {"DEPT", "GENDER", "BATCH"}
ALLOWED_METRICS = {"Problem Count", "Contest Rating", "Contest Attended", "Easy", "medium", "hard"}

# --------------- MongoDB ---------------
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

# --------------- Redis (optional) ---------------
redis_client = None
try:
    import redis
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD,
        decode_responses=True,
    )
    redis_client.ping()
    print("Redis connected")
except Exception:
    redis_client = None
    print("Redis unavailable — running without cache")

# --------------- FastAPI App ---------------
app = FastAPI(title="LeetCode Analytics API")
router = APIRouter(prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------- Helpers ---------------
def cache_get(key: str):
    if redis_client is None:
        return None
    try:
        val = redis_client.get(key)
        return json.loads(val) if val else None
    except Exception:
        return None


def cache_set(key: str, value, ttl: int = CACHE_TTL):
    if redis_client is None:
        return
    try:
        redis_client.setex(key, ttl, json.dumps(value))
    except Exception:
        pass


def build_pipeline(group_by: str, metric: str):
    return [
        {"$group": {"_id": f"${group_by}", "value": {"$avg": f"${metric}"}}},
        {"$project": {"_id": 0, "group": "$_id", "value": {"$round": ["$value", 2]}}},
        {"$sort": {"value": -1}},
    ]


# --------------- Endpoints ---------------
@router.get("/analytics")
def analytics(
    group_by: str = Query(..., description="Field to group by"),
    metric: str = Query(..., description="Metric to aggregate"),
):
    if group_by not in ALLOWED_GROUP_BY:
        raise HTTPException(status_code=400, detail=f"group_by must be one of {ALLOWED_GROUP_BY}")
    if metric not in ALLOWED_METRICS:
        raise HTTPException(status_code=400, detail=f"metric must be one of {ALLOWED_METRICS}")

    cache_key = f"analytics:{group_by}:{metric}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    pipeline = build_pipeline(group_by, metric)
    result = list(collection.aggregate(pipeline))
    cache_set(cache_key, result)
    return result


@router.get("/summary")
def summary():
    cached = cache_get("summary")
    if cached is not None:
        return cached

    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_students": {"$sum": 1},
                "avg_rating": {"$avg": "$Contest Rating"},
                "total_problems": {"$sum": "$Problem Count"},
                "total_contests": {"$sum": "$Contest Attended"},
            }
        },
        {
            "$project": {
                "_id": 0,
                "total_students": 1,
                "avg_rating": {"$round": ["$avg_rating", 2]},
                "total_problems": 1,
                "total_contests": 1,
            }
        },
    ]
    result = list(collection.aggregate(pipeline))
    data = result[0] if result else {"total_students": 0, "avg_rating": 0, "total_problems": 0, "total_contests": 0}
    cache_set("summary", data)
    return data


@router.get("/leaderboard")
def leaderboard():
    cached = cache_get("leaderboard")
    if cached is not None:
        return cached

    cursor = collection.find(
        {},
        {"_id": 0, "Name": 1, "Roll No": 1, "DEPT": 1, "Problem Count": 1, "Contest Rating": 1},
    ).sort("Problem Count", -1).limit(50)

    result = list(cursor)
    cache_set("leaderboard", result)
    return result


@router.get("/scatter")
def scatter():
    cached = cache_get("scatter")
    if cached is not None:
        return cached

    cursor = collection.find(
        {},
        {"_id": 0, "Name": 1, "Problem Count": 1, "Contest Rating": 1},
    )
    result = list(cursor)
    cache_set("scatter", result)
    return result


# --------------- Register Router ---------------
app.include_router(router)
