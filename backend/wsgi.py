import os
from app import create_app
from config import Config

# Get environment configuration
env = os.getenv('FLASK_ENV', 'development')

# Create application instance
app = create_app(Config)

# Configure logging
if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    
    # Ensure logs directory exists
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Configure file handler
    file_handler = RotatingFileHandler(
        'logs/studyhub.log',
        maxBytes=10240,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('StudyHub startup')

if __name__ == '__main__':
    # Development server configuration
    app.run(host='0.0.0.0', port=5100, debug=True) 