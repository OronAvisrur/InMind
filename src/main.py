from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI(
    title="InMind",
    version="0.1.0",
    description="AI-powered product recommendation system"
)

@app.get("/", response_class=PlainTextResponse)
async def root() -> str:
    return "InMind"

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "InMind"}