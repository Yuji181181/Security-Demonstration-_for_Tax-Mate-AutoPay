import uuid
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from src.backend.agents import vulnerable_app, secure_app
from src.backend.mock_bank import bank_system
from src.data.invoices import POISONED_INVOICE_TEXT

import time
from collections import deque
from fastapi import Request

app = FastAPI(title="Tax-Mate AutoPay Backend")

# --- Simple In-Memory Rate Limiter ---
class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.timestamps = deque()

    def is_allowed(self) -> bool:
        now = time.time()
        # Remove timestamps older than the window
        while self.timestamps and now - self.timestamps[0] > self.window_seconds:
            self.timestamps.popleft()
        
        if len(self.timestamps) >= self.max_requests:
            return False
        
        self.timestamps.append(now)
        return True

# Limit to 20 requests per minute per instance
limiter = RateLimiter(max_requests=20, window_seconds=60)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Apply rate limit only to execution endpoints
    if "/run/" in request.url.path:
        if not limiter.is_allowed():
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429, 
                content={"detail": "Too many requests. Please wait a moment."}
            )
    response = await call_next(request)
    return response

class RunRequest(BaseModel):
    invoice_text: Optional[str] = POISONED_INVOICE_TEXT

class ResumeRequest(BaseModel):
    thread_id: str
    action: str  # "approve" or "reject"

@app.post("/reset")
def reset_system():
    bank_system.reset()
    return {"status": "System and Bank reset"}

@app.get("/logs")
def get_logs():
    return {"logs": bank_system.get_logs()}

@app.post("/run/vulnerable")
async def run_vulnerable(req: RunRequest):
    # 脆弱なエージェント: 最後まで一気に実行
    # ステートを持たないため、毎回新しい実行として扱う
    inputs = {"messages": [HumanMessage(content=req.invoice_text)]}
    try:
        # invokeで実行。同期的に完了まで待つ
        result = vulnerable_app.invoke(inputs)
        return {"status": "completed", "final_output": str(result["messages"][-1].content)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run/secure/start")
def start_secure(req: RunRequest):
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    inputs = {"messages": [HumanMessage(content=req.invoice_text)]}
    
    # ツール実行前で停止するはず
    result = secure_app.invoke(inputs, config=config)
    
    # 次の状態を確認
    snapshot = secure_app.get_state(config)
    next_step = snapshot.next
    
    tool_calls = []
    if snapshot.values and "messages" in snapshot.values:
        last_msg = snapshot.values["messages"][-1]
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            tool_calls = last_msg.tool_calls

    return {
        "status": "paused" if next_step else "completed",
        "thread_id": thread_id,
        "next": next_step,
        "tool_calls": tool_calls
    }

@app.post("/run/secure/resume")
def resume_secure(req: ResumeRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    snapshot = secure_app.get_state(config)
    
    if not snapshot.next:
        return {"status": "error", "message": "No pending steps for this thread."}

    if req.action == "reject":
        # 拒否された場合、ツールを実行せず、拒否メッセージをエージェントに返して終了させる（あるいはループさせる）
        # ここではシンプルに「拒否されたのでツール出力をエラーとして返す」ことでエージェントに知らせる
        # または、単に中断して終了扱いにする。
        
        # 今回はToolNodeをスキップするのではなく、
        # "Tool execution rejected by user" というToolMessageを挿入して再開する方法がスマートだが、
        # 実装を簡単にするため、ユーザーからのメッセージとして「拒否」を送り、エージェントを動かす。
        # ただし interrupt_before="tools" なので、次は "tools" ノードに行こうとする。
        # ここで update_state を使って "tools" ノードをスキップあるいはダミー結果を入れる必要がある。
        
        # 最も簡単な実装: ツール呼び出しIDに対応するエラー出力を注入して進める
        last_msg = snapshot.values["messages"][-1]
        tool_calls = last_msg.tool_calls
        
        # ツール呼び出しに対する拒否レスポンスを作成(ToolMessage)
        # Type check to avoid crashes
        if tool_calls:
            from langchain_core.messages import ToolMessage
            tool_messages = [
                ToolMessage(
                    tool_call_id=tc["id"],
                    content="Error: User rejected this operation via Human-in-the-loop validation."
                ) for tc in tool_calls
            ]
            # update_stateでステートを更新（as_node="tools"とすることで、toolsノードが実行されたかのように振る舞う）
            secure_app.update_state(config, {"messages": tool_messages}, as_node="tools")
            
            # 再開 (toolsノードはスキップされ、エージェントに戻る)
            result = secure_app.invoke(None, config=config)
            return {"status": "rejected_and_completed", "final_output": str(result["messages"][-1].content)}
        else:
             return {"status": "error", "message": "No tool calls found to reject."}

    elif req.action == "approve":
        # 承認された場合、そのまま続行 (Noneを渡して再開すると、保留されていたToolNodeが実行される)
        result = secure_app.invoke(None, config=config)
        return {"status": "approved_and_completed", "final_output": str(result["messages"][-1].content)}
    
    return {"status": "invalid_action"}

@app.get("/state/{thread_id}")
def get_state(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = secure_app.get_state(config)
    return {
        "values": str(snapshot.values),
        "next": snapshot.next
    }
