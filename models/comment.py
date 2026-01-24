"""Comment models and parser for LinkedIn data."""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from .base import BaseModel, TextViewModel
from .actor import Commenter


@dataclass
class SocialDetail(BaseModel):
    """Social detail information for comments."""
    
    comments: Optional[Dict[str, Any]] = None
    elements: Optional[List[str]] = None  # Reply URNs from comments.*elements
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SocialDetail":
        """Create from dictionary."""
        # Extract reply URNs from comments.elements (or comments.*elements)
        reply_urns = None
        comments_data = data.get("comments")
        if comments_data and isinstance(comments_data, dict):
            # Try both 'elements' and '*elements' as the key might vary
            reply_urns = comments_data.get("*elements") or comments_data.get("elements")
        
        return cls(
            comments=comments_data,
            elements=reply_urns,
            type=data.get("$type"),
        )


@dataclass
class Comment(BaseModel):
    """Comment data model."""
    
    entity_urn: Optional[str] = None
    urn: Optional[str] = None
    commentary: Optional[TextViewModel] = None
    commenter: Optional[Commenter] = None
    created_at: Optional[int] = None
    permalink: Optional[str] = None
    parent_comment_urn: Optional[str] = None
    parent_comment: Optional[Any] = None
    social_detail_urn: Optional[str] = None
    social_detail: Optional[SocialDetail] = None
    display_reason: Optional[str] = None
    hide_comment_action_urn: Optional[str] = None
    translation: Optional[Any] = None
    actions: Optional[List[str]] = None
    headline: Optional[Any] = None
    contributed: Optional[bool] = None
    tracking_id: Optional[str] = None
    annotation: Optional[Any] = None
    edited: Optional[bool] = None
    thread_urn: Optional[str] = None
    time_offset: Optional[int] = None
    root_social_permissions: Optional[Any] = None
    replies: List["Comment"] = field(default_factory=list)
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Comment":
        """Create from dictionary."""
        commentary = None
        if data.get("commentary"):
            commentary = TextViewModel.from_dict(data["commentary"])
        
        commenter = None
        if data.get("commenter"):
            commenter = Commenter.from_dict(data["commenter"])
        
        return cls(
            entity_urn=data.get("entityUrn"),
            urn=data.get("urn"),
            commentary=commentary,
            commenter=commenter,
            created_at=data.get("createdAt"),
            permalink=data.get("permalink"),
            parent_comment_urn=data.get("parentCommentUrn"),
            parent_comment=data.get("parentComment"),
            social_detail_urn=data.get("*socialDetail"),
            social_detail=None,  # Will be resolved separately
            display_reason=data.get("displayReason"),
            hide_comment_action_urn=data.get("*hideCommentAction"),
            translation=data.get("translation"),
            actions=data.get("actions"),
            headline=data.get("headline"),
            contributed=data.get("contributed"),
            tracking_id=data.get("trackingId"),
            annotation=data.get("annotation"),
            edited=data.get("edited"),
            thread_urn=data.get("threadUrn"),
            time_offset=data.get("timeOffset"),
            root_social_permissions=data.get("rootSocialPermissions"),
            replies=[],
            type=data.get("$type"),
        )


class CommentParser:
    """Parser for converting JSON comment data to Comment objects."""
    
    def __init__(self, index: Dict[str, Any]):
        """
        Initialize parser with lookup index.
        
        Args:
            index: Dictionary mapping entity URNs to their data objects
        """
        self.index = index
    
    def parse(self, comment_data: Dict[str, Any]) -> Optional[Comment]:
        """
        Parse a comment from JSON data.
        
        Args:
            comment_data: Raw comment JSON data
            
        Returns:
            Comment object or None if parsing fails
        """
        try:
            # Parse the main comment
            comment = Comment.from_dict(comment_data)
            
            # Resolve social detail if present
            if comment.social_detail_urn:
                social_detail_data = self.index.get(comment.social_detail_urn)
                if social_detail_data:
                    comment.social_detail = SocialDetail.from_dict(social_detail_data)
                    
                    # Parse nested replies
                    if comment.social_detail and comment.social_detail.elements:
                        for reply_urn in comment.social_detail.elements:
                            reply_data = self.index.get(reply_urn)
                            if reply_data:
                                reply_parser = CommentParser(self.index)
                                reply = reply_parser.parse(reply_data)
                                if reply:
                                    comment.replies.append(reply)
            
            return comment
        except Exception as e:
            # Log error but don't fail completely
            print(f"Error parsing comment: {e}")
            return None
    
    def parse_list(self, comment_urns: List[str]) -> List[Comment]:
        """
        Parse a list of comments from URNs.
        
        Args:
            comment_urns: List of comment URNs
            
        Returns:
            List of Comment objects
        """
        comments = []
        for urn in comment_urns:
            comment_data = self.index.get(urn)
            if comment_data:
                comment = self.parse(comment_data)
                if comment:
                    comments.append(comment)
        return comments
