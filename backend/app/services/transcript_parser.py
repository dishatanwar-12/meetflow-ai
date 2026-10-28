import io
import re
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader
import docx

class DocumentParseError(Exception):
    pass

class TranscriptParser:
    @staticmethod
    def parse_txt(file_bytes: bytes) -> str:
        """Decodes raw text bytes using utf-8 with fallback to latin-1."""
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return file_bytes.decode("latin-1")
            except Exception as e:
                raise DocumentParseError(f"Unable to decode text file: {str(e)}")

    @staticmethod
    def parse_pdf(file_bytes: bytes) -> str:
        """Extracts text from PDF bytes using pypdf. Detects empty/scanned PDFs."""
        try:
            stream = io.BytesIO(file_bytes)
            reader = PdfReader(stream)
            extracted_pages = []
            
            for idx, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    extracted_pages.append(text)
            
            full_text = "\n\n".join(extracted_pages).strip()
            if not full_text:
                raise DocumentParseError(
                    "The PDF contains no extractable text. It may be a scanned image. "
                    "Please paste or upload a machine-readable text transcript."
                )
            return full_text
        except DocumentParseError:
            raise
        except Exception as e:
            raise DocumentParseError(f"Failed to parse PDF document: {str(e)}")

    @staticmethod
    def parse_docx(file_bytes: bytes) -> str:
        """Extracts text from DOCX bytes using python-docx."""
        try:
            stream = io.BytesIO(file_bytes)
            doc = docx.Document(stream)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            
            # Also extract text from tables if present
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        paragraphs.append(row_text)
                        
            full_text = "\n\n".join(paragraphs).strip()
            if not full_text:
                raise DocumentParseError("The DOCX document is empty or contains no readable text.")
            return full_text
        except DocumentParseError:
            raise
        except Exception as e:
            raise DocumentParseError(f"Failed to parse DOCX document: {str(e)}")

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalizes transcript text without altering vocabulary, numbers, or punctuation.
        Standardizes line breaks, removes carriage returns, and strips excessive blank lines.
        """
        if not text:
            return ""
        # Standardize line breaks
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Replace non-breaking spaces
        text = text.replace("\u00a0", " ")
        # Strip excessive consecutive blank lines (> 2)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @staticmethod
    def extract_speakers(text: str) -> List[str]:
        """
        Scans transcript for speaker labels (e.g., 'Alex:', 'Speaker 1:', '[Sarah]', '<Bob>:').
        """
        patterns = [
            r"^([A-Z][a-zA-Z0-9_\s]{1,30}):\s",     # Alex: or Speaker 1:
            r"^\[([A-Z][a-zA-Z0-9_\s]{1,30})\]:\s",   # [Alex]:
            r"^<([A-Z][a-zA-Z0-9_\s]{1,30})>:\s",   # <Alex>:
        ]
        speakers = set()
        for line in text.split("\n"):
            line = line.strip()
            for pat in patterns:
                match = re.match(pat, line)
                if match:
                    speaker = match.group(1).strip()
                    if len(speaker) > 1 and not speaker.lower().startswith("http"):
                        speakers.add(speaker)
        return sorted(list(speakers))

    @staticmethod
    def chunk_transcript(text: str, max_chunk_chars: int = 12000, overlap_chars: int = 1000) -> List[Dict[str, Any]]:
        """
        Splits lengthy transcripts into overlapping windows to fit LLM context limits
        while preserving exact character offset locations for evidence traceability.
        """
        if len(text) <= max_chunk_chars:
            return [{"index": 0, "text": text, "start_char": 0, "end_char": len(text)}]

        chunks = []
        start = 0
        chunk_idx = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + max_chunk_chars, text_len)

            # If not at the very end, try to break at a paragraph or sentence boundary
            if end < text_len:
                boundary = text.rfind("\n\n", start, end)
                if boundary == -1 or boundary < start + (max_chunk_chars // 2):
                    boundary = text.rfind(". ", start, end)
                if boundary != -1 and boundary > start + (max_chunk_chars // 2):
                    end = boundary + 1

            chunk_text = text[start:end]
            chunks.append({
                "index": chunk_idx,
                "text": chunk_text,
                "start_char": start,
                "end_char": end
            })

            if end >= text_len:
                break

            start = max(end - overlap_chars, start + 1)
            chunk_idx += 1

        return chunks

