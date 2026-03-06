from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Static
from textual.containers import Horizontal, Vertical
from textual import on, work
from rich.syntax import Syntax
from rich.text import Text

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0,str(project_root))

# Import our database tools
from sqlmodel import Session, select, desc
from backend.database import engine
from backend.models.models import ClipboardItem, ContentType
import subprocess

class ClipboardWidget(ListItem):
    """A custom list item to show a snippet of the clipboard content."""
    def __init__(self, item: ClipboardItem) -> None:
        super().__init__()
        self.db_item = item
        
    def compose(self) -> ComposeResult:
        # Show an icon based on type
        icon = "📄" if self.db_item.content_type == ContentType.TEXT else \
               "🖼️" if self.db_item.content_type == ContentType.IMAGE else "📁"
        
        # Show the first 30 chars of content or the filename
        display_text = self.db_item.content.replace("\n", " ")[:30]
        yield Label(f"{icon} {display_text}...")

class ClippyTUI(App):
    """The Main TUI Application."""
    
    CSS = """
    Screen {
        layout: horizontal;
    }
    
    #sidebar {
        width: 30%;
        height: 100%;
        border-right: solid $accent;
        background: $surface;
    }
    
    #preview_area {
        width: 70%;
        height: 100%;
        padding: 1 2;
    }
    
    ListView {
        height: 100%;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("enter", "select", "Paste Selection"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            # Left: The List
            with Vertical(id="sidebar"):
                yield Label(" 📋 History", classes="header")
                yield ListView(id="history_list")
            
            # Right: The Preview
            with Vertical(id="preview_area"):
                yield Static(id="preview_content", expand=True)
        yield Footer()

    def on_mount(self) -> None:
        """Runs when the app starts. Loads data from DB."""
        self.load_history()

    def load_history(self):
        """Queries SQLite and populates the list."""
        list_view = self.query_one("#history_list", ListView)
        
        with Session(engine) as session:
            # Get items, newest first
            statement = select(ClipboardItem).order_by(desc(ClipboardItem.id)).limit(50)
            results = session.exec(statement).all()
            
            for item in results:
                list_view.append(ClipboardWidget(item))
                
        # Focus the list immediately so keyboard works
        list_view.focus()

    @on(ListView.Highlighted)
    def update_preview(self, event: ListView.Highlighted):
        """When user moves selection up/down, update the right panel."""
        if not event.item:
            return

        item = event.item.db_item # Access the data we stored in the widget
        preview_widget = self.query_one("#preview_content", Static)

        if item.content_type == ContentType.TEXT:
            # Use Rich Syntax Highlighting for code/text
            syntax = Syntax(item.content, "python", theme="monokai", line_numbers=True, word_wrap=True)
            preview_widget.update(syntax)
            
        elif item.content_type == ContentType.IMAGE:
            # For now, just show the path. We can add image rendering later.
            preview_widget.update(f"\n\n   🖼️  Image stored at:\n   {item.content}\n\n   (Press Enter to paste)")
            
        elif item.content_type == ContentType.FILE:
            preview_widget.update(f"\n\n   📁  File Reference:\n   {item.content}\n\n   (Press Enter to paste)")

    @on(ListView.Selected)
    def on_paste(self, event: ListView.Selected):
        """When user hits Enter."""
        item = event.item.db_item
        self.inject_to_clipboard(item)
        self.exit() # Close the app after pasting

    def inject_to_clipboard(self, item: ClipboardItem):
        """The Logic to push data back to the OS clipboard."""
        try:
            if item.content_type == ContentType.TEXT:
                subprocess.run(["wl-copy"], input=item.content.encode("utf-8"))
                
            elif item.content_type == ContentType.FILE:
                # wl-copy expects the MIME type for files
                subprocess.run(["wl-copy", "--type", "text/uri-list"], input=item.content.encode("utf-8"))
                
            elif item.content_type == ContentType.IMAGE:
                # Read the image file and pipe it to wl-copy
                with open(item.content, "rb") as f:
                    subprocess.run(["wl-copy", "--type", "image/png"], stdin=f)
                    
        except Exception as e:
            self.notify(f"Error pasting: {e}", severity="error")

if __name__ == "__main__":
    app = ClippyTUI()
    app.run()