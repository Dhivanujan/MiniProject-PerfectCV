"""
FastAPI Main Application
Includes CV generation pipeline routes
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from pymongo import MongoClient
from config.config import Config

# Import routers
from app.routes.cv import router as cv_router
from app.routes.auth_fastapi import router as auth_router

# MongoDB connection
mongo_client = None
mongo_db = None

def get_mongo_db():
    """Get MongoDB database instance"""
    global mongo_db
    if mongo_db is None:
        global mongo_client
        mongo_client = MongoClient(Config.MONGO_URI)
        # Extract database name from URI or use default
        db_name = Config.MONGO_URI.split('/')[-1].split('?')[0] or 'perfectcv'
        mongo_db = mongo_client[db_name]
    return mongo_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PerfectCV API",
    description="AI-powered CV extraction, enhancement, and PDF generation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cv_router, prefix="/api/cv", tags=["CV Generation"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PerfectCV API",
        "version": "1.0.0",
        "endpoints": {
            "authentication": {
                "login": "/auth/login",
                "register": "/auth/register",
                "forgot_password": "/auth/forgot-password",
                "verify_code": "/auth/verify-code",
                "reset_password": "/auth/reset-password",
                "logout": "/auth/logout"
            },
            "cv": {
                "generation": "/api/cv/generate-cv",
                "extraction": "/api/cv/extract-cv",
                "improvement": "/api/cv/improve-cv",
                "pdf_from_json": "/api/cv/generate-pdf-from-json",
                "health": "/api/cv/health"
            }
        }
    }

@app.get("/health")
async def health():
    """Health check"""
    db_status = "connected"
    try:
        db = get_mongo_db()
        db.command('ping')
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status
    }

@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    logger.info("Initializing MongoDB connection...")
    try:
        db = get_mongo_db()
        db.command('ping')
        logger.info("✅ MongoDB connected successfully")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global mongo_client
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed")


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(
        "app_fastapi:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
