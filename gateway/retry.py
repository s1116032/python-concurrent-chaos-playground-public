# gateway/retry.py
import asyncio
import random
import httpx
from datetime import datetime
from aiobreaker import CircuitBreakerError, CircuitBreakerState
from .breaker import db_breaker
from .cloud_client import fetch_from_cloud_raw

async def retry_pipeline_with_jitter(client_req_id: int):
    """
    工業級重試狀態機：
    1. 實作指數退避 + Full Jitter
    2. 隨時監控斷路器狀態，若變為 OPEN 則立即終止重試
    3. 若全面失敗，外拋異常給外層斷路器計點（整套重試完畢只算 1 次失敗）
    """
    max_retries = 3
    base_delay = 0.5  # 基礎秒數
    
    for attempt in range(max_retries):
        # 【主動終止機制 1/2】發送前檢查：是否已有並行兄弟把斷路器點爆了？
        if db_breaker.current_state == CircuitBreakerState.OPEN:
            print(f"🛑 [Req {client_req_id}] 在第 {attempt + 1} 次嘗試前，發現斷路器已 OPEN！立刻終止重試。")
            raise CircuitBreakerError("Circuit is open. Aborting ongoing retries.", db_breaker.opens_at or datetime.utcnow())
            
        try:
            print(f"🔄 [Req {client_req_id}] 正在執行第 {attempt + 1} 次嘗試...")
            return await fetch_from_cloud_raw()
            
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            print(f"⚠️ [Req {client_req_id}] 第 {attempt + 1} 次嘗試失敗 原因: {type(e).__name__}")
            
            # 如果是最後一次嘗試也失敗了，直接外拋給外層的斷路器記點
            if attempt == max_retries - 1:
                print(f"❌ [Req {client_req_id}] 已達最大重試次數，宣告整筆請求失敗。")
                raise e
            
            # --- 計算指數退避 + Full Jitter (AWS 標準演算法) ---
            max_backoff = base_delay * (2 ** attempt)
            sleep_time = random.uniform(0, max_backoff)
            print(f"⏳ [Req {client_req_id}] 進入退避，預計等待 {sleep_time:.2f} 秒...")
            
            # 在非同步的 sleep 期間，控制權會交還給 Event Loop，讓其他請求也有機會失敗並改變斷路器狀態
            await asyncio.sleep(sleep_time)
            
            # 【主動終止機制 2/2】睡醒後檢查：睡覺期間斷路器是不是開了？若是，就不再浪費網路資源
            if db_breaker.current_state == CircuitBreakerState.OPEN:
                print(f"🛑 [Req {client_req_id}] 睡醒後發現斷路器已變更為 OPEN！拒絕第 {attempt + 2} 次嘗試，直接終止。")
                raise CircuitBreakerError("Circuit popped during sleep. Aborting.", db_breaker.opens_at or datetime.utcnow())