from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class DocumentType(str, Enum):
    INVOICE = "invoice"
    RECEIPT = "receipt"
    BANK_STATEMENT = "bank_statement"
    PAYMENT_PROOF = "payment_proof"
    WECHAT_TRANSFER = "wechat_transfer"
    TRAVEL_DOCUMENT = "travel_document"
    SUPPORTING_DOCUMENT = "supporting_document"
    UNKNOWN = "unknown"


class CurrencyTotal(BaseModel):
    currency: str = Field(..., description="Currency code or visible currency symbol.")
    amount: float = Field(..., description="Total amount for this currency.")

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        cleaned = value.strip()
        return cleaned.upper() if cleaned else cleaned


class ExtractedRecord(BaseModel):
    source_file: str = Field(..., description="Original uploaded filename for this record.")
    page_or_item: Optional[str] = Field(default=None, description="Page, table row, item, or visual region if known.")
    document_type: DocumentType = Field(..., description="Best supported document type classification.")
    invoice_number: Optional[str] = None
    document_date: Optional[str] = Field(default=None, description="Date as shown in the document, preferably ISO-8601 if clear.")
    amount: Optional[float] = Field(default=None, description="Monetary amount exactly extracted from the document.")
    currency: Optional[str] = Field(default=None, description="Currency code or symbol exactly supported by visible evidence.")
    seller_or_counterparty: Optional[str] = None
    payment_reference: Optional[str] = None
    payment_proof_found: bool = False
    layout_summary: Optional[str] = None
    uncertain_fields: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    @field_validator("currency")
    @classmethod
    def normalize_optional_currency(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned.upper() if cleaned else None


class ReimbursementExtractionResult(BaseModel):
    source_files: List[str] = Field(default_factory=list)
    document_summary: str = ""
    records: List[ExtractedRecord] = Field(default_factory=list)
    detected_document_types: List[str] = Field(default_factory=list)
    detected_currencies: List[str] = Field(default_factory=list)
    claimed_total_from_filename: Optional[float] = None
    claimed_currency_from_filename: Optional[str] = None
    extracted_totals_by_currency: List[CurrencyTotal] = Field(default_factory=list)
    payment_proof_found: bool = False
    layout_observations: List[str] = Field(default_factory=list)
    uncertain_fields: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    recommended_review_action: str = "human_review"

    @field_validator("extracted_totals_by_currency", mode="before")
    @classmethod
    def normalize_extracted_totals(cls, values):
        if values is None:
            return []
        if hasattr(values, "items"):
            return [{"currency": str(currency), "amount": amount} for currency, amount in values.items()]
        return values
    @field_validator("detected_currencies")
    @classmethod
    def normalize_detected_currencies(cls, values: List[str]) -> List[str]:
        normalized: List[str] = []
        for value in values:
            cleaned = value.strip().upper()
            if cleaned and cleaned not in normalized:
                normalized.append(cleaned)
        return normalized

    @field_validator("detected_document_types")
    @classmethod
    def normalize_document_types(cls, values: List[str]) -> List[str]:
        normalized: List[str] = []
        for value in values:
            cleaned = value.strip().lower()
            if cleaned and cleaned not in normalized:
                normalized.append(cleaned)
        return normalized
