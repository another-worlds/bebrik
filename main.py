from fastapi import FastAPI
from app.core.bot import bot

# Initialize FastAPI
app = FastAPI(title="Telegram Multi-Agent AI Bot", version="1.0.0")

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    return {"status": "healthy", "service": "telegram-bot"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Telegram Multi-Agent AI Bot is running"}

@app.on_event("startup")
async def startup_event():
    """Start the bot when the application starts"""
    await bot.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the bot when the application shuts down"""
    await bot.stop()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
