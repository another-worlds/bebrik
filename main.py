from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
from app.core.bot import bot
from app.utils.logging import setup_logging

# Initialize logging system
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting Telegram Multi-Agent AI Bot")
    logger.info("📱 Initializing Telegram bot connection")
    await bot.start()
    logger.info("✅ Bot started successfully")
    yield
    # Shutdown
    logger.info("🛑 Shutting down Telegram Multi-Agent AI Bot")
    await bot.stop()
    logger.info("✅ Bot stopped successfully")

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
