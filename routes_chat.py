import os, asyncio
from typing import Dict, List
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, PlainTextResponse
from pydantic import BaseModel
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
router = APIRouter(prefix="", tags=["chat"])


CONV: Dict[str, List[Dict[str, str]]] = {}

class ChatReq(BaseModel):
    session_id: str            
    message: str               
    stream: bool = True        
    model: str = "gpt-4o"      
    max_output_tokens: int = 3000

async def _aiter_text(s: str):
    for ch in s:
        yield ch
        await asyncio.sleep(0)  

def _needs_summarize(history: List[Dict[str,str]]) -> bool:

    return len(history) > 20

def _summarize(history: List[Dict[str,str]]) -> str:
    text = "\n".join(f"{m['role']}: {m['content']}" for m in history)

    rsp = client.responses.create(
        model="gpt-4o-mini",
        input=f"Summarize briefly (<=200 words) preserving key facts and decisions:\n\n{text}"
    )

    parts = []
    for item in rsp.output or []:
        for c in getattr(item, "content", []) or []:
            if getattr(c, "type", "") == "output_text":
                parts.append(c.get("text", ""))  
    return "".join(parts) or "Conversation so far: (summary unavailable)."

def _response_text(resp) -> str:

    buf = []
    for item in resp.output or []:
        for c in getattr(item, "content", []) or []:
            if getattr(c, "type", "") == "output_text":
                buf.append(c.get("text", ""))  # type: ignore
    return "".join(buf).strip()


@router.post("/chat", response_class=PlainTextResponse)
def chat(req: ChatReq):
    sid = req.session_id
    CONV.setdefault(sid, [])


    if _needs_summarize(CONV[sid]):
        summary = _summarize(CONV[sid])
        CONV[sid] = [{"role": "system", "content": f"Summary so far:\n{summary}"}]


    messages = CONV[sid] + [{"role": "user", "content": req.message}]

    try:
        resp = client.responses.create(
            model=req.model,
            input=[{"role": m["role"], "content": m["content"]} for m in messages],
            max_output_tokens=req.max_output_tokens,
        )
        text = _response_text(resp)
        if not text:
            raise HTTPException(500, "Empty response from model")


        CONV[sid].append({"role": "user", "content": req.message})
        CONV[sid].append({"role": "assistant", "content": text})
        return text

    except Exception as e:
        raise HTTPException(500, f"AI error: {e}")


@router.post("/chat_stream")
def chat_stream(req: ChatReq):
    text = chat(req)
    return StreamingResponse(_aiter_text(text), media_type="text/plain")
