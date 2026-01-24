"""Display components for LinkedIn reactions and comments using Rich."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.console import Group
from typing import Optional, Dict, Any

from models.update import Update
from models.comment import Comment
from models.comment import CommentParser


class LinkedInDisplay:
    """Handles all UI/display logic for LinkedIn data."""
    
    def __init__(self):
        """Initialize the display with Rich console."""
        self.console = Console()
    
    def create_comment_panel(
        self, 
        comment: Comment, 
        is_reply: bool = False, 
        index: Dict[str, Any] = None,
        comment_parser: Optional[CommentParser] = None
    ) -> Panel:
        """
        Create a comment panel with nested replies.
        
        Args:
            comment: Comment object to display
            is_reply: Whether this is a reply (affects styling)
            index: Lookup index for resolving URNs
            comment_parser: Parser for parsing replies
            
        Returns:
            Rich Panel with comment content
        """
        # Extract comment data with type safety
        comment_text = comment.commentary.text if comment.commentary else "No text"
        commenter = comment.commenter
        
        if not commenter:
            comment_author = "Unknown"
            comment_profile_url = ""
            comment_headline = ""
        else:
            comment_author = commenter.title.text if commenter.title else "Unknown"
            comment_profile_url = commenter.navigation_url or ""
            comment_headline = commenter.subtitle or ""
        
        # Create comment content with author info
        comment_content = Text()
        comment_content.append("Comment Author: ", style="bold yellow" if not is_reply else "bold green")
        
        # Use Rich link format for clickable author name
        if comment_profile_url:
            comment_content.append(f"{comment_author}", style=f"link {comment_profile_url}")
        else:
            comment_content.append(f"{comment_author}", style="bold white")
        
        # Show headline on same line if available
        if comment_headline:
            comment_content.append(f" ({comment_headline})", style="dim yellow" if not is_reply else "dim green")
        
        comment_content.append("\n\nComment: ", style="bold yellow" if not is_reply else "bold green")
        comment_content.append(f"{comment_text}", style="white")
        
        # Get replies for this comment
        reply_panels = []
        
        # First try the parsed replies list
        if comment.replies:
            for reply in comment.replies:
                reply_panel = self.create_comment_panel(reply, is_reply=True, index=index, comment_parser=comment_parser)
                reply_panels.append(reply_panel)
        # Fallback: check social_detail directly if replies weren't parsed
        elif comment.social_detail and comment.social_detail.elements and index and comment_parser:
            # Parse replies on-the-fly from social_detail
            for reply_urn in comment.social_detail.elements:
                reply_data = index.get(reply_urn)
                if reply_data:
                    reply = comment_parser.parse(reply_data)
                    if reply:
                        reply_panel = self.create_comment_panel(reply, is_reply=True, index=index, comment_parser=comment_parser)
                        reply_panels.append(reply_panel)
        
        # Create panel for this comment
        border_style = "yellow" if not is_reply else "green"
        title = "[bold yellow]COMMENT[/bold yellow]" if not is_reply else "[bold green]REPLY[/bold green]"
        
        if reply_panels:
            # If there are replies, nest them inside
            comment_content.append("\n\n", style="white")
            comment_content.append("─" * 40, style="dim")
            comment_content.append("\n", style="white")
            
            # Create a group with comment content and reply panels
            renderables = [comment_content]
            renderables.extend(reply_panels)
            
            comment_panel = Panel(
                Group(*renderables),
                title=title,
                border_style=border_style,
                box=box.ROUNDED,
                padding=(1, 2)
            )
        else:
            comment_panel = Panel(
                comment_content,
                title=title,
                border_style=border_style,
                box=box.ROUNDED,
                padding=(1, 2)
            )
        
        return comment_panel
    
    def create_reshared_post_panel(
        self,
        reshared_post_text: str,
        reshared_post_author: Optional[str],
        reshared_post_author_headline: Optional[str]
    ) -> Panel:
        """
        Create a panel for displaying reshared post content.
        
        Args:
            reshared_post_text: The original post content
            reshared_post_author: Author of the original post
            reshared_post_author_headline: Headline of the original post author
            
        Returns:
            Rich Panel with reshared post content
        """
        reshared_content = Text()
        reshared_content.append("Original Post Author: ", style="bold cyan")
        # Note: We don't have profile URL for reshared author, so just show name
        reshared_content.append(f"{reshared_post_author or 'Unknown'}", style="bold white")
        if reshared_post_author_headline:
            reshared_content.append(f" ({reshared_post_author_headline})\n", style="dim white")
        else:
            reshared_content.append("\n", style="white")
        reshared_content.append("Original Post Content: ", style="bold cyan")
        reshared_content.append(f"{reshared_post_text}", style="white")
        
        return Panel(
            reshared_content,
            title="[bold blue]RESHARED POST[/bold blue]",
            border_style="blue",
            box=box.ROUNDED,
            padding=(1, 2)
        )
    
    def create_update_panel(
        self,
        update: Update,
        parser_index: Dict[str, Any],
        comment_parser: CommentParser
    ) -> Panel:
        """
        Create a panel for displaying an update with all its content.
        
        Args:
            update: Update object to display
            parser_index: Lookup index for resolving URNs
            comment_parser: Parser for parsing comments
            
        Returns:
            Rich Panel with update content
        """
        # Extract header text
        header_text = update.header.text if update.header else ""
        
        # Extract post text and check for reshared content
        post_text = "No text content"
        reshared_post_text = None
        reshared_post_author = None
        reshared_post_author_headline = None
        
        # Check if this is a reshared post
        if update.reshared_update_urn:
            reshared_data = parser_index.get(update.reshared_update_urn)
            if reshared_data:
                # Get the original post content from the reshared update
                if 'commentary' in reshared_data:
                    comm = reshared_data['commentary']
                    if isinstance(comm, dict) and 'text' in comm:
                        text_obj = comm['text']
                        if isinstance(text_obj, dict) and 'text' in text_obj:
                            reshared_post_text = text_obj['text']
                
                # Get the original post author from the reshared update
                if 'actor' in reshared_data:
                    actor_data = reshared_data['actor']
                    if isinstance(actor_data, dict):
                        if 'name' in actor_data:
                            name_obj = actor_data['name']
                            if isinstance(name_obj, dict) and 'text' in name_obj:
                                reshared_post_author = name_obj['text']
                        if 'description' in actor_data:
                            desc_obj = actor_data['description']
                            if isinstance(desc_obj, dict) and 'text' in desc_obj:
                                reshared_post_author_headline = desc_obj['text']
        
        # The commentary is what the person wrote when resharing (if it's a reshare)
        # Otherwise it's the original post text
        if update.commentary:
            post_text = update.commentary.text if update.commentary.text else "No text content"
        
        # Extract author information
        author_name = "Unknown Author"
        author_headline = ""
        author_profile_url = None
        if update.actor:
            if update.actor.name:
                author_name = update.actor.name.text or "Unknown Author"
            if update.actor.description:
                author_headline = update.actor.description.text or ""
            # Get author profile URL from navigation context
            if update.actor.navigation_context and update.actor.navigation_context.action_target:
                author_profile_url = update.actor.navigation_context.action_target
        
        # Extract URL
        post_url = None
        if update.social_content and update.social_content.share_url:
            post_url = update.social_content.share_url
        elif update.metadata and update.metadata.share_url:
            post_url = update.metadata.share_url
        
        # Create main content
        content = Text()
        content.append("User Action:  ", style="bold cyan")
        content.append(f"{header_text}\n", style="white")
        content.append("Post Author:  ", style="bold cyan")
        
        # Use Rich link format for clickable author name
        if author_profile_url:
            content.append(f"{author_name}", style=f"link {author_profile_url}")
        else:
            content.append(f"{author_name}", style="bold white")
        
        # Show headline on same line if available
        if author_headline:
            content.append(f" ({author_headline})\n", style="dim white")
        else:
            content.append("\n", style="white")
        
        # Display post content
        if reshared_post_text:
            # This is a reshared post - show the reshare commentary first
            content.append("Reshare Commentary: ", style="bold cyan")
            content.append(f"{post_text}\n", style="white")
        else:
            # Regular post
            content.append("Post Content: ", style="bold cyan")
            content.append(f"{post_text}", style="white")
        
        content.append("\nLink:         ", style="bold cyan")
        if post_url:
            content.append(f"{post_url}", style="blue underline")
        else:
            content.append("No URL available", style="dim")
        
        # Create comment panels
        comment_panels = []
        if update.highlighted_comments:
            for comment in update.highlighted_comments:
                comment_panel = self.create_comment_panel(
                    comment, 
                    is_reply=False, 
                    index=parser_index,
                    comment_parser=comment_parser
                )
                comment_panels.append(comment_panel)
        
        # Build renderables list
        renderables = [content]
        
        # Add reshared post panel if it exists
        if reshared_post_text:
            reshared_panel = self.create_reshared_post_panel(
                reshared_post_text,
                reshared_post_author,
                reshared_post_author_headline
            )
            renderables.append(reshared_panel)
        
        # Add comments if they exist
        if comment_panels:
            separator = Text()
            separator.append("\n", style="white")
            separator.append("─" * 50, style="dim")
            separator.append("\n", style="white")
            renderables.append(separator)
            renderables.extend(comment_panels)
        
        # Create main panel
        panel = Panel(
            Group(*renderables),
            title="[bold magenta]ACTIVITY FOUND[/bold magenta]",
            border_style="magenta",
            box=box.ROUNDED
        )
        
        return panel
    
    def display_update(self, panel: Panel) -> None:
        """
        Display an update panel.
        
        Args:
            panel: Rich Panel to display
        """
        self.console.print(panel)
        self.console.print()  # Empty line for spacing
