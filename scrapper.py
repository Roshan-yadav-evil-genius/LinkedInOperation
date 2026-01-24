from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.console import Group
import json

with open("reaction.json", "r") as f:
    json_data = json.load(f)
    
# 1. Create lookup index for speed
index = {item.get('entityUrn'): item for item in json_data['included'] if 'entityUrn' in item}

# 2. Extract activities
activities = json_data.get('data', {}).get('data', {}).get('feedDashProfileUpdatesByMemberReactions', {}).get('*elements', [])

# Initialize rich console
console = Console()

def create_comment_panel(comment_obj, index, is_reply=False):
    """Helper function to create a comment panel with nested replies"""
    # Extract comment data
    comment_text = comment_obj.get('commentary', {}).get('text', {})
    commenter = comment_obj.get('commenter', {})
    comment_author = commenter.get('title', {}).get('text', "Unknown")
    comment_profile_url = commenter.get('navigationUrl', "")
    comment_headline = commenter.get('subtitle', "")
    
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
    
    # Get replies for this comment
    reply_panels = []
    social_detail_urn = comment_obj.get('*socialDetail')
    if social_detail_urn:
        social_detail = index.get(social_detail_urn)
        if social_detail and social_detail.get('comments'):
            reply_urns = social_detail.get('comments', {}).get('*elements', [])
            for reply_urn in reply_urns:
                reply_obj = index.get(reply_urn)
                if reply_obj:
                    reply_panel = create_comment_panel(reply_obj, index, is_reply=True)
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

for urn in activities:
    item = index.get(urn)
    if not item or item.get('$type') != 'com.linkedin.voyager.dash.feed.Update':
        continue

    # --- 1. THE ACTION & REACTION TYPE ---
    header_text = item.get('header', {}).get('text', {}).get('text', "")

    # --- 2. THE ORIGINAL POST TEXT ---
    # In a reaction update, the original post text is often in 'commentary'
    # or inside 'resharedUpdate' if they reacted to a share.
    post_text = "No text content"
    if item.get('commentary'):
        post_text = item['commentary'].get('text', {}).get('text', "")
    
    # --- 3. THE ORIGINAL AUTHOR ---
    # We look for the 'actor' URN and find their name in our index
    author_name = "Unknown Author"
    author_headline = ""
    actor = item.get('actor')
    if actor:
        author_name = actor.get("name", {}).get("text", "Unknown Author")
        author_headline = actor.get("description", {}).get("text", "")

    # --- 4. THE URL ---
    post_url = item.get('socialContent', {}).get('shareUrl') or item.get('metadata', {}).get('shareUrl')

    # --- 5. EXTRACT COMMENTS WITH REPLIES ---
    highlightedComments = item.get('*highlightedComments', [])
    comment_panels = []
    
    if highlightedComments:
        for comment_urn in highlightedComments:
            comment_obj = index.get(comment_urn)
            if not comment_obj:
                continue
            
            # Create comment panel (which will recursively include replies)
            comment_panel = create_comment_panel(comment_obj, index, is_reply=False)
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
    content.append(f"{post_url}", style="blue underline")
    
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