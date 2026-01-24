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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InfiniteScrollMetadata":
        """Create from dictionary."""
        return cls(
            pagination_token=data.get("paginationToken"),
        )


@dataclass
class CollectionMetadata(BaseModel):
    """Collection pagination metadata."""
    
    count: Optional[int] = None
    start: Optional[int] = None
    total: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CollectionMetadata":
        """Create from dictionary."""
        return cls(
            count=data.get("count"),
            start=data.get("start"),
            total=data.get("total"),
        )


@dataclass
class CollectionResponse(BaseModel):
    """Collection response with elements and pagination."""
    
    elements: Optional[List[str]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CollectionResponse":
        """Create from dictionary."""
        return cls(
            elements=data.get("*elements"),
        )


@dataclass
class ReactionsCollectionResponse(BaseModel):
    """Reactions collection response."""
    
    feed_dash_profile_updates_by_member_reactions: Optional[CollectionResponse] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReactionsCollectionResponse":
        """Create from dictionary."""
        reactions = None
        if data.get("feedDashProfileUpdatesByMemberReactions"):
            reactions = CollectionResponse.from_dict(data["feedDashProfileUpdatesByMemberReactions"])
        
        return cls(
            feed_dash_profile_updates_by_member_reactions=reactions,
        )


@dataclass
class CommentsCollectionResponse(BaseModel):
    """Comments collection response."""
    
    feed_dash_profile_updates_by_member_comments: Optional[CollectionResponse] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CommentsCollectionResponse":
        """Create from dictionary."""
        comments = None
        if data.get("feedDashProfileUpdatesByMemberComments"):
            comments = CollectionResponse.from_dict(data["feedDashProfileUpdatesByMemberComments"])
        
        return cls(
            feed_dash_profile_updates_by_member_comments=comments,
        )


@dataclass
class PostsCollectionResponse(BaseModel):
    """Posts collection response."""
    
    feed_dash_profile_updates_by_member_share_feed: Optional[CollectionResponse] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PostsCollectionResponse":
        """Create from dictionary."""
        posts = None
        if data.get("feedDashProfileUpdatesByMemberShareFeed"):
            posts = CollectionResponse.from_dict(data["feedDashProfileUpdatesByMemberShareFeed"])
        
        return cls(
            feed_dash_profile_updates_by_member_share_feed=posts,
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
    index: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CommentsResponse(BaseModel):
    """Parsed comments response with typed Comment objects."""
    
    comments: List[Comment] = field(default_factory=list)
    index: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PostsResponse(BaseModel):
    """Parsed posts response with typed Update objects."""
    
    updates: List[Update] = field(default_factory=list)
    index: Dict[str, Any] = field(default_factory=dict)
