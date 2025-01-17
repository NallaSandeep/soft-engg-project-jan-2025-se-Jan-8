# soft-engg-project-jan-2025-se-Jan-8
An AI-powered virtual guide to enhance learning for IITM BS students, promoting effective study habits, resource discovery, and academic integrity while fostering collaboration.

# Project Structure
```
project_root/
├── config/
│   ├── __init__.py
│   └── config.py              # Environment and configuration settings
├── data/
│   ├── documents/            # Source documents for RAG
│   ├── vector_store/         # Serialized vector stores
│   └── artifacts/            # Conversation artifacts and history
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── rag_agent.py      # RAG implementation
│   │   ├── course_agent.py   # Course guidance agent
│   │   ├── integrity_agent.py # Academic integrity agent
│   │   └── study_agent.py    # Study planning agent
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helper.py         # Shared utility functions
│   ├── supervisor.py         # Agent orchestration
│   └── main.py              # Application entry point
├── tests/
│   ├── __init__.py
│   └── test_agents/         # Unit tests for agents
├── .env                     # Environment variables
├── .gitignore
├── requirements.txt
└── README.md
```