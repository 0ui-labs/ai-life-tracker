"""Tests for the Entry Service - Tracker categorization and data management."""

import pytest

from app.services.entry import get_category_for_tracker, TRACKER_CATEGORIES


class TestTrackerCategorization:
    """Tests for automatic tracker category detection."""

    # =========================================================================
    # Fitness Category
    # =========================================================================

    def test_bankdruecken_is_categorized_as_fitness(self):
        """German exercise name should be detected as fitness."""
        assert get_category_for_tracker("bankdrücken") == "fitness"

    def test_bench_press_is_categorized_as_fitness(self):
        """English exercise name should be detected as fitness."""
        assert get_category_for_tracker("bench press") == "fitness"

    def test_kniebeugen_is_categorized_as_fitness(self):
        """Squats in German should be fitness."""
        assert get_category_for_tracker("Kniebeugen") == "fitness"

    def test_kreuzheben_is_categorized_as_fitness(self):
        """Deadlift in German should be fitness."""
        assert get_category_for_tracker("Kreuzheben") == "fitness"

    def test_pull_ups_is_categorized_as_fitness(self):
        """Pull-ups should be fitness."""
        assert get_category_for_tracker("pull-ups") == "fitness"

    def test_laufen_is_categorized_as_fitness(self):
        """Running in German should be fitness."""
        assert get_category_for_tracker("Laufen") == "fitness"

    # =========================================================================
    # Health Category
    # =========================================================================

    def test_gewicht_is_categorized_as_health(self):
        """Body weight tracking should be health."""
        assert get_category_for_tracker("Gewicht") == "health"

    def test_sleep_tracker_is_categorized_as_health(self):
        """Sleep tracking should be health."""
        assert get_category_for_tracker("Sleep Tracker") == "health"

    def test_schlaf_is_categorized_as_health(self):
        """German sleep should be health."""
        assert get_category_for_tracker("Schlaf") == "health"

    def test_wasser_is_categorized_as_health(self):
        """Water intake should be health."""
        assert get_category_for_tracker("Wasser trinken") == "health"

    def test_blutdruck_is_categorized_as_health(self):
        """Blood pressure should be health."""
        assert get_category_for_tracker("Blutdruck") == "health"

    # =========================================================================
    # Habit Category
    # =========================================================================

    def test_meditation_is_categorized_as_habit(self):
        """Meditation should be a habit."""
        assert get_category_for_tracker("Meditation") == "habit"

    def test_lesen_is_categorized_as_habit(self):
        """Reading in German should be habit."""
        assert get_category_for_tracker("Lesen") == "habit"

    def test_reading_is_categorized_as_habit(self):
        """Reading in English should be habit."""
        assert get_category_for_tracker("Daily Reading") == "habit"

    # =========================================================================
    # Default/General Category
    # =========================================================================

    def test_unknown_tracker_defaults_to_general(self):
        """Unknown tracker names should default to general."""
        assert get_category_for_tracker("Meine Katze füttern") == "general"

    def test_random_text_defaults_to_general(self):
        """Random text should default to general."""
        assert get_category_for_tracker("xyz123") == "general"

    def test_empty_string_defaults_to_general(self):
        """Empty string should default to general."""
        assert get_category_for_tracker("") == "general"

    # =========================================================================
    # Case Insensitivity
    # =========================================================================

    def test_category_detection_is_case_insensitive(self):
        """Category detection should work regardless of case."""
        assert get_category_for_tracker("BANKDRÜCKEN") == "fitness"
        assert get_category_for_tracker("BaNkDrÜcKeN") == "fitness"

    def test_partial_match_in_longer_name(self):
        """Should detect category when keyword is part of longer name."""
        assert get_category_for_tracker("Mein Bankdrücken Tracker") == "fitness"


class TestTrackerCategoriesMapping:
    """Tests to verify the TRACKER_CATEGORIES mapping is complete."""

    def test_all_fitness_exercises_are_mapped(self):
        """Verify common fitness exercises are in the mapping."""
        fitness_exercises = [
            "bankdrücken", "bench press", "kniebeugen", "squat",
            "kreuzheben", "deadlift", "klimmzüge", "pull-ups"
        ]
        for exercise in fitness_exercises:
            assert exercise in TRACKER_CATEGORIES
            assert TRACKER_CATEGORIES[exercise] == "fitness"

    def test_all_health_metrics_are_mapped(self):
        """Verify common health metrics are in the mapping."""
        health_metrics = ["gewicht", "weight", "schlaf", "sleep", "wasser", "water"]
        for metric in health_metrics:
            assert metric in TRACKER_CATEGORIES
            assert TRACKER_CATEGORIES[metric] == "health"

    def test_default_category_exists(self):
        """Verify default fallback category exists."""
        assert "default" in TRACKER_CATEGORIES
        assert TRACKER_CATEGORIES["default"] == "general"
