"""Regression coverage for caller mutation and cache LRU isolation."""

import pytest

from fastdocparse.cache import InMemoryCache


def test_cache_set_copies_nested_input():
    cache = InMemoryCache()
    result = {"field": {"flags": ["grounded"], "value": [1, 2]}}
    cache.set("doc", result)
    result["field"]["flags"].append("later")
    result["field"]["value"][0] = 99
    assert cache.get("doc") == {"field": {"flags": ["grounded"], "value": [1, 2]}}


def test_cache_get_returns_isolated_nested_copy():
    cache = InMemoryCache()
    cache.set("doc", {"field": {"flags": ["grounded"], "value": [1, 2]}})
    first = cache.get("doc")
    first["field"]["flags"].clear()
    first["field"]["value"].append(3)
    assert cache.get("doc") == {"field": {"flags": ["grounded"], "value": [1, 2]}}


def test_cache_lru_eviction_after_read():
    cache = InMemoryCache(max_size=2)
    cache.set("a", {"value": 1})
    cache.set("b", {"value": 2})
    assert cache.get("a") == {"value": 1}
    cache.set("c", {"value": 3})
    assert cache.get("b") is None
    assert cache.get("a") == {"value": 1}
    assert cache.get("c") == {"value": 3}


def test_cache_rejects_nonpositive_limit():
    for limit in (0, -1):
        with pytest.raises(ValueError):
            InMemoryCache(max_size=limit)
