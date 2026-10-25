"""Regression cases for JSON responses containing nested objects and prose."""

import pytest

from fastdocparse.json_repair import parse_json_from_llm


@pytest.mark.parametrize(
    "response, expected",
    [
        ('{"field": {"nested": 1}, "total": 2}', {"field": {"nested": 1}, "total": 2}),
        ('prefix {"field": {"nested": 1}, "total": 2} suffix', {"field": {"nested": 1}, "total": 2}),
        ('{"description": "literal {brace} and }", "n": 1}', {"description": "literal {brace} and }", "n": 1}),
        ('```json\n{"outer": {"inner": 1}}\n```', {"outer": {"inner": 1}}),
        ('```json\n[1,2]\n``` then {"good": 3}', {"good": 3}),
        ('{"invoice_number":"INV-1", "total_price":', {"invoice_number": "INV-1"}),
        ('{"invoice_number":"INV-1", "line_items":[{"name":"Widget","qty":5', {"invoice_number": "INV-1", "line_items": [{"name": "Widget", "qty": 5}]}),
        ("no JSON in this answer", {}),
    ],
)
def test_json_parser_prefers_outer_object(response, expected):
    assert parse_json_from_llm(response) == expected
