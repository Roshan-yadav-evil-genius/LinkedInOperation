"""Response models for LinkedIn API responses."""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from .base import BaseModel
from .update import Update
from .comment import Comment


@dataclass
class InfiniteScrollMetadata(BaseModel):
    """Infinite scroll pagination metadata."""
    
    pagination_token: Optional[str] = None
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InfiniteScrollMetadata":
        """Create from dictionary."""
        return cls(
            pagination_token=data.get("paginationToken"),
            type=data.get("$type"),
        )


@dataclass
class CollectionMetadata(BaseModel):
    """Collection pagination metadata."""
    
    count: Optional[int] = None
    start: Optional[int] = None
    total: Optional[int] = None
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CollectionMetadata":
        """Create from dictionary."""
        return cls(
            count=data.get("count"),
            start=data.get("start"),
            total=data.get("total"),
            type=data.get("$type"),
        )


@dataclass
class CollectionResponse(BaseModel):
    """Collection response with elements and pagination."""
    
    metadata: Optional[InfiniteScrollMetadata] = None
    paging: Optional[CollectionMetadata] = None
    elements: Optional[List[str]] = None
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CollectionResponse":
        """Create from dictionary."""
        metadata = None
        if data.get("metadata"):
            metadata = InfiniteScrollMetadata.from_dict(data["metadata"])
        
        paging = None
        if data.get("paging"):
            paging = CollectionMetadata.from_dict(data["paging"])
        
        return cls(
            metadata=metadata,
            paging=paging,
            elements=data.get("*elements"),
            type=data.get("$type"),
        )


@dataclass
class ReactionsCollectionResponse(BaseModel):
    """Reactions collection response."""
    
    feed_dash_profile_updates_by_member_reactions: Optional[CollectionResponse] = None
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReactionsCollectionResponse":
        """Create from dictionary."""
        reactions = None
        if data.get("feedDashProfileUpdatesByMemberReactions"):
            reactions = CollectionResponse.from_dict(data["feedDashProfileUpdatesByMemberReactions"])
        
        return cls(
            feed_dash_profile_updates_by_member_reactions=reactions,
            type=data.get("$type"),
        )


@dataclass
class CommentsCollectionResponse(BaseModel):
    """Comments collection response."""
    
    feed_dash_profile_updates_by_member_comments: Optional[CollectionResponse] = None
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CommentsCollectionResponse":
        """Create from dictionary."""
        comments = None
        if data.get("feedDashProfileUpdatesByMemberComments"):
            comments = CollectionResponse.from_dict(data["feedDashProfileUpdatesByMemberComments"])
        
        return cls(
            feed_dash_profile_updates_by_member_comments=comments,
            type=data.get("$type"),
        )


@dataclass
class LinkedInResponse(BaseModel):
    """Top-level LinkedIn API response."""
    
    data: Optional[Dict[str, Any]] = None
    included: Optional[List[Dict[str, Any]]] = None
    meta: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LinkedInResponse":
        """Create from dictionary."""
        return cls(
            data=data.get("data"),
            included=data.get("included"),
            meta=data.get("meta"),
        )


@dataclass
class ReactionsResponse(BaseModel):
    """Parsed reactions response with typed Update objects."""
    
    updates: List[Update] = field(default_factory=list)
    raw_response: Optional[LinkedInResponse] = None
    index: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CommentsResponse(BaseModel):
    """Parsed comments response with typed Comment objects."""
    
    comments: List[Comment] = field(default_factory=list)
    raw_response: Optional[LinkedInResponse] = None
    index: Dict[str, Any] = field(default_factory=dict)
