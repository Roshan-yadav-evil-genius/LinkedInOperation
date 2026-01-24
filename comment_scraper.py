"""Main script to scrape and display LinkedIn comments data."""

from parsers.factory import LinkedInDataParser
from models.comment import CommentParser
from models.update import UpdateParser
from ui.display import LinkedInDisplay


def main():
    """Main function to parse and display LinkedIn comments."""
    # Parse Updates (posts) from comment.json
    # comment.json contains Updates where the user commented, not Comments directly
    parser = LinkedInDataParser.from_file("comment.json")
    elements = parser._get_elements()
    
    # Parse Updates and Comments
    update_parser = UpdateParser(parser.index)
    comment_parser = CommentParser(parser.index)
    updates = update_parser.parse_list(elements)
    
    # Initialize display
    display = LinkedInDisplay()
    
    # Display each post (Update) with its comments nested inside
    # This creates the LinkedIn-like structure: Post → Comments → Replies (recursive)
    for update in updates:
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
