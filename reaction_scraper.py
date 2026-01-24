"""Main script to scrape and display LinkedIn reactions data."""

from parsers.factory import LinkedInDataParser
from models.comment import CommentParser
from ui.display import LinkedInDisplay


def main():
    """Main function to parse and display LinkedIn reactions."""
    # Parse reactions using the new typed classes
    parser = LinkedInDataParser.from_file("reaction.json")
    reactions_response = parser.parse_reactions()
    comment_parser = CommentParser(parser.index)
    
    # Initialize display
    display = LinkedInDisplay()
    
    # Process each update and display it
    for update in reactions_response.updates:
        # Skip if not a valid Update
        if not update:
            continue
        
        # Create and display the update panel
        panel = display.create_update_panel(update, parser.index, comment_parser)
        display.display_update(panel)


if __name__ == "__main__":
    main()
