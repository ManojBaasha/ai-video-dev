"""Tests for color grade loading and application."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.grades import list_grades, load_grade


def test_list_grades_returns_results():
    grades = list_grades()
    assert len(grades) > 0


def test_all_grades_have_names():
    grades = list_grades()
    for name in grades:
        assert isinstance(name, str)
        assert len(name) > 0


def test_load_grade_by_exact_name():
    grades = list_grades()
    grade = load_grade(grades[0])
    assert "name" in grade
    assert "filter_chain" in grade
    assert len(grade["filter_chain"]) > 0


def test_load_grade_partial_match():
    # "neon rain" should match "Neon Rain - Night City"
    grade = load_grade("neon rain")
    assert "Neon Rain" in grade["name"]


def test_load_grade_case_insensitive():
    grade = load_grade("STEEL BLUE")
    assert "Steel Blue" in grade["name"]


def test_load_grade_filter_chain_is_valid_ffmpeg():
    """Filter chain should not contain newlines or obvious syntax errors."""
    for name in list_grades():
        grade = load_grade(name)
        fc = grade["filter_chain"]
        assert "\n" not in fc, f"Filter chain for '{name}' contains newline"
        assert len(fc) > 20, f"Filter chain for '{name}' seems too short"


def test_load_grade_unknown_raises():
    with pytest.raises(ValueError, match="not found"):
        load_grade("this grade does not exist xyz123")
