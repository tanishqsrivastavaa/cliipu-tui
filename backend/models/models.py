from enum import Enum
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional

class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"

class ClipboardItem(SQLModel,table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content_type :  ContentType

    #files/images: path to file/cache
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

    #displaying preview snippet of text
    preview: Optional[str] = None