import json
import os

import asyncpg
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings


# --- Configuration via Env Vars (K8s ConfigMaps/Secrets) ---
class Settings(BaseSettings):
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    pg_user: str = os.getenv("PG_USER", "postgres")
    pg_password: str = os.getenv("PG_PASSWORD", "password")
    pg_db: str = os.getenv("PG_DB", "messenger")
    pg_host: str = os.getenv("PG_HOST", "localhost")
    language: str = os.getenv("LANGUAGE", "fr")


settings = Settings()
app = FastAPI()


# --- Modèles ---
class Message(BaseModel):
    content: str
    author: str


# --- Clients DB (Global) ---
redis_client = None
pg_pool = None


@app.on_event("startup")
async def startup_event():
    # Initialisation des connexions au démarrage
    global redis_client, pg_pool
    try:
        redis_client = redis.from_url(
            f"redis://{settings.redis_host}", decode_responses=True
        )
        pg_pool = await asyncpg.create_pool(
            user=settings.pg_user,
            password=settings.pg_password,
            database=settings.pg_db,
            host=settings.pg_host,
        )
        # Création table si inexistante
        async with pg_pool.acquire() as conn:
            await conn.execute("""CREATE TABLE IF NOT EXISTS messages
                                  (id serial PRIMARY KEY, content text, author text, created_at TIMESTAMP DEFAULT NOW())""")
    except Exception as e:
        print(f"Initial connection error (non-fatal for startup): {e}")


# --- Endpoints ---


@app.get("/config")
async def get_config():
    """Retourne la configuration de l'application (accessible au frontend)"""
    return {"language": settings.language}


@app.get("/messages")
async def get_messages():
    """Lit le cache Redis en priorité, fallback sur Postgres si Redis est down"""
    messages = []
    source = "unknown"

    # Tentative Redis (Cache)
    try:
        cached_msgs = await redis_client.lrange("recent_messages", 0, 9)
        if cached_msgs:
            messages = [json.loads(m) for m in cached_msgs]
            source = "redis_cache"
    except Exception as e:
        print(f"Redis error: {e}")
        source = "redis_down_trying_db"

    # Si Redis n'avait rien ou était down, tentative Postgres
    if not messages and pg_pool:
        try:
            async with pg_pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT content, author FROM messages ORDER BY created_at DESC LIMIT 10"
                )
                messages = [
                    {"content": r["content"], "author": r["author"]} for r in rows
                ]
                source = "postgresql_live"
        except Exception as e:
            print(f"Postgres error: {e}")
            source = "all_dbs_down"

    return {"source": source, "data": messages}


@app.post("/messages")
async def post_message(msg: Message):
    """Écrit dans Postgres PUIS met à jour le cache Redis"""
    if not pg_pool:
        raise HTTPException(status_code=503, detail="PostgresUnavailable")

    # 1. Écriture DB (Critique)
    try:
        async with pg_pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO messages(content, author) VALUES($1, $2)",
                msg.content,
                msg.author,
            )
    except Exception as e:
        print(f"Failed to write to DB: {e}")
        raise HTTPException(status_code=500, detail="DatabaseWriteFailed")

    # 2. Mise à jour Cache (Best effort)
    try:
        msg_json = json.dumps(msg.dict())
        await redis_client.lpush("recent_messages", msg_json)
        await redis_client.ltrim(
            "recent_messages", 0, 9
        )  # Garde seulement les 10 derniers
    except Exception as e:
        print(f"Failed to update cache (non-critical): {e}")

    return {"status": "Message posted"}


# --- Probes K8s ---
@app.get("/healthz")
async def liveness():
    # L'app est vivante tant que le serveur web tourne
    return {"status": "alive"}


@app.get("/readyz")
async def readiness():
    # L'app est prête si elle peut parler au moins à une DB
    pg_ok = False
    redis_ok = False
    try:
        async with pg_pool.acquire() as conn:
            await conn.execute("SELECT 1")
        pg_ok = True
    except Exception:
        pass

    try:
        await redis_client.ping()
        redis_ok = True
    except Exception:
        pass

    if pg_ok or redis_ok:
        return {"status": "ready", "pg": pg_ok, "redis": redis_ok}
    raise HTTPException(status_code=503, detail="NotReady")
