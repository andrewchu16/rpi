from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

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

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

if __name__ == '__main__':
    import uvicorn
    print("Starting AI")
    uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
    )


