"""Main parser factory for LinkedIn JSON data."""

import json
from typing import Dict, Any, Optional, List
from pathlib import Path

from models.response import (
    LinkedInResponse,
    ReactionsResponse,
    CommentsResponse,
    ReactionsCollectionResponse,
    CommentsCollectionResponse,
)
from models.update import Update, UpdateParser
from models.comment import Comment, CommentParser


class LinkedInDataParser:
    """Main parser for LinkedIn JSON data."""
    
    # Type mappings for routing
    UPDATE_TYPE = "com.linkedin.voyager.dash.feed.Update"
    COMMENT_TYPE = "com.linkedin.voyager.dash.social.Comment"
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        Initialize parser with JSON data.
        
        Args:
            json_data: Raw JSON data dictionary
        """
        self.json_data = json_data
        self.index: Dict[str, Any] = {}
        self._build_index()
    
    @classmethod
    def from_file(cls, file_path: str) -> "LinkedInDataParser":
        """
        Create parser from JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            LinkedInDataParser instance
        """
        with open(file_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        return cls(json_data)
    
    def _build_index(self) -> None:
        """Build lookup index from included array."""
        if not self.json_data:
            return
        
        included = self.json_data.get("included", [])
        for item in included:
            entity_urn = item.get("entityUrn")
            if entity_urn:
                self.index[entity_urn] = item
    
    def _get_elements(self) -> List[str]:
        """Extract element URNs from the response."""
        if not self.json_data:
            return []
        
        data = self.json_data.get("data", {}).get("data", {})
        
        # Try reactions first
        reactions = data.get("feedDashProfileUpdatesByMemberReactions")
        if reactions:
            return reactions.get("*elements", [])
        
        # Try comments
        comments = data.get("feedDashProfileUpdatesByMemberComments")
        if comments:
            return comments.get("*elements", [])
        
        return []
    
    def parse_reactions(self) -> ReactionsResponse:
        """
        Parse reactions from JSON data.
        
        Returns:
            ReactionsResponse with typed Update objects
        """
        elements = self._get_elements()
        update_parser = UpdateParser(self.index)
        updates = update_parser.parse_list(elements)
        
        return ReactionsResponse(
            updates=updates,
            raw_response=LinkedInResponse.from_dict(self.json_data) if self.json_data else None,
            index=self.index,
        )
    
    def parse_comments(self) -> CommentsResponse:
        """
        Parse comments from JSON data.
        
        Note: comment.json contains Updates, each with highlightedComments.
        We parse Updates first, then extract their highlighted comments.
        
        Returns:
            CommentsResponse with typed Comment objects
        """
        elements = self._get_elements()
        update_parser = UpdateParser(self.index)
        updates = update_parser.parse_list(elements)
        
        # Extract all highlighted comments from Updates
        all_comments = []
        for update in updates:
            if update and update.highlighted_comments:
                all_comments.extend(update.highlighted_comments)
        
        return CommentsResponse(
            comments=all_comments,
            raw_response=LinkedInResponse.from_dict(self.json_data) if self.json_data else None,
            index=self.index,
        )
    
    def parse_by_type(self, entity_type: str) -> List[Any]:
        """
        Parse entities by type from the index.
        
        Args:
            entity_type: The $type field value to filter by
            
        Returns:
            List of parsed entities
        """
        results = []
        
        if entity_type == self.UPDATE_TYPE:
            update_parser = UpdateParser(self.index)
            for urn, data in self.index.items():
                if data.get("$type") == entity_type:
                    update = update_parser.parse(data)
                    if update:
                        results.append(update)
        elif entity_type == self.COMMENT_TYPE:
            comment_parser = CommentParser(self.index)
            for urn, data in self.index.items():
                if data.get("$type") == entity_type:
                    comment = comment_parser.parse(data)
                    if comment:
                        results.append(comment)
        else:
            # Generic parsing - return raw data
            for urn, data in self.index.items():
                if data.get("$type") == entity_type:
                    results.append(data)
        
        return results
    
    def resolve_urn(self, urn: str) -> Optional[Dict[str, Any]]:
        """
        Resolve a URN to its data object.
        
        Args:
            urn: Entity URN to resolve
            
        Returns:
            Data object or None if not found
        """
        return self.index.get(urn)
