"""Extracts plain text from uploaded attachments so it can be appended to
the transcript before it reaches the prompt (Camino B).

Kept deliberately simple: only .pdf and .txt/.md are supported for now.
Anything else raises a clear error rather than silently skipping content
the user expects to be considered.
"""

import io
from fastapi import UploadFile
from pypdf import PdfReader
from pypdf.errors import PdfReadError

def _extract_pdf_text(data: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(data))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except PdfReadError as exc:
        raise ValueError(f"Could not read PDF: {exc}") from exc

    if not text.strip():
        raise ValueError(
            "PDF has no extractable text (likely a scanned/image-only document)"
        )
    return text

async def _extract_text(file: UploadFile) -> str:
    data = await file.read()
    filename = file.filename or "attachment"

    if filename.lower().endswith(".pdf"):
        return _extract_pdf_text(data)
    if filename.lower().endswith((".txt", ".md")):
        return data.decode("utf-8", errors="replace")

    raise ValueError(f"Unsupported attachment type: {filename}")

async def build_transcript(transcript: str, attachments: list[UploadFile] | None) -> str:
    if not attachments:
        return transcript

    parts=[transcript]
    for file in attachments:
        text = await _extract_text(file)
        parts.append(f"--- attachment: {file.filename} --- \n{text}")

    return "\n\n".join(parts)