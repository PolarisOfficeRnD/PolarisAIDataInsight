import mimetypes
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, Optional


class Blob(BaseModel):
    """
    Blob class to represent a file with its metadata.
    """

    data: bytes
    mimetype: str
    metadata: Dict[str, str]

    @classmethod
    def from_path(
        cls, path: str | Path, mime_type: str, metadata: Optional[Dict[str, str]] = None
    ) -> "Blob":
        with open(path, "rb") as f:
            data = f.read()
        return cls(data=data, mimetype=mime_type, metadata=metadata or {})

    @classmethod
    def from_data(
        cls, data: bytes, mime_type: str, metadata: Optional[Dict[str, str]] = None
    ) -> "Blob":
        return cls(data=data, mimetype=mime_type, metadata=metadata or {})


def determine_mime_type(filename: str) -> str:
    mime_type = mimetypes.guess_type(filename)[0]
    if mime_type is None:
        mime_type = "application/octet-stream"
    return mime_type
