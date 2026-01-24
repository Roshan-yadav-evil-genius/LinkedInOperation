"""Update and reaction models for LinkedIn data."""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from .base import BaseModel, TextViewModel
from .actor import ActorComponent
from .comment import Comment, CommentParser


@dataclass
class SocialContent(BaseModel):
    """Social content information."""
    
    share_url: Optional[str] = None
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SocialContent":
        """Create from dictionary."""
        return cls(
            share_url=data.get("shareUrl"),
            type=data.get("$type"),
        )


@dataclass
class UpdateMetadata(BaseModel):
    """Update metadata."""
    
    share_url: Optional[str] = None
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UpdateMetadata":
        """Create from dictionary."""
        return cls(
            share_url=data.get("shareUrl"),
            type=data.get("$type"),
        )


@dataclass
class Update(BaseModel):
    """Update/reaction data model."""
    
    entity_urn: Optional[str] = None
    actor: Optional[ActorComponent] = None
    header: Optional[TextViewModel] = None
    commentary: Optional[TextViewModel] = None
    social_content: Optional[SocialContent] = None
    metadata: Optional[UpdateMetadata] = None
    highlighted_comments_urns: Optional[List[str]] = None
    highlighted_comments: List[Comment] = field(default_factory=list)
    social_detail_urn: Optional[str] = None
    boost_header: Optional[Any] = None
    contextual_header: Optional[Any] = None
    reshared_update_urn: Optional[str] = None  # URN reference to reshared update
    interstitial: Optional[Any] = None
    aggregated_content: Optional[Any] = None
    contextual_description: Optional[Any] = None
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Update":
        """Create from dictionary."""
        actor = None
        if data.get("actor"):
            actor = ActorComponent.from_dict(data["actor"])
        
        header = None
        if data.get("header"):
            # Header can be a dict with text inside
            header_data = data["header"]
            if isinstance(header_data, dict) and "text" in header_data:
                header = TextViewModel.from_dict(header_data["text"])
            elif isinstance(header_data, dict):
                header = TextViewModel.from_dict(header_data)
        
        commentary = None
        if data.get("commentary"):
            commentary_data = data["commentary"]
            if isinstance(commentary_data, dict) and "text" in commentary_data:
                commentary = TextViewModel.from_dict(commentary_data["text"])
            elif isinstance(commentary_data, dict):
                commentary = TextViewModel.from_dict(commentary_data)
        
        social_content = None
        if data.get("socialContent"):
            social_content = SocialContent.from_dict(data["socialContent"])
        
        metadata = None
        if data.get("metadata"):
            metadata = UpdateMetadata.from_dict(data["metadata"])
        
        return cls(
            entity_urn=data.get("entityUrn"),
            actor=actor,
            header=header,
            commentary=commentary,
            social_content=social_content,
            metadata=metadata,
            highlighted_comments_urns=data.get("*highlightedComments"),
            highlighted_comments=[],
            social_detail_urn=data.get("*socialDetail"),
            boost_header=data.get("boostHeader"),
            contextual_header=data.get("contextualHeader"),
            reshared_update_urn=data.get("*resharedUpdate"),  # Note: *resharedUpdate is a URN reference
            interstitial=data.get("interstitial"),
            aggregated_content=data.get("aggregatedContent"),
            contextual_description=data.get("contextualDescription"),
            type=data.get("$type"),
        )


class UpdateParser:
    """Parser for converting JSON update data to Update objects."""
    
    def __init__(self, index: Dict[str, Any]):
        """
        Initialize parser with lookup index.
        
        Args:
            index: Dictionary mapping entity URNs to their data objects
        """
        self.index = index
        self.comment_parser = CommentParser(index)
    
    def parse(self, update_data: Dict[str, Any]) -> Optional[Update]:
        """
        Parse an update from JSON data.
        
        Args:
            update_data: Raw update JSON data
            
        Returns:
            Update object or None if parsing fails
        """
        try:
            # Parse the main update
            update = Update.from_dict(update_data)
            
            # Resolve highlighted comments if present
            if update.highlighted_comments_urns:
                update.highlighted_comments = self.comment_parser.parse_list(
                    update.highlighted_comments_urns
                )
            
            return update
        except Exception as e:
            # Log error but don't fail completely
            print(f"Error parsing update: {e}")
            return None
    
    def parse_list(self, update_urns: List[str]) -> List[Update]:
        """
        Parse a list of updates from URNs.
        
        Args:
            update_urns: List of update URNs
            
        Returns:
            List of Update objects
        """
        updates = []
        for urn in update_urns:
            update_data = self.index.get(urn)
            if update_data:
                update = self.parse(update_data)
                if update:
                    updates.append(update)
        return updates
