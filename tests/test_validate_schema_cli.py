"""Regression coverage for the validate-schema CLI command."""

import json

from typer.testing import CliRunner

from fastdocparse.cli import app


runner = CliRunner()


def test_validate_schema_accepts_valid_schema_without_llm_credentials(tmp_path):
    schema_path = tmp_path / "invoice.json"
    schema_path.write_text(
        json.dumps(
            {
                "name": "Invoice",
                "fields": [
                    {
                        "name": "invoice_number",
                        "description": "Invoice identifier",
                        "type": "text",
                    }
                ],
                "examples": [["Invoice 42", {"invoice_number": "42"}]],
            }
        )
    )

    result = runner.invoke(
        app,
        ["validate-schema", str(schema_path)],
        env={"LLM_API_KEY": "", "OPENAI_API_KEY": "", "FASTDOCPARSE_BASE_URL": ""},
    )

    assert result.exit_code == 0
    assert "Schema 'Invoice' is valid: 1 field, 1 example." in result.output


def test_validate_schema_reports_existing_schema_validation_errors(tmp_path):
    schema_path = tmp_path / "invalid.json"
    schema_path.write_text(
        json.dumps(
            {
                "name": "Invalid",
                "fields": [
                    {
                        "name": "_meta",
                        "description": "Reserved output metadata field",
                        "type": "text",
                    }
                ],
            }
        )
    )

    result = runner.invoke(app, ["validate-schema", str(schema_path)])

    assert result.exit_code == 1
    assert f"Could not load schema from {schema_path}" in result.output
    assert "reserved field name" in result.output
