from fastapi import FastAPI, Query, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import functools, os

from src.lm.ngram import NGramLM

API_KEY = os.getenv("API_KEY")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app = FastAPI(title="Text Suggestion API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_api_key(x_api_key: Optional[str] = Header(None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


LM = NGramLM.load("models/ngram.pkl")


class SuggestResp(BaseModel):
    candidates: List[str]


@functools.lru_cache(maxsize=8192)
def infer(ctx: str, prefix: Optional[str], k: int):
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
