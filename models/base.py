"""Base models and common data structures for LinkedIn data."""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class BaseModel:
    """Base model with common configuration."""
    pass


@dataclass
class LinkedInEntity(BaseModel):
    """Base class for all LinkedIn entities."""
    
    entity_urn: Optional[str] = None
    type: Optional[str] = None
    recipe_types: Optional[List[str]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LinkedInEntity":
        """Create from dictionary with field name mapping."""
        return cls(
            entity_urn=data.get("entityUrn"),
            type=data.get("$type"),
            recipe_types=data.get("$recipeTypes"),
        )


@dataclass
class VectorArtifact(BaseModel):
    """Vector image artifact with dimensions and URL."""
    
    width: int = 0
    height: int = 0
    file_identifying_url_path_segment: Optional[str] = None
    expires_at: Optional[int] = None
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VectorArtifact":
        """Create from dictionary."""
        return cls(
            width=data.get("width", 0),
            height=data.get("height", 0),
            file_identifying_url_path_segment=data.get("fileIdentifyingUrlPathSegment"),
            expires_at=data.get("expiresAt"),
            type=data.get("$type"),
        )


@dataclass
class VectorImage(BaseModel):
    """Vector image with multiple artifacts."""
    
    root_url: Optional[str] = None
    artifacts: Optional[List[VectorArtifact]] = None
    digitalmedia_asset: Optional[str] = None
    attribution: Optional[Any] = None
    c2pa_manifest_data: Optional[Any] = None
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VectorImage":
        """Create from dictionary."""
        artifacts = None
        if data.get("artifacts"):
            artifacts = [VectorArtifact.from_dict(a) for a in data["artifacts"]]
        
        return cls(
            root_url=data.get("rootUrl"),
            artifacts=artifacts,
            digitalmedia_asset=data.get("digitalmediaAsset"),
            attribution=data.get("attribution"),
            c2pa_manifest_data=data.get("c2paManifestData"),
            type=data.get("$type"),
        )


@dataclass
class TextAttribute(BaseModel):
    """Text attribute with position and detail data."""
    
    start: int = 0
    length: int = 0
    detail_data: Optional[Dict[str, Any]] = None
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TextAttribute":
        """Create from dictionary."""
        return cls(
            start=data.get("start", 0),
            length=data.get("length", 0),
            detail_data=data.get("detailData"),
            type=data.get("$type"),
        )


@dataclass
class TextViewModel(BaseModel):
    """Text view model with text content and attributes."""
    
    text: str = ""
    text_direction: Optional[str] = None
    attributes_v2: Optional[List[TextAttribute]] = None
    accessibility_text_attributes_v2: Optional[List[TextAttribute]] = None
    accessibility_text: Optional[str] = None
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TextViewModel":
        """Create from dictionary."""
        attributes_v2 = None
        if data.get("attributesV2"):
            attributes_v2 = [TextAttribute.from_dict(a) for a in data["attributesV2"]]
        
        accessibility_text_attributes_v2 = None
        if data.get("accessibilityTextAttributesV2"):
            accessibility_text_attributes_v2 = [
                TextAttribute.from_dict(a) for a in data["accessibilityTextAttributesV2"]
            ]
        
        return cls(
            text=data.get("text", ""),
            text_direction=data.get("textDirection"),
            attributes_v2=attributes_v2,
            accessibility_text_attributes_v2=accessibility_text_attributes_v2,
            accessibility_text=data.get("accessibilityText"),
            type=data.get("$type"),
        )


@dataclass
class ImageAttribute(BaseModel):
    """Image attribute with detail data."""
    
    scaling_type: Optional[str] = None
    detail_data: Optional[Dict[str, Any]] = None
    tint_color: Optional[Any] = None
    tap_targets: Optional[List[Any]] = None
    display_aspect_ratio: Optional[float] = None
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImageAttribute":
        """Create from dictionary."""
        return cls(
            scaling_type=data.get("scalingType"),
            detail_data=data.get("detailData"),
            tint_color=data.get("tintColor"),
            tap_targets=data.get("tapTargets"),
            display_aspect_ratio=data.get("displayAspectRatio"),
            type=data.get("$type"),
        )


@dataclass
class ImageViewModel(BaseModel):
    """Image view model with attributes."""
    
    attributes: Optional[List[ImageAttribute]] = None
    editable_accessibility_text: Optional[bool] = None
    action_target: Optional[str] = None
    accessibility_text_attributes: Optional[List[Any]] = None
    total_count: Optional[int] = None
    accessibility_text: Optional[str] = None
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImageViewModel":
        """Create from dictionary."""
        attributes = None
        if data.get("attributes"):
            attributes = [ImageAttribute.from_dict(a) for a in data["attributes"]]
        
        return cls(
            attributes=attributes,
            editable_accessibility_text=data.get("editableAccessibilityText"),
            action_target=data.get("actionTarget"),
            accessibility_text_attributes=data.get("accessibilityTextAttributes"),
            total_count=data.get("totalCount"),
            accessibility_text=data.get("accessibilityText"),
            type=data.get("$type"),
        )


@dataclass
class NavigationContext(BaseModel):
    """Navigation context with URL and tracking information."""
    
    action_target: Optional[str] = None
    url_viewing_behavior: Optional[str] = None
    tracking_action_type: Optional[str] = None
    accessibility_text: Optional[str] = None
    sponsored_url_attributes: Optional[Any] = None
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NavigationContext":
        """Create from dictionary."""
        return cls(
            action_target=data.get("actionTarget"),
            url_viewing_behavior=data.get("urlViewingBehavior"),
            tracking_action_type=data.get("trackingActionType"),
            accessibility_text=data.get("accessibilityText"),
            sponsored_url_attributes=data.get("sponsoredUrlAttributes"),
            type=data.get("$type"),
        )
