import os
from app import create_app
from config import config

# Get environment configuration
env = os.getenv('FLASK_ENV', 'development')
app = create_app(config[env])

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
    # Use configuration from Config class
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    ) 