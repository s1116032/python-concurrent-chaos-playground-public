# gateway/cloud_client.py
import httpx

SIMULATOR_URL = "http://127.0.0.1:8001/data"

async def fetch_from_cloud_raw():
    """
    底層最純粹的網路呼叫，設定嚴格的 1.0 秒超時。
    若 simulator 關閉，將會拋出 httpx.ConnectError。
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(SIMULATOR_URL, timeout=0.1)
        response.raise_for_status()  # 確保 4xx/5xx 也會拋出例外
        return response.json()