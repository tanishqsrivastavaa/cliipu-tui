import subprocess
import uuid
import sys
from pathlib import Path
from sqlmodel import Session
from database import engine, APP_NAME
from models.models import ClipboardItem, ContentType

#Path: ~/.cache/clippy_tui/images/
CACHE_DIR = Path.home() / ".cache" / APP_NAME / "images"
CACHE_DIR.mkdir(parents=True,exist_ok=True)

def get_clipboard_data():
    
    try:
        result = subprocess.check_output(["wl-paste","--list-types"],text=True)
        mimes = result.splitlines()

    except subprocess.CalledProcessError:
        return None,None

    #Images : Priority 1
    if "image/png" in mimes:
        try:
            image_bytes = subprocess.check_output(["wl-paste","--type","image/png"])

            filename = f"{uuid.uuid4()}.png"
            file_path = CACHE_DIR / filename

            with open(file_path,"wb") as f:
                f.write(image_bytes)

            return ContentType.IMAGE, str(file_path)
        except Exception as e:
            print(f"Error saving image: {e}")
            return None,None

    #text/uri-list : Priority 2
    elif "text/uri-list" in mimes:
        content = subprocess.check_output(["wl-paste","--type","text/uri-list"],text=True)
        return ContentType.FILE, content.strip()


    elif "text/plain" in mimes or "text/plain;charset=utf-8" in mimes:
        content = subprocess.check_output(["wl-paste","--type","text/plain"],text=True)

    return None,None


def save_to_db():
    c_type, c_content = get_clipboard_data()

    if not c_type or not c_content:
        return


    item = ClipboardItem(
        content_type = c_type,
        content = c_content
    )

    with Session(engine) as session:
        session.add(item)
        session.commit()
        print(f"Saved [{c_type}]: {c_content[:50]}...")

if __name__ == "__main__":
    save_to_db()