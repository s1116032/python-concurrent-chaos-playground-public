# tests/test_concurrent.py
import asyncio
import httpx
import time

async def send_request(req_id: int):
    async with httpx.AsyncClient() as client:
        try:
            # 帶上 req_id 讓網關的日誌可以清晰分辨是誰在說話
            response = await client.get(f"http://127.0.0.1:8000/api/v1/cloud-data?req_id={req_id}", timeout=15.0)
            data = response.json()
            print(f"🚀 [Task {req_id}] 回應狀態: {data.get('status')} | 訊息: {data.get('message', '成功取得雲端數據')}")
        except Exception as e:
            print(f"❌ [Task {req_id}] 連線至網關失敗: {e}")

async def main():
    print(f"🔥 [{time.strftime('%X')}] 開始對網關發動並行混沌攻擊（同時轟炸 4 筆請求）...")
    # 同時發射 4 筆請求
    await asyncio.gather(*[send_request(i) for i in range(1, 5)])

if __name__ == "__main__":
    asyncio.run(main())