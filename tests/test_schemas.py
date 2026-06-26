from pathlib import Path

import pytest
from pydantic import ValidationError

from schemas import ExtractedRecord, ReimbursementExtractionResult

ROOT = Path(__file__).resolve().parents[1]


def _contains_key(value, key: str) -> bool:
    if isinstance(value, dict):
        return key in value or any(_contains_key(item, key) for item in value.values())
    if isinstance(value, list):
        return any(_contains_key(item, key) for item in value)
    return False


def test_sample_result_validates():
    payload = (ROOT / "sample_data" / "sample_result.json").read_text(encoding="utf-8")

    result = ReimbursementExtractionResult.model_validate_json(payload)

    assert result.records
    assert "USD" in result.detected_currencies
    assert result.records[0].document_type == "invoice"
    assert result.extracted_totals_by_currency[0].currency == "CNY"


def test_schema_does_not_emit_additional_properties():
    schema = ReimbursementExtractionResult.model_json_schema()

    assert not _contains_key(schema, "additionalProperties")


def test_legacy_totals_dict_is_normalized_after_response():
    payload = (ROOT / "sample_data" / "sample_result.json").read_text(encoding="utf-8")
    data = ReimbursementExtractionResult.model_validate_json(payload).model_dump(mode="json")
    data["extracted_totals_by_currency"] = {"USD": 7.99, "CNY": 2136.0}

    result = ReimbursementExtractionResult.model_validate(data)

    assert result.extracted_totals_by_currency[0].currency == "USD"
    assert result.extracted_totals_by_currency[0].amount == 7.99


def test_invalid_document_type_is_rejected():
    with pytest.raises(ValidationError):
        ExtractedRecord(source_file="x.pdf", document_type="contract")
