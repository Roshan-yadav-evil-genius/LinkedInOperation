"""Actor and profile models for LinkedIn data."""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from .base import BaseModel, TextViewModel, ImageViewModel, NavigationContext


@dataclass
class FollowAction(BaseModel):
    """Follow action information."""
    
    type: Optional[str] = None
    follow_tracking_action_type: Optional[str] = None
    unfollow_tracking_action_type: Optional[str] = None
    mute_tracking_action_type: Optional[str] = None
    unmute_tracking_action_type: Optional[str] = None
    company_following_tracking_context: Optional[Any] = None
    following_state_urn: Optional[str] = None
    type_field: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FollowAction":
        """Create from dictionary."""
        return cls(
            type=data.get("type"),
            follow_tracking_action_type=data.get("followTrackingActionType"),
            unfollow_tracking_action_type=data.get("unfollowTrackingActionType"),
            mute_tracking_action_type=data.get("muteTrackingActionType"),
            unmute_tracking_action_type=data.get("unmuteTrackingActionType"),
            company_following_tracking_context=data.get("companyFollowingTrackingContext"),
            following_state_urn=data.get("*followingState"),
            type_field=data.get("$type"),
        )


@dataclass
class FollowingState(BaseModel):
    """Following state information."""
    
    entity_urn: Optional[str] = None
    following: Optional[bool] = None
    following_type: Optional[str] = None
    follower_count: Optional[int] = None
    followee_count: Optional[int] = None
    tracking_urn: Optional[str] = None
    pre_dash_following_info_urn: Optional[str] = None
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FollowingState":
        """Create from dictionary."""
        return cls(
            entity_urn=data.get("entityUrn"),
            following=data.get("following"),
            following_type=data.get("followingType"),
            follower_count=data.get("followerCount"),
            followee_count=data.get("followeeCount"),
            tracking_urn=data.get("trackingUrn"),
            pre_dash_following_info_urn=data.get("preDashFollowingInfoUrn"),
            type=data.get("$type"),
        )


@dataclass
class ActorComponent(BaseModel):
    """Actor component representing a person or entity."""
    
    name: Optional[TextViewModel] = None
    description: Optional[TextViewModel] = None
    sub_description: Optional[TextViewModel] = None
    supplementary_actor_info: Optional[TextViewModel] = None
    image: Optional[ImageViewModel] = None
    navigation_context: Optional[NavigationContext] = None
    follow_action: Optional[FollowAction] = None
    connect_action: Optional[Any] = None
    backend_urn: Optional[str] = None
    ring_status: Optional[Any] = None
    group_membership_for_join_action: Optional[Any] = None
    show_small_actor_portrait: Optional[bool] = None
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActorComponent":
        """Create from dictionary."""
        name = None
        if data.get("name"):
            name = TextViewModel.from_dict(data["name"])
        
        description = None
        if data.get("description"):
            description = TextViewModel.from_dict(data["description"])
        
        sub_description = None
        if data.get("subDescription"):
            sub_description = TextViewModel.from_dict(data["subDescription"])
        
        supplementary_actor_info = None
        if data.get("supplementaryActorInfo"):
            supplementary_actor_info = TextViewModel.from_dict(data["supplementaryActorInfo"])
        
        image = None
        if data.get("image"):
            image = ImageViewModel.from_dict(data["image"])
        
        navigation_context = None
        if data.get("navigationContext"):
            navigation_context = NavigationContext.from_dict(data["navigationContext"])
        
        follow_action = None
        if data.get("followAction"):
            follow_action = FollowAction.from_dict(data["followAction"])
        
        return cls(
            name=name,
            description=description,
            sub_description=sub_description,
            supplementary_actor_info=supplementary_actor_info,
            image=image,
            navigation_context=navigation_context,
            follow_action=follow_action,
            connect_action=data.get("connectAction"),
            backend_urn=data.get("backendUrn"),
            ring_status=data.get("ringStatus"),
            group_membership_for_join_action=data.get("groupMembershipForJoinAction"),
            show_small_actor_portrait=data.get("showSmallActorPortrait"),
            type=data.get("$type"),
        )


@dataclass
class Commenter(BaseModel):
    """Commenter information (simplified actor for comments)."""
    
    title: Optional[TextViewModel] = None
    subtitle: Optional[str] = None
    image: Optional[ImageViewModel] = None
    navigation_url: Optional[str] = None
    follow_action: Optional[FollowAction] = None
    accessibility_text: Optional[str] = None
    urn: Optional[str] = None
    actor: Optional[Dict[str, Any]] = None
    tracking_action_type: Optional[str] = None
    tracking_id: Optional[str] = None
    type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Commenter":
        """Create from dictionary."""
        title = None
        if data.get("title"):
            title = TextViewModel.from_dict(data["title"])
        
        image = None
        if data.get("image"):
            image = ImageViewModel.from_dict(data["image"])
        
        follow_action = None
        if data.get("followAction"):
            follow_action = FollowAction.from_dict(data["followAction"])
        
        return cls(
            title=title,
            subtitle=data.get("subtitle"),
            image=image,
            navigation_url=data.get("navigationUrl"),
            follow_action=follow_action,
            accessibility_text=data.get("accessibilityText"),
            urn=data.get("urn"),
            actor=data.get("actor"),
            tracking_action_type=data.get("trackingActionType"),
            tracking_id=data.get("trackingId"),
            type=data.get("$type"),
        )
