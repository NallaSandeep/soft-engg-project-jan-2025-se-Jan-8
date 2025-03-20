"""Test configuration and fixtures for StudyAI tests."""

import os
import sys
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid
from datetime import datetime, timezone, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.database import get_db, Base
from src.models.db_models import ChatSession, Message, ReportedResponse
from app import app


# Create an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    isolation_level="SERIALIZABLE",  # Add isolation level for better concurrency handling
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_mock_sessions(db):
    """Create mock chat sessions in the database."""
    sessions = [
        ChatSession(name="Sample Study Session", status="active", is_bookmarked=True),
        ChatSession(
            name="Machine Learning Discussion", status="active", is_bookmarked=False
        ),
        ChatSession(name="Archived Session", status="active", is_bookmarked=False),
    ]

    for session in sessions:
        db.add(session)
    db.flush()  # Flush changes to get generated IDs

    print(f"Created {len(sessions)} mock sessions")
    # Verify sessions were created
    created_sessions = db.query(ChatSession).all()
    print(f"Verified {len(created_sessions)} sessions in database")
    return created_sessions


def create_mock_messages(db, sessions):
    """Create mock messages for the chat sessions."""
    messages = []

    # Create at least one message that we know can be reported
    for session in sessions:
        # Add user message
        user_msg = Message(
            message="Test user message", sender="user", session_id=session.session_id
        )
        messages.append(user_msg)
        db.add(user_msg)

        # Add bot message that can be reported
        bot_msg = Message(
            message="Test bot response", sender="bot", session_id=session.session_id
        )
        messages.append(bot_msg)
        db.add(bot_msg)

    db.flush()  # Flush changes to get generated IDs

    print(f"Created {len(messages)} mock messages")
    # Verify messages were created
    created_messages = db.query(Message).all()
    print(f"Verified {len(created_messages)} messages in database")
    return created_messages

def create_mock_reports(db, messages):
    """Create mock reports for some bot messages."""
    reports = []

    # Only report bot messages
    bot_messages = [msg for msg in messages if msg.sender == "bot"]

    # Report a couple of messages
    if len(bot_messages) >= 2:

        report2 = ReportedResponse(
            message_id=bot_messages[1].message_id,
            session_id=bot_messages[1].session_id,
            reason="inappropriate_content",
            status="reviewed",
        )

        db.add(report2)
        reports.extend([report2])

    db.commit()
    return reports

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test with mock data."""
    # Create the tables
    Base.metadata.create_all(bind=engine)
    print("\n🔧 Setting up test database...")

    # Create a new session
    db = TestingSessionLocal()

    try:
        # Create mock data
        mock_sessions = create_mock_sessions(db)
        assert len(mock_sessions) > 0, "No mock sessions created"

        mock_messages = create_mock_messages(db, mock_sessions)
        assert len(mock_messages) > 0, "No mock messages created"

        # Verify bot messages exist
        bot_messages = [msg for msg in mock_messages if msg.sender == "bot"]
        assert len(bot_messages) > 0, "No bot messages created"

        # Verify database state
        session_count = db.query(ChatSession).count()
        message_count = db.query(Message).count()
        bot_message_count = db.query(Message).filter(Message.sender == "bot").count()

        print("\n📊 Test Database State:")
        print(f"✓ Sessions: {session_count}")
        print(f"✓ Total Messages: {message_count}")
        print(f"✓ Bot Messages: {bot_message_count}")

        # Verify relationships
        for message in mock_messages:
            session = (
                db.query(ChatSession)
                .filter(ChatSession.session_id == message.session_id)
                .first()
            )
            assert session is not None, f"Orphaned message: {message.message_id}"

        db.commit()  # Commit all changes
        yield db

    except Exception as e:
        print(f"\n❌ Error setting up test database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
        print("\n🧹 Cleaned up test database")


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with proper database dependency."""

    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def test_session(client, test_db):
    """Create a test chat session with database access."""
    response = client.post("/chat/session")
    session_data = response.json()

    # Verify session was created in database
    db_session = (
        test_db.query(ChatSession)
        .filter(ChatSession.session_id == session_data["session_id"])
        .first()
    )
    assert db_session is not None, "Session was not created in database"

    yield session_data


@pytest.fixture(scope="function")
def mock_data(test_db):
    """Create and verify mock data with database access."""
    sessions = test_db.query(ChatSession).all()
    messages = test_db.query(Message).all()
    reports = create_mock_reports(test_db, messages)

    # Verify data integrity
    assert len(sessions) > 0, "No sessions found in mock_data"
    assert len(messages) > 0, "No messages found in mock_data"
    bot_messages = [msg for msg in messages if msg.sender == "bot"]
    assert len(bot_messages) > 0, "No bot messages found in mock_data"

    print("\nTest Database State:")
    print(f"- Sessions: {len(sessions)}")
    print(f"- Total Messages: {len(messages)}")
    print(f"- Bot Messages: {len(bot_messages)}")
    print(f"- Reports: {len(reports)}")

    yield {"sessions": sessions, "messages": messages, "reports": reports}
