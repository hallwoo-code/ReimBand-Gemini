from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable, Optional

from dotenv import load_dotenv
from pydantic import ValidationError

from file_utils import UploadedDocument, write_temp_upload
from schemas import ReimbursementExtractionResult

PROJECT_ROOT = Path(__file__).resolve().parent
PROMPT_PATH = PROJECT_ROOT / "prompts" / "document_extraction.md"
DEFAULT_MODEL = "gemini-2.5-flash"


class GeminiNotConfigured(RuntimeError):
    pass


class GeminiExtractionError(RuntimeError):
    pass


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def configured_model(secrets: Optional[dict] = None) -> str:
    load_dotenv()
    if secrets and secrets.get("GEMINI_MODEL"):
        return str(secrets["GEMINI_MODEL"])
    return os.getenv("GEMINI_MODEL", DEFAULT_MODEL)


def configured_api_key(secrets: Optional[dict] = None) -> Optional[str]:
    load_dotenv()
    if secrets and secrets.get("GEMINI_API_KEY"):
        return str(secrets["GEMINI_API_KEY"])
    return os.getenv("GEMINI_API_KEY")


def _safe_json_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    return text.strip()


def _validate_response(response) -> ReimbursementExtractionResult:
    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, ReimbursementExtractionResult):
        return parsed
    if isinstance(parsed, dict):
        return ReimbursementExtractionResult.model_validate(parsed)

    text = getattr(response, "text", "")
    if not text:
        raise GeminiExtractionError("Gemini returned an empty response.")
    return ReimbursementExtractionResult.model_validate_json(_safe_json_text(text))


def _looks_like_schema_subset_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "additionalproperties" in message or "response_schema" in message or "schema" in message


def extract_reimbursement(uploaded_documents: Iterable[UploadedDocument], api_key: Optional[str] = None, model: str = DEFAULT_MODEL) -> ReimbursementExtractionResult:
    api_key = api_key or configured_api_key()
    if not api_key:
        raise GeminiNotConfigured("GEMINI_API_KEY is not configured.")

    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise GeminiExtractionError("google-genai is not installed. Run pip install -r requirements.txt.") from exc

    client = genai.Client(api_key=api_key)
    documents = list(uploaded_documents)
    filenames = [doc.name for doc in documents]
    content_parts: list[object] = [load_prompt(), "Source filenames: " + json.dumps(filenames)]
    uploaded_file_refs: list[object] = []
    temp_paths: list[Path] = []

    try:
        for doc in documents:
            if doc.requires_files_api:
                temp_path = write_temp_upload(doc)
                temp_paths.append(temp_path)
                file_ref = client.files.upload(file=str(temp_path))
                uploaded_file_refs.append(file_ref)
                content_parts.append(file_ref)
            else:
                content_parts.append(types.Part.from_bytes(data=doc.data, mime_type=doc.mime_type))

        try:
            response = client.models.generate_content(
                model=model,
                contents=content_parts,
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                    response_schema=ReimbursementExtractionResult,
                ),
            )
        except Exception as exc:
            if not _looks_like_schema_subset_error(exc):
                raise
            response = client.models.generate_content(
                model=model,
                contents=content_parts + [
                    "Return only valid JSON matching the required schema. Do not include Markdown fences or explanatory text."
                ],
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                ),
            )

        return _validate_response(response)
    except ValidationError as exc:
        raise GeminiExtractionError(f"Gemini response did not match the expected schema: {exc}") from exc
    except Exception as exc:
        if isinstance(exc, GeminiExtractionError):
            raise
        raise GeminiExtractionError(f"Gemini extraction failed safely: {exc}") from exc
    finally:
        for file_ref in uploaded_file_refs:
            name = getattr(file_ref, "name", None)
            if name:
                try:
                    client.files.delete(name=name)
                except Exception:
                    pass
        for temp_path in temp_paths:
            try:
                temp_path.unlink(missing_ok=True)
            except Exception:
                pass
