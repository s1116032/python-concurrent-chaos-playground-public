# main.py
from fastapi import FastAPI
from aiobreaker import CircuitBreakerError
from gateway.breaker import db_breaker
from gateway.retry import retry_pipeline_with_jitter

app = FastAPI()

@app.get("/api/v1/cloud-data")
async def get_cloud_data(req_id: int = 0):
    try:
        # 斷路器包裹住「整套重試機制」，因此重試 3 次失敗，在外層只算 1 次記點
        data = await db_breaker.callasync(retry_pipeline_with_jitter, client_req_id=req_id)
        return {"status": "success", "data": data}
        
    except CircuitBreakerError:
        # 包含兩種情況：
        # 1. 請求進來時斷路器已經 OPEN
        # 2. 重試退避睡醒後，發現斷路器被其他協程搞到 OPEN，主動終止拋出
        return {
            "status": "degraded",
            "req_id": req_id,
            "message": "🌟 [Fallback] 斷路器處於開啟狀態（或退避中途遭同伴連累熔斷），直接回傳本地降級快取資料。"
        }
    except Exception:
        # 防禦性例外處理（理論上重試耗盡的例外會被 aiobreaker 攔截並轉化為計點，不會跑到這裡）
        return {"status": "error", "req_id": req_id, "message": "服務暫時不可用（預期外錯誤）"}

if __name__ == "__main__":
    import uvicorn
    print("🚪 [Gateway] API 網關啟動於 http://127.0.0.1:8000")
    uvicorn.run("main:app", port=8000, reload=False)