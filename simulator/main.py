# simulator/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/data")
async def send_data():
    """
    模擬正常的雲端服務回應。
    在混沌測試時，我們會直接把這個服務關掉 (Ctrl+C) 來觸發 Gateway 的錯誤。
    """
    return {"status": "Databricks Pipeline Active"}

if __name__ == "__main__":
    import uvicorn
    print("🎭 [Simulator] 外部服務模擬器啟動於 http://127.0.0.1:8001")
    uvicorn.run("simulator.main:app", port=8001, reload=False)