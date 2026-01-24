from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.console import Group
from parsers.factory import LinkedInDataParser
from models.update import Update
from models.comment import Comment, CommentParser

# Parse reactions using the new typed classes
parser = LinkedInDataParser.from_file("reaction.json")
reactions_response = parser.parse_reactions()
comment_parser = CommentParser(parser.index)

# Initialize rich console
console = Console()

def create_comment_panel(comment: Comment, is_reply: bool = False, index: dict = None) -> Panel:
    """Helper function to create a comment panel with nested replies using typed Comment object"""
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
    if comment_profile_url:
        comment_content.append(f"{comment_author}", style="bold white underline")
        comment_content.append(f"\nProfile: {comment_profile_url}", style="dim blue")
    else:
        comment_content.append(f"{comment_author}", style="bold white")
    
    if comment_headline:
        comment_content.append(f"\n{comment_headline}", style="dim yellow" if not is_reply else "dim green")
    
    comment_content.append("\n\nComment: ", style="bold yellow" if not is_reply else "bold green")
    comment_content.append(f"{comment_text}", style="white")
    
    # Get replies for this comment (now using typed replies list)
    # Also check social_detail directly as fallback (like original code)
    reply_panels = []
    
    # First try the parsed replies list
    if comment.replies:
        for reply in comment.replies:
            reply_panel = create_comment_panel(reply, is_reply=True, index=index)
            reply_panels.append(reply_panel)
    # Fallback: check social_detail directly if replies weren't parsed
    elif comment.social_detail and comment.social_detail.elements and index:
        # Parse replies on-the-fly from social_detail
        for reply_urn in comment.social_detail.elements:
            reply_data = index.get(reply_urn)
            if reply_data:
                reply = comment_parser.parse(reply_data)
                if reply:
                    reply_panel = create_comment_panel(reply, is_reply=True, index=index)
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

# Process each update with typed access
for update in reactions_response.updates:
    # Skip if not a valid Update
    if not update:
        continue

    # --- 1. THE ACTION & REACTION TYPE ---
    header_text = update.header.text if update.header else ""

    # --- 2. THE ORIGINAL POST TEXT ---
    # In a reaction update, the original post text is often in 'commentary'
    post_text = "No text content"
    if update.commentary:
        post_text = update.commentary.text if update.commentary.text else "No text content"
    
    # --- 3. THE ORIGINAL AUTHOR ---
    # Use typed actor component
    author_name = "Unknown Author"
    author_headline = ""
    if update.actor:
        if update.actor.name:
            author_name = update.actor.name.text or "Unknown Author"
        if update.actor.description:
            author_headline = update.actor.description.text or ""

    # --- 4. THE URL ---
    post_url = None
    if update.social_content and update.social_content.share_url:
        post_url = update.social_content.share_url
    elif update.metadata and update.metadata.share_url:
        post_url = update.metadata.share_url

    # --- 5. EXTRACT COMMENTS WITH REPLIES ---
    # Now using typed highlighted_comments list
    comment_panels = []
    
    if update.highlighted_comments:
        for comment in update.highlighted_comments:
            # Create comment panel (which will recursively include replies)
            comment_panel = create_comment_panel(comment, is_reply=False, index=parser.index)
            comment_panels.append(comment_panel)
    
    # --- 6. CREATE MAIN CONTENT ---
    content = Text()
    content.append("User Action:  ", style="bold cyan")
    content.append(f"{header_text}\n", style="white")
    content.append("Post Author:  ", style="bold cyan")
    content.append(f"{author_name}\n", style="bold white")
    content.append("Post Author Headline: ", style="bold cyan")
    content.append(f"{author_headline}\n", style="dim white")
    content.append("Post Content: ", style="bold cyan")
    content.append(f"{post_text}", style="white")
    content.append("\nLink:         ", style="bold cyan")
    if post_url:
        content.append(f"{post_url}", style="blue underline")
    else:
        content.append("No URL available", style="dim")
    
    # Create main panel
    if comment_panels:
        # Add separator before comments
        content.append("\n\n", style="white")
        content.append("─" * 50, style="dim")
        content.append("\n", style="white")
        
        # Create a combined renderable with main content and comment panels
        renderables = [content]
        renderables.extend(comment_panels)
        
        panel = Panel(
            Group(*renderables),
            title="[bold magenta]ACTIVITY FOUND[/bold magenta]",
            border_style="magenta",
            box=box.ROUNDED
        )
    else:
        panel = Panel(
            content,
            title="[bold magenta]ACTIVITY FOUND[/bold magenta]",
            border_style="magenta",
            box=box.ROUNDED
        )
    
    console.print(panel)
    console.print()  # Empty line for spacing
