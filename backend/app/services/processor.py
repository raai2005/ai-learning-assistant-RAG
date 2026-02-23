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
    from youtube_transcript_api import YouTubeTranscriptApiException
    
    video_id = extract_video_id(url)
    try:
        api = YouTubeTranscriptApi()
        # Get all available transcripts
        transcript_list = api.list(video_id)
        
        try:
            # Try to find English first (manually created or generated)
            transcript_obj = transcript_list.find_transcript(['en'])
        except Exception:
            # Fallback: Just take the first one ever available
            try:
                transcript_obj = next(iter(transcript_list))
            except StopIteration:
                raise ValueError("No transcripts are available for this video.")
            
        fetched = transcript_obj.fetch()
        transcript_text = " ".join([snippet.text for snippet in fetched])
        return transcript_text
    except YouTubeTranscriptApiException as e:
        # This catches general API errors (e.g. video unavailable, blocked, etc.)
        raise ValueError(f"YouTube Transcript API error: {str(e)}")
    except ValueError as e:
        # Pass through our own ValueErrors (like "No transcripts available")
        raise e
    except Exception as e:
        raise ValueError(f"An unexpected error occurred while fetching transcript: {str(e)}")


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
    text: str, chunk_size: int = 1000, chunk_overlap: int = 250
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
