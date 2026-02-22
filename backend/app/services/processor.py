import io

from youtube_transcript_api import YouTubeTranscriptApi
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_video_id(url: str) -> str:
    """Extract the video ID from a YouTube URL."""
    import re

    patterns = [
        r"(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from URL: {url}")


def get_youtube_transcript(url: str) -> str:
    """Fetch the transcript of a YouTube video."""
    video_id = extract_video_id(url)
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    transcript_text = " ".join([entry["text"] for entry in transcript_list])
    return transcript_text


def get_youtube_title(url: str) -> str:
    """Get a simple title from the video ID."""
    video_id = extract_video_id(url)
    return f"YouTube Video ({video_id})"


def extract_pdf_text(file_bytes: bytes) -> tuple[str, int]:
    """Extract text from PDF bytes. Returns (text, page_count)."""
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = len(reader.pages)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip(), pages


def chunk_text(
    text: str, chunk_size: int = 1000, chunk_overlap: int = 200
) -> list[str]:
    """Split text into overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(text)
    return chunks
