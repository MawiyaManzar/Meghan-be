"""
Peer Cluster Schemas for Project Meghan

Handles peer support clusters and memberships (optional feature).
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class PeerClusterBase(BaseModel):
    name: str
    description: str

class PeerClusterCreate(PeerClusterBase):
    pass

class PeerClusterResponse(PeerClusterBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    member_count: Optional[int] = None  # Number of members in cluster

class UserClusterMembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    user_id: int
    cluster_id: int
    cluster_name: str  # For convenience
    joined_at: datetime

class ClusterListResponse(BaseModel):
    clusters: List[PeerClusterResponse]
