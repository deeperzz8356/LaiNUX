from fastapi import FastAPI
import uvicorn
app = FastAPI()
@app.get("/")
def read_root(): return {"Hello": "World"}
if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"UVICORN ERROR: {e}")
