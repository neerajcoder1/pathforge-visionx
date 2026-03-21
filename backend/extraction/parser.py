"""Document parsing and OCR triage for resume ingestion."""

from __future__ import annotations

import io
import math
from typing import Tuple

import pdfplumber
import pytesseract


def _extract_with_pdfplumber(file_bytes: bytes) -> str:
	"""Extract text quickly from PDF text layers."""
	text_chunks: list[str] = []
	with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
		for page in pdf.pages:
			page_text = page.extract_text() or ""
			if page_text.strip():
				text_chunks.append(page_text.strip())
	return "\n".join(text_chunks).strip()


def _extract_with_ocr(file_bytes: bytes) -> str:
	"""Fallback OCR extraction using pypdfium2-rendered page bitmaps."""
	try:
		import pypdfium2 as pdfium
	except Exception:
		return ""

	ocr_chunks: list[str] = []
	pdf = pdfium.PdfDocument(io.BytesIO(file_bytes))
	for idx in range(len(pdf)):
		page = pdf[idx]
		# Scale renders at ~300 DPI for better OCR quality.
		bitmap = page.render(scale=300 / 72)
		pil_image = bitmap.to_pil()
		text = pytesseract.image_to_string(pil_image) or ""
		if text.strip():
			ocr_chunks.append(text.strip())
	return "\n".join(ocr_chunks).strip()


def document_triage(file_bytes: bytes) -> Tuple[str, str]:
	"""Return extracted text and extraction method.

	If pdfplumber extraction yields fewer than 100 characters, OCR is used.
	The returned text is prefixed with "ocr_sourced: true" when OCR is chosen.
	"""
	text = _extract_with_pdfplumber(file_bytes)
	if len(text) >= 100:
		return text, "pdfplumber"

	ocr_text = _extract_with_ocr(file_bytes)
	if ocr_text:
		return f"ocr_sourced: true\n{ocr_text}", "ocr"

	# Keep the contract deterministic even when OCR dependencies/system binary fail.
	fallback_text = text if text else "ocr_sourced: true"
	return fallback_text, "ocr"
