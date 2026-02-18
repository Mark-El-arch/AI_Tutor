from pathlib import Path
from urllib.parse import urlparse


class MaterialProcessor:
    """Normalizes uploaded study material into title + content for tutoring."""

    TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".py", ".rst"}
    SLIDE_EXTENSIONS = {".ppt", ".pptx", ".pdf"}
    AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a"}
    VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}

    def process(self, source_type: str, payload: str, title: str | None = None) -> dict:
        source_type = source_type.strip().lower()

        if source_type == "raw_text":
            return {
                "title": title or "Uploaded Notes",
                "content": payload.strip(),
                "source_type": source_type,
            }

        if source_type == "file":
            return self._process_file(payload, title)

        if source_type == "web_link":
            return self._process_link(payload, title)

        raise ValueError("Unsupported source_type. Use raw_text, file, or web_link.")

    def _process_file(self, file_path: str, title: str | None = None) -> dict:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        ext = path.suffix.lower()
        material_title = title or path.stem

        if ext in self.TEXT_EXTENSIONS:
            content = path.read_text(encoding="utf-8", errors="ignore")
            return {"title": material_title, "content": content, "source_type": "text_file"}

        if ext in self.SLIDE_EXTENSIONS:
            return {
                "title": material_title,
                "content": (
                    "Slides were uploaded. Please provide extracted text or speaker notes so the tutor "
                    "can explain the material and generate accurate quizzes/flashcards."
                ),
                "source_type": "slides_file",
            }

        if ext in self.AUDIO_EXTENSIONS | self.VIDEO_EXTENSIONS:
            return {
                "title": material_title,
                "content": (
                    "Audio/video was uploaded. Automatic transcription is not configured yet. "
                    "Please paste a transcript to continue tutoring."
                ),
                "source_type": "media_file",
            }

        raise ValueError(f"Unsupported file type: {ext}")

    def _process_link(self, link: str, title: str | None = None) -> dict:
        parsed = urlparse(link)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Only http(s) links are supported.")

        host = parsed.netloc.lower()
        material_title = title or f"Web Material from {host}"

        return {
            "title": material_title,
            "content": (
                f"Study material link: {link}. "
                "Please provide the transcript or key notes from the link so the tutor can explain and quiz accurately."
            ),
            "source_type": "web_link",
        }
