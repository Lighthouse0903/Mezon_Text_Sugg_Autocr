from fastapi import FastAPI, Query, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, PlainTextResponse
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import functools, os

from sqlalchemy import false, null
from sympy import true

API_KEY = os.getenv("API_KEY", "")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app = FastAPI(title="Text Suggestion API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_embed_headers(request, call_next):
    resp = await call_next(request)
    resp.headers["Content-Security-Policy"] = (
        "frame-ancestors 'self' https://*.mezon.ai;"
    )
    for h in ("x-frame-options", "X-Frame-Options"):
        if h in resp.headers:
            del resp.headers[h]
    return resp


def require_api_key(x_api_key: Optional[str] = Header(None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


from src.autosuggest.lm.ngram import NGramLM
from src.autocorrect.core.realtime import autocorrect_token_live, autocorrect_line_live

LM = NGramLM.load("models/ngram.pkl")


class SuggestResp(BaseModel):
    candidates: List[str]


class AutocorrectResp(BaseModel):
    input: str
    corrected: str


@functools.lru_cache(maxsize=8192)
def infer(ctx: str, prefix: Optional[str], k: int) -> tuple[str, ...]:
    return tuple(LM.suggest(ctx[-1024:], prefix, k))


@app.get("/health")
def health():
    return {"ok": True}


@app.get(
    "/v1/suggest", response_model=SuggestResp, dependencies=[Depends(require_api_key)]
)
def suggest(
    context: str = Query(""),
    prefix: Optional[str] = None,
    k: int = Query(5, ge=1, le=20),
):
    return SuggestResp(candidates=list(infer(context, prefix, k)))


@app.get(
    "/v1/autocorrect",
    response_model=AutocorrectResp,
    dependencies=[Depends(require_api_key)],
)
def autocorrect_endpoint(token: str = Query("")):
    corrected = autocorrect_token_live(token)
    return AutocorrectResp(input=token, corrected=corrected)


HERE = Path(__file__).resolve()
PROJECT_ROOT = HERE.parents[2]

print(f"[PATH] HERE         = {HERE}")
print(f"[PATH] PROJECT_ROOT = {PROJECT_ROOT}")

UI_CANDIDATES = [
    PROJECT_ROOT / "ui",
    PROJECT_ROOT / "mezon_bot" / "ui",
]

ui_dir = None
for p in UI_CANDIDATES:
    print(f"[UI] probe: {p} | exists={p.exists()}")
    if p.exists() and (p / "typeahead.html").exists():
        ui_dir = p
        break

if ui_dir:
    print(f"[UI] MOUNT /ui -> {ui_dir}")
    app.mount("/ui", StaticFiles(directory=str(ui_dir), html=True), name="ui")
else:
    print("[UI] WARNING: không tìm thấy typeahead.html trong các vị trí dự kiến.")


@app.get("/", include_in_schema=False)
def root():
    if ui_dir:
        return RedirectResponse("/ui/typeahead.html", status_code=302)
    return PlainTextResponse(
        "UI folder not found. Visit /docs for API.", status_code=200
    )


@app.get("/__ui_debug")
def ui_debug():
    data = {
        "HERE": str(HERE),
        "PROJECT_ROOT": str(PROJECT_ROOT),
        "ui_dir": (str(ui_dir) if ui_dir else None),
        "exists": (ui_dir.exists() if ui_dir else False),
        "files": (sorted([f.name for f in ui_dir.iterdir()]) if ui_dir else []),
    }
    return data


@app.get("/v1/echo")
def echo(text: str = ""):
    return {"text": text}

