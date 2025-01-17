import os
from dotenv import load_dotenv

def load_environment_variables():
    """
    Load environment variables from a .env file and ensure required variables are present.
    """
    load_dotenv()

    # Required environment variables
    required_vars = ['GOOGLE_API_KEY', 'LANGSMITH_API_KEY']

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

    return {
        'google_api_key': os.getenv('GOOGLE_API_KEY'),
        'langsmith_api_key': os.getenv('LANGSMITH_API_KEY'),
        'langsmith_project': os.getenv('LANGSMITH_PROJECT', 'Agentic AI'),
        'langsmith_tracing': os.getenv('LANGSMITH_TRACING', 'true')
    }

def configure_langsmith(config):
    """
    Configure LangSmith settings using environment variables.
    """
    os.environ["LANGSMITH_TRACING"] = config['langsmith_tracing']
    os.environ["LANGSMITH_PROJECT"] = config['langsmith_project']
    os.environ["LANGSMITH_API_KEY"] = config['langsmith_api_key']