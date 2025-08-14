from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import Config
from routes import auth_router, health_router


app = FastAPI()

"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""

app.include_router(auth_router)
app.include_router(health_router)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

if __name__ == '__main__':
    import uvicorn
    print("Starting AI")
    uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=Config.DEBUG
    )


