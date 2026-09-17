from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from fastdocparse.cli import app
from fastdocparse.config import ExtractionConfig

runner = CliRunner()
REPO_ROOT = Path(__file__).parent.parent
SAMPLE_IMAGE = REPO_ROOT / "sample_invoice.png"
INVOICE_SCHEMA_PATH = REPO_ROOT / "src" / "fastdocparse" / "schemas" / "invoice.json"


def test_extract_command_passes_all_tuning_flags_to_document_parser() -> None:
    fake_result = {
        "_meta": {"truncated": False, "truncation_reason": None},
        "invoice_number": {"value": "INV-1", "confidence": "high", "flags": ["grounded"]},
    }
    args = [
        "extract",
        str(SAMPLE_IMAGE),
        str(INVOICE_SCHEMA_PATH),
        "--api-key",
        "test-key",
        "--max-pages",
        "7",
        "--chunk-max-tokens",
        "2048",
        "--pdf-render-dpi",
        "200",
        "--max-image-dim",
        "1024",
        "--ocr-min-confidence",
        "0.75",
        "--max-concurrent-chunks",
        "4",
    ]

    with patch("fastdocparse.cli.DocumentParser") as parser_cls, patch(
        "fastdocparse.cli.LLMClient"
    ):
        parser_cls.return_value.extract.return_value = fake_result
        result = runner.invoke(app, args)

    assert result.exit_code == 0
    config = parser_cls.call_args.kwargs["config"]
    assert config == ExtractionConfig(
        max_pages=7,
        chunk_max_tokens=2048,
        pdf_render_dpi=200,
        max_image_dim=1024,
        ocr_min_confidence=0.75,
        max_concurrent_chunks=4,
    )


@pytest.mark.parametrize(
    ("flag", "value", "message"),
    [
        ("--chunk-max-tokens", "0", "chunk_max_tokens must be positive"),
        ("--pdf-render-dpi", "0", "pdf_render_dpi must be positive"),
        ("--max-image-dim", "0", "max_image_dim must be positive"),
        ("--ocr-min-confidence", "2.0", "ocr_min_confidence must be between 0 and 1"),
        ("--max-concurrent-chunks", "0", "max_concurrent_chunks must be positive"),
    ],
)
def test_extract_command_reports_invalid_tuning_flags_cleanly(
    flag: str, value: str, message: str
) -> None:
    result = runner.invoke(
        app,
        [
            "extract",
            str(SAMPLE_IMAGE),
            str(INVOICE_SCHEMA_PATH),
            flag,
            value,
            "--api-key",
            "test-key",
        ],
    )

    assert result.exit_code == 1
    assert message in result.output
    assert "Traceback" not in result.output
