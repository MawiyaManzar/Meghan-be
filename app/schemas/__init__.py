"""
Schemas package for Project Meghan

Exports all Pydantic schemas for API request/response validation.
"""
from .hearts import HeartsBalance, HeartsTransactionResponse, HeartsTransactionCreate


# Authentication schemas
from .auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    TokenData,
)

# User profile schemas
from .user import (
    UserProfileBase,
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
)

# User state schemas
from .userState import (
    UserStateBase,
    UserStateCreate,
    UserStateUpdate,
    UserStateResponse,
    XPAddRequest,
    XPAddResponse,
)

# Chat schemas
from .chat import (
    ConversationBase,
    ConversationCreate,
    ConversationResponse,
    ChatMessageBase,
    ChatMessageCreate,
    ChatMessageResponse,
    ConversationListResponse,
    ChatHistoryResponse,
)

# Dashboard schemas
from .dashboard import (
    DashboardResponse,
)

# Leaderboard schemas
from .leaderboard import (
    LeaderboardEntry,
    LeaderboardResponse,
)

# Journal schemas
from .journal import (
    JournalEntryCreate,
    JournalEntryUpdate,
    JournalEntryResponse,
    JournalEntryListResponse,
)

from .cluster import (
    PeerClusterBase,
    PeerClusterCreate,
    PeerClusterResponse,
    UserClusterMembershipResponse,
    ClusterListResponse,
)

# Therapist / crisis schemas
from .therapist import (
    CrisisEventResponse,
    CrisisEventListResponse,
)

__all__ = [
    # Auth
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenData",
    # Profile
    "UserProfileBase",
    "UserProfileCreate",
    "UserProfileUpdate",
    "UserProfileResponse",
    # State
    "UserStateBase",
    "UserStateCreate",
    "UserStateUpdate",
    "UserStateResponse",
    "XPAddRequest",
    "XPAddResponse",
    # Chat
    "ConversationBase",
    "ConversationCreate",
    "ConversationResponse",
    "ChatMessageBase",
    "ChatMessageCreate",
    "ChatMessageResponse",
    "ConversationListResponse",
    "ChatHistoryResponse",
    # Dashboard
    "DashboardResponse",
    # Leaderboard
    "LeaderboardEntry",
    "LeaderboardResponse",
    # Journal
    "JournalEntryCreate",
    "JournalEntryUpdate",
    "JournalEntryResponse",
    "JournalEntryListResponse",
    # Cluster
    "PeerClusterBase",
    "PeerClusterCreate",
    "PeerClusterResponse",
    "UserClusterMembershipResponse",
    "ClusterListResponse",
    # Therapist / crisis
    "CrisisEventResponse",
    "CrisisEventListResponse",
    # Hearts
    "HeartsBalance",
    "HeartsTransactionResponse",
    "HeartsTransactionCreate",
]
