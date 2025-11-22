from sqlmodel import SQLModel, create_engine
from pathlib import Path
from models.models import ClipboardItem
import os

APP_NAME = "clippy_tui"
DB_DIR = Path.home() / ".local" / "share" / APP_NAME
DB_NAME = "clipboard.db"
DB_PATH = DB_DIR / DB_NAME

#ensuring the DB exists:
os.makedirs(DB_DIR, exist_ok=True)


#Connection URL
sqlite_url = f"sqlite:///{DB_PATH}"

#to remove TUI and Listener accessing DB at the same time, check_same_thread = False!!!!

engine = create_engine(sqlite_url, connect_args={"check_same_thread":False})

def init_db():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()

    print(f"Database initiliazed at: {DB_PATH}")

