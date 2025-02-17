import uvicorn
import signal
import sys
from app import app
from app.core.config import settings

def signal_handler(sig, frame):
    print("\nShutting down StudyIndexer service...")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the application
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1,
        log_level="info"
    ) 