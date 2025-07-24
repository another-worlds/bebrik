from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.bot import bot

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    await bot.start()
    yield
    # Shutdown
    await bot.stop()

# Initialize FastAPI with lifespan
app = FastAPI(
    title="Telegram Multi-Agent AI Bot", 
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    return {"status": "healthy", "service": "telegram-bot"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Telegram Multi-Agent AI Bot is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
