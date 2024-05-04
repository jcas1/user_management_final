import pytest
import uuid
from fastapi import status
from datetime import datetime, timedelta
from app.services.user_service import UserService
from app.models.user_model import User, UserRole
from app.utils.security import hash_password

@pytest.fixture
async def test_users(db_session):
    # Create test users
    user1 = User(
        id=uuid.uuid4(),
        nickname="crazy_koala_22",
        email="john.doe@example.com",
        role=UserRole.ADMIN,
        hashed_password=hash_password("SecurePassword123!"),
        is_locked=False,
        email_verified=True,
        created_at=datetime.utcnow() - timedelta(days=40),
    )

    user2 = User(
        id=uuid.uuid4(),
        nickname="fat_pelican_12",
        email="prince_devitt@example.com",
        role=UserRole.AUTHENTICATED,
        hashed_password=hash_password("AnotherSecurePassword123!"),
        is_locked=True,
        email_verified=False,
        created_at=datetime.utcnow() - timedelta(days=20),
    )

    # Add users to the session
    db_session.add_all([user1, user2])
    await db_session.commit()

    return [user1, user2]

@pytest.mark.asynco
async def test_search_users_by_username(db_session, test_users):
    users = await UserService.search_users(db_session, username="koala")
    assert len(users) > 0  # Check that users are returned based on username

@pytest.mark.asyncio
async def test_search_users_by_email(db_session, test_users):
    users = await UserService.search_users(db_session, email="example.com")
    assert len(users) > 0  # Check that users are returned based on email

@pytest.mark.asyncio
async def test_search_users_by_role(db_session, test_users):
    users = await UserService.search_users(db_session, role=UserRole.ADMIN)
    assert len(users) > 0  # Check that users are returned based on role

@pytest.mark.asyncio
async def test_search_users_by_account_status(db_session):
    # Test filtering by account status
    users_locked = await UserService.search_users(db_session, is_locked=True)
    assert all(user.is_locked for user in users_locked)

    users_unlocked = await UserService.search_users(db_session, is_locked=False)
    assert all(not user.is_locked for user in users_unlocked)

@pytest.mark.asyncio
async def test_search_users_by_registration_date(db_session):
    # Test filtering by registration date range
    date_from = datetime.utcnow() - timedelta(days=30)  # Last 30 days
    users = await UserService.search_users(db_session, date_from=date_from)
    assert all(user.created_at >= date_from for user in users)

    date_to = datetime.utcnow() - timedelta(days=10)  # Last 10 days
    users = await UserService.search_users(db_session, date_to=date_to)
    assert all(user.created_at <= date_to for user in users)

@pytest.mark.asyncio
async def test_search_users_by_locked_status(db_session):
    users_locked = await UserService.search_users(db_session, is_locked=True)
    assert all(user.is_locked for user in users_locked)

    users_unlocked = await UserService.search_users(db_session, is_locked=False)
    assert all(not user.is_locked for user in users_unlocked)

@pytest.mark.asyncio
async def test_search_users_by_email_verification_status(db_session):
    users_verified = await UserService.search_users(db_session, email_verified=True)
    assert all(user.email_verified for user in users_verified)

    users_unverified = await UserService.search_users(db_session, email_verified=False)
    assert all(not user.email_verified for user in users_unverified)
