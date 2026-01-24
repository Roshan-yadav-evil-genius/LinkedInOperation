"""Comment models and parser for LinkedIn data."""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from .base import BaseModel, TextViewModel
from .actor import Commenter


@dataclass
class SocialDetail(BaseModel):
    """Social detail information for comments."""
    
    elements: Optional[List[str]] = None  # Reply URNs from comments.*elements
    
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
            elements=reply_urns,
        )


@dataclass
class Comment(BaseModel):
    """Comment data model."""
    
    commentary: Optional[TextViewModel] = None
    commenter: Optional[Commenter] = None
    social_detail_urn: Optional[str] = None
    social_detail: Optional[SocialDetail] = None
    replies: List["Comment"] = field(default_factory=list)
    
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
            commentary=commentary,
            commenter=commenter,
            social_detail_urn=data.get("*socialDetail"),
            social_detail=None,  # Will be resolved separately
            replies=[],
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
