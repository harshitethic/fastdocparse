"""Extraction parameter boundary and type validation."""

import math

import pytest

from fastdocparse.config import ExtractionConfig


@pytest.mark.parametrize(
    "field",
    ["max_pages", "chunk_max_tokens", "pdf_render_dpi", "max_image_dim", "max_concurrent_chunks"],
)
@pytest.mark.parametrize("value", [True, 0.5, float("nan"), float("inf")])
def test_integer_config_rejects_nonintegers(field, value):
    with pytest.raises((ValueError, TypeError)):
        ExtractionConfig(**{field: value})


@pytest.mark.parametrize("value", [float("nan"), math.inf, -math.inf, -0.1, 1.1])
def test_ocr_confidence_rejects_nonfinite_out_of_range(value):
    with pytest.raises(ValueError):
        ExtractionConfig(ocr_min_confidence=value)


@pytest.mark.parametrize("value", [0, 0.3, 1])
def test_ocr_confidence_accepts_finite_boundaries(value):
    assert ExtractionConfig(ocr_min_confidence=value).ocr_min_confidence == value
