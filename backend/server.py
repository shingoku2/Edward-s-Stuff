"""
Omnix V2 Backend Server
FastAPI sidecar exposing all V1 modules via REST + WebSocket.
Runs on localhost:7432. Started by Tauri on app launch.
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.config import Config
from src.credential_store import CredentialStore
from src.ai_assistant import AIAssistant
from src.game_detector import GameDetector
from src.knowledge_store import KnowledgePackStore
from src.macro_manager import MacroManager
from src.macro_runner import MacroRunner
from src.session_logger import SessionLogger
from src.session_coaching import SessionCoach

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

_config: Optional[Config] = None
_assistant: Optional[AIAssistant] = None
_detector: Optional[GameDetector] = None
_macro_manager: Optional[MacroManager] = None
_session_coaching: Optional[SessionCoach] = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config()
    return _config


def get_assistant() -> AIAssistant:
    global _assistant
    if _assistant is None:
        _assistant = AIAssistant(config=get_config())
    return _assistant


def get_detector() -> GameDetector:
    global _detector
    if _detector is None:
        _detector = GameDetector()
    return _detector


def get_macro_manager() -> MacroManager:
    global _macro_manager
    if _macro_manager is None:
        _macro_manager = MacroManager()
    return _macro_manager


def get_session_coaching() -> SessionCoach:
    global _session_coaching
    if _session_coaching is None:
        _session_coaching = SessionCoach(config=get_config())
    return _session_coaching


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info("Omnix V2 backend starting...")
    get_config()
    get_detector()
    task = asyncio.create_task(_game_detection_loop())
    logger.info("Omnix V2 backend ready on port 7432")
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="Omnix V2 API", version="2.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["tauri://localhost", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    game_context: Optional[Dict[str, Any]] = None


class KnowledgeIngestRequest(BaseModel):
    source: str
    game_profile_id: str
    pack_name: Optional[str] = None


class LicenseRequest(BaseModel):
    license_key: str


class OllamaConfigRequest(BaseModel):
    host: str
    model: str


class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, data: dict):
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                pass


manager = ConnectionManager()


async def _game_detection_loop():
    detector = get_detector()
    last_name: Optional[str] = None
    while True:
        try:
            game = detector.detect_running_game()
            game_name = game.get("name") if game else None
            if game_name != last_name:
                last_name = game_name
                payload = (
                    {"name": game.get("name"), "id": game.get("process_name", "")}
                    if game
                    else {"name": None, "id": None}
                )
                await manager.broadcast({"type": "game_changed", "data": payload})
        except Exception as e:
            logger.error(f"Game detection loop error: {e}")
        await asyncio.sleep(5)


def _game_to_payload(game: Optional[dict]) -> dict:
    if not game:
        return {"name": None, "id": None}
    return {"name": game.get("name"), "id": game.get("process_name", "")}


def _context_str(game_context: Optional[Dict[str, Any]]) -> Optional[str]:
    if not game_context:
        return None
    parts = [f"{k}: {v}" for k, v in game_context.items() if v is not None]
    return ", ".join(parts) if parts else None


@app.get("/api/v2/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


@app.post("/api/v2/chat")
async def chat(req: ChatRequest):
    try:
        response = await asyncio.to_thread(
            get_assistant().ask_question,
            req.message,
            game_context=_context_str(req.game_context),
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            payload = await ws.receive_json()
            if payload.get("type") == "chat":
                await _handle_chat_ws(
                    ws, payload.get("message", ""), payload.get("game_context", {})
                )
            elif payload.get("type") == "ping":
                await ws.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(ws)


async def _handle_chat_ws(ws: WebSocket, message: str, game_context: dict):
    try:
        assistant = get_assistant()
        ctx_str = _context_str(game_context)
        if hasattr(assistant, "stream"):
            async for token in assistant.stream(message, game_context=ctx_str):
                await ws.send_json({"type": "token", "data": token})
        else:
            response = await asyncio.to_thread(
                assistant.ask_question, message, game_context=ctx_str
            )
            for word in response.split(" "):
                await ws.send_json({"type": "token", "data": word + " "})
                await asyncio.sleep(0.02)
        await ws.send_json({"type": "done"})
    except Exception as e:
        await ws.send_json({"type": "error", "data": str(e)})


@app.get("/api/v2/game/current")
def current_game():
    try:
        game = get_detector().detect_running_game()
        return _game_to_payload(game)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/game/profiles")
def game_profiles():
    try:
        from src.game_profile import GameProfileStore
        store = GameProfileStore()
        return {"profiles": [p.to_dict() for p in store.list_profiles()]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/knowledge/packs")
def list_knowledge_packs():
    try:
        packs = KnowledgePackStore().load_all_packs()
        return {"packs": [p.to_dict() for p in packs.values()]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/knowledge/ingest")
async def ingest_knowledge(req: KnowledgeIngestRequest):
    try:
        from src.knowledge_ingestion import IngestionPipeline
        pipeline = IngestionPipeline()
        src = req.source.strip()
        if src.startswith("http://") or src.startswith("https://"):
            result = await asyncio.to_thread(pipeline.ingest, "url", url=src)
        else:
            result = await asyncio.to_thread(pipeline.ingest, "file", file_path=src)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v2/knowledge/packs/{pack_id}")
def delete_knowledge_pack(pack_id: str):
    try:
        KnowledgePackStore().delete_pack(pack_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/macros")
def list_macros():
    try:
        macros = get_macro_manager().get_all_macros()
        return {"macros": [m.to_dict() for m in macros]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/macros/{macro_id}/execute")
def execute_macro(macro_id: str):
    try:
        mgr = get_macro_manager()
        macros = mgr.get_all_macros()
        macro = next((m for m in macros if m.id == macro_id), None)
        if macro is None:
            raise HTTPException(status_code=404, detail=f"Macro '{macro_id}' not found")
        MacroRunner(macro_manager=mgr).execute_macro(macro)
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v2/macros/{macro_id}")
def delete_macro(macro_id: str):
    try:
        get_macro_manager().delete_macro(macro_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/session/summary")
def session_summary():
    try:
        game = get_detector().detect_running_game()
        game_id = game.get("process_name", "default") if game else "default"
        return SessionLogger().get_session_summary(game_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/session/recap")
async def generate_recap():
    try:
        game = get_detector().detect_running_game()
        game_id = game.get("process_name", "default") if game else "default"
        recap = await asyncio.to_thread(
            get_session_coaching().generate_session_recap,
            game_id,
            game_name=game.get("name") if game else None,
        )
        return {"recap": recap}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/config")
def get_app_config():
    cfg = get_config()
    return {
        "ollama_host":     cfg.ollama_host,
        "ollama_model":    cfg.ollama_model,
        "overlay_opacity": getattr(cfg, "overlay_opacity", 0.92),
        "overlay_hotkey":  getattr(cfg, "overlay_hotkey", "ctrl+shift+g"),
        "check_interval":  getattr(cfg, "check_interval", 5),
    }


@app.post("/api/v2/config/ollama")
def update_ollama_config(req: OllamaConfigRequest):
    try:
        cfg = get_config()
        cfg.ollama_host = req.host
        cfg.ollama_model = req.model
        cfg.save()
        global _assistant
        _assistant = None
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/ollama/models")
def list_ollama_models():
    try:
        import ollama
        cfg = get_config()
        resp = ollama.Client(host=cfg.ollama_host).list()
        return {
            "models": [m.get("name", "") for m in resp.get("models", []) if m.get("name")]
        }
    except Exception as e:
        return {"models": [], "error": str(e)}


@app.get("/api/v2/stats/system")
def system_stats():
    try:
        import psutil
        return {
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "ram_total_gb": round(psutil.virtual_memory().total / 1e9, 1),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/license/validate")
def validate_license(req: LicenseRequest):
    try:
        from src.licensing import get_validator
        validator = get_validator(
            supabase_url=os.getenv("SUPABASE_URL", ""),
            anon_key=os.getenv("SUPABASE_ANON_KEY", ""),
        )
        valid, msg = validator.validate(req.license_key)
        if valid:
            CredentialStore().set_credential("omnix_license_key", req.license_key)
        return {"valid": valid, "message": msg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/license/status")
def license_status():
    try:
        if os.getenv("OMNIX_DEV_MODE", "").lower() in ("1", "true", "yes"):
            return {"valid": True, "message": "Dev mode", "dev_mode": True}
        key = CredentialStore().get_credential("omnix_license_key") or ""
        if not key:
            return {"valid": False, "message": "No license key found"}
        from src.licensing import get_validator
        validator = get_validator(
            supabase_url=os.getenv("SUPABASE_URL", ""),
            anon_key=os.getenv("SUPABASE_ANON_KEY", ""),
        )
        valid, msg = validator.validate(key)
        return {"valid": valid, "message": msg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("OMNIX_PORT", "7432"))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
