# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Amadeus API Credentials
    AMADEUS_API_KEY = os.getenv('AMADEUS_API_KEY')
    AMADEUS_API_SECRET = os.getenv('AMADEUS_API_SECRET')
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'trip-planner-dev-key')
    
    # File paths
    PDF_OUTPUT_DIR = 'pdfs'
    
    # API endpoints
    AMADEUS_BASE_URL = "https://test.api.amadeus.com"
    
    @staticmethod
    def validate():
        """Validate configuration"""
        if not Config.AMADEUS_API_KEY or not Config.AMADEUS_API_SECRET:
            print("⚠️  Amadeus API credentials not found. Using sample data.")
            return False
        return True
    
    @staticmethod
    def ensure_directories():
        """Create necessary directories"""
        if not os.path.exists(Config.PDF_OUTPUT_DIR):
            os.makedirs(Config.PDF_OUTPUT_DIR)