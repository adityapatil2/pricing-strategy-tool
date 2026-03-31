import os

class Config:
    # Flask settings
    DEBUG = True
    SECRET_KEY = "pricing-strategy-secret-key"
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "data", "uploads")
    ALLOWED_EXTENSIONS = {"csv", "xlsx"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # CORS settings
    CORS_ORIGINS = "http://localhost:5173"  # React app URL