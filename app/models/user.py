"""
Database Models for Project Meghan - Student Wellness Assistant

This module contains SQLAlchemy ORM models representing the database schema.
Each model corresponds to a database table and handles data persistence.

Model Overview:
---------------

1. User
   Purpose: Core user authentication and identity
   Focus: Stores login credentials (email, password_hash) and basic user metadata
   Relationship: One-to-one with UserProfile and UserState

2. UserProfile
   Purpose: Extended user bio and profile information
   Focus: Stores user's personal information for personalization (name, major, hobbies, values, bio)
   Fields:
   - name: User's display name
   - major: Academic major/field of study
   - hobbies: User's hobbies/interests (stored as string)
   - values: User's personal values/principles (stored as string)
   - bio: Optional general biographical text
   - profile_picture: URL to profile picture
   Relationship: Belongs to one User

3. UserState
   Purpose: Current user's wellness state and metrics
   Focus: Tracks mood, risk tier, wellness metrics (steps, sleep, pomo sessions), XP, and level
   Fields:
   - mood: Current emotional state ('Heavy', 'Pulse', 'Grounded')
   - stress_source: Source of stress ('Family', 'Relationship', 'Career/Academics', 'Others')
   - other_text: Additional context when stress_source is 'Others'
   - risk_tier: Risk assessment level ('Green', 'Yellow', 'Red')
   - xp: Experience points (used for gamification)
   - level: User level (calculated from XP: floor(xp / 200) + 1)
   - steps: Daily step count
   - sleep_hours: Hours of sleep
   - pomo_sessions: Pomodoro technique sessions completed
   Relationship: Belongs to one User (one-to-one)

4. Conversation
   Purpose: Groups chat messages into conversations with contextual information
   Focus: Creates a conversation container that captures the context (mood, tier, stress source) 
          at the time the conversation started. This allows the system to understand the user's
          state when a conversation began, even if their current state changes.
   Fields:
   - tier: Risk tier when conversation started
   - mood: Mood when conversation started
   - source: Stress source when conversation started
   Relationship: Belongs to one User, has many ChatMessages (one-to-many)

5. ChatMessage
   Purpose: Individual messages within a conversation
   Focus: Stores each message exchange between user and AI assistant
   Fields:
   - role: Who sent the message - 'user' (student) or 'model' (AI assistant)
   - content: The actual message text (can be long, hence Text type)
   Relationship: Belongs to one Conversation (many-to-one)

6. JournalEntry
   Purpose: Store sentiment journal entries for user reflection
   Focus: Persists user's journal entries with context of their state at time of entry
   Fields:
   - content: Journal entry text
   - mood_at_time: Mood when entry was created
   - tier_at_time: Risk tier when entry was created
   - xp_gained: XP awarded for completing journal entry (default: 30)
   Relationship: Belongs to one User (one-to-many)

7. PeerCluster
   Purpose: Peer support groups/clusters for community features
   Focus: Defines peer support groups that users can join
   Relationship: Many-to-many with User via UserClusterMembership

8. UserClusterMembership
   Purpose: Join table for user-cluster relationships
   Focus: Tracks which users belong to which peer clusters (many-to-many relationship)
   Relationship: Links User and PeerCluster
"""

from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.functions import now

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="cascade"))
    name = Column(String, index=True, nullable=True)
    bio = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    major = Column(String, nullable=True)
    hobbies = Column(String, nullable=True)
    values = Column(String, nullable=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class UserState(Base):
    __tablename__ = "user_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="cascade"))
    mood = Column(String)
    stress_source = Column(String, nullable=True)
    other_text = Column(String, nullable=True)
    risk_tier = Column(String)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    steps = Column(Integer, default=0)
    sleep_hours = Column(Integer, default=0)
    pomo_sessions = Column(Integer, default=0)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="cascade"))
    tier = Column(String)
    mood = Column(String)
    source = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="cascade"))
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=func.now(), index=True)

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="cascade"))
    content = Column(Text)
    mood_at_time = Column(String, nullable=True)
    tier_at_time = Column(String, nullable=True)
    xp_gained = Column(Integer, default=30)
    created_at = Column(DateTime, default=func.now(), index=True)

class PeerCluster(Base):
    __tablename__ = "peer_clusters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)
    created_at = Column(DateTime, default=func.now())

class UserClusterMembership(Base):
    __tablename__ = "user_cluster_memberships"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    cluster_id = Column(Integer, ForeignKey("peer_clusters.id"), primary_key=True)
    joined_at = Column(DateTime, default=func.now())

class HeartsTransaction(Base):
   __tablename__ = "hearts_transactions"

   id=Column(Integer,primary_key=True,index=True)
   user_id=Column(Integer,ForeignKey("users.id",ondelete="cascade"))
   amount=Column(Integer,nullable=False)
   type=Column(String,nullable=False)
   description=Column(String,nullable=False)
   balance_after=Column(Integer,nullable=False)
   created_at=Column(DateTime,default=func.now(),index=True)
