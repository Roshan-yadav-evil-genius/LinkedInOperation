"""Main script to scrape and display LinkedIn posts data."""

from parsers.factory import LinkedInDataParser
from models.comment import CommentParser
from ui.display import LinkedInDisplay


def main():
    """Main function to parse and display LinkedIn posts."""
    # Parse posts using the new typed classes
    parser = LinkedInDataParser.from_file("posts.json")
    posts_response = parser.parse_posts()
    comment_parser = CommentParser(parser.index)
    
    # Initialize display
    display = LinkedInDisplay()
    
    # Process each post (Update) and display it with nested comments
    for update in posts_response.updates:
        # Skip if not a valid Update
        if not update:
            continue
        
        # Create and display the update panel
        # create_update_panel() automatically handles:
        # - Post display (author, content, metadata)
        # - Nested comments from update.highlighted_comments
        # - Recursive replies (via create_comment_panel())
        panel = display.create_update_panel(update, parser.index, comment_parser)
        display.display_update(panel)


if __name__ == "__main__":
    main()
