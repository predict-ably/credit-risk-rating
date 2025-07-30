"""Tests for credit_risk_rating.rating._mappings module.

This module contains comprehensive tests for the RatingScale and Metadata classes,
ensuring proper immutability, validation, and functionality. Tests are designed
to achieve 100% code coverage and robust edge case testing.
"""

from __future__ import annotations

import pytest

from credit_risk_rating.exceptions import MetadataError, RatingScaleError
from credit_risk_rating.rating.system._mappings import Metadata, RatingScale


class TestBaseImmutableMapping:
    """Test suite for common behavior across RatingScale and Metadata."""

    @pytest.mark.parametrize(
        "mapping_class,sample_data",
        [
            (RatingScale, {1: 0.01, 2: 0.02, 3: 0.05}),
            (Metadata, {"model_version": "v2.1", "institution": "ABC"}),
        ],
    )
    def test_immutability_after_init(self, mapping_class, sample_data) -> None:
        """Test that objects become immutable after initialization."""
        instance = mapping_class(sample_data)

        with pytest.raises(AttributeError, match="immutable"):
            instance.new_attr = "value"

        with pytest.raises(AttributeError, match="immutable"):
            instance._data = {}

    @pytest.mark.parametrize(
        "mapping_class,sample_data",
        [
            (RatingScale, {1: 0.01, 2: 0.02}),
            (Metadata, {"key1": "value1", "key2": "value2"}),
        ],
    )
    def test_dictionary_like_access(self, mapping_class, sample_data) -> None:
        """Test dictionary-like access patterns."""
        instance = mapping_class(sample_data)

        # Test __getitem__
        first_key = list(sample_data.keys())[0]
        assert instance[first_key] == sample_data[first_key]

        # Test __contains__
        assert first_key in instance
        assert "nonexistent" not in instance

        # Test __len__
        assert len(instance) == len(sample_data)

        # Test __iter__
        assert set(instance) == set(sample_data.keys())

    @pytest.mark.parametrize(
        "mapping_class,sample_data",
        [
            (RatingScale, {1: 0.01, 2: 0.02}),
            (Metadata, {"key1": "value1", "key2": "value2"}),
        ],
    )
    def test_equality_and_repr(self, mapping_class, sample_data) -> None:
        """Test equality comparison and string representation."""
        instance1 = mapping_class(sample_data)
        instance2 = mapping_class(sample_data.copy())
        instance3 = mapping_class({})

        # Test equality
        assert instance1 == instance2
        assert instance1 != instance3
        assert instance1 != "not a mapping"

        # Test repr
        repr_str = repr(instance1)
        assert mapping_class.__name__ in repr_str
        assert str(sample_data) in repr_str

    @pytest.mark.parametrize(
        "mapping_class,sample_data",
        [
            (RatingScale, {1: 0.01, 2: 0.02, 3: 0.05}),
            (Metadata, {"a": 1, "b": 2, "c": 3}),
        ],
    )
    def test_keys_values_items(self, mapping_class, sample_data) -> None:
        """Test keys(), values(), and items() methods."""
        instance = mapping_class(sample_data)

        # Test keys
        keys = instance.keys()
        assert isinstance(keys, list)
        assert set(keys) == set(sample_data.keys())

        # Test values
        values = instance.values()
        assert isinstance(values, list)
        assert set(values) == set(sample_data.values())

        # Test items
        items = instance.items()
        assert isinstance(items, list)
        assert set(items) == set(sample_data.items())

    @pytest.mark.parametrize("mapping_class", [RatingScale, Metadata])
    def test_empty_initialization(self, mapping_class) -> None:
        """Test initialization with no data."""
        instance = mapping_class()
        assert len(instance) == 0
        assert list(instance.keys()) == []
        assert list(instance.values()) == []
        assert list(instance.items()) == []

    @pytest.mark.parametrize("mapping_class", [RatingScale, Metadata])
    def test_none_initialization(self, mapping_class) -> None:
        """Test initialization with None."""
        instance = mapping_class(None)
        assert len(instance) == 0

    @pytest.mark.parametrize(
        "mapping_class,sample_data",
        [
            (RatingScale, {1: 0.01, 2: 0.02}),
            (Metadata, {"key1": "value1", "key2": "value2"}),
        ],
    )
    def test_to_dict(self, mapping_class, sample_data) -> None:
        """Test to_dict() method."""
        instance = mapping_class(sample_data)
        result = instance.to_dict()

        assert result == sample_data
        assert result is not instance._data  # Different object

        # Modifying returned dict shouldn't affect original
        if sample_data:
            first_key = list(sample_data.keys())[0]
            result[first_key] = "modified"
            assert instance[first_key] == sample_data[first_key]

    @pytest.mark.parametrize(
        "mapping_class,sample_data",
        [
            (RatingScale, {1: 0.01, 2: 0.02}),
            (Metadata, {"key1": "value1", "key2": "value2"}),
        ],
    )
    def test_from_dict_classmethod(self, mapping_class, sample_data) -> None:
        """Test from_dict class method."""
        # With data
        instance = mapping_class.from_dict(sample_data)
        assert instance.to_dict() == sample_data

        # With None
        instance = mapping_class.from_dict(None)
        assert len(instance) == 0

        # With empty dict
        instance = mapping_class.from_dict({})
        assert len(instance) == 0


class TestRatingScale:
    """Test suite for RatingScale class."""

    def test_valid_initialization(self) -> None:
        """Test valid initialization patterns."""
        # Integer grades with float values
        rating_map = RatingScale({1: 0.01, 2: 0.02, 3: 0.05})
        assert len(rating_map) == 3
        assert rating_map[1] == 0.01

        # String grades with float values
        rating_map = RatingScale({"A": 0.10, "B": 0.20, "C": 0.35})
        assert len(rating_map) == 3
        assert rating_map["A"] == 0.10

        # Mixed grades with float values
        rating_map = RatingScale({1: 0.01, "A": 0.10})
        assert len(rating_map) == 2
        assert rating_map[1] == 0.01
        assert rating_map["A"] == 0.10

    def test_invalid_grade_types(self) -> None:
        """Test that invalid grade types raise TypeError."""
        with pytest.raises(TypeError, match="Rating grades must be 'str' or 'int'"):
            RatingScale({1.5: 0.01})  # float grade

        with pytest.raises(TypeError, match="Rating grades must be 'str' or 'int'"):
            RatingScale({None: 0.01})  # None grade

        with pytest.raises(TypeError, match="Rating grades must be 'str' or 'int'"):
            RatingScale({[1, 2]: 0.01})  # list grade

    def test_invalid_value_types(self) -> None:
        """Test that non-float values raise TypeError."""
        with pytest.raises(TypeError, match="must be numeric"):
            RatingScale({1: "not_numeric"})

        with pytest.raises(TypeError, match="must be numeric"):
            RatingScale({1: 0.01, 2: None})

        with pytest.raises(TypeError, match="must be numeric"):
            RatingScale({1: 0.01, 2: [1, 2, 3]})

        with pytest.raises(TypeError, match="must be numeric"):
            RatingScale(
                {1: 1}
            )  # int values should also raise error according to validation

    def test_float_values_only(self) -> None:
        """Test that only float values are accepted."""
        # This should work
        rating_map = RatingScale({1: 1.0, 2: 2.5, 3: 0.0})  # All floats
        assert rating_map[1] == 1.0
        assert rating_map[2] == 2.5
        assert rating_map[3] == 0.0

    def test_rating_scale_property(self) -> None:
        """Test the rating_scale property."""
        original_data = {1: 0.01, 2: 0.02}
        rating_map = RatingScale(original_data)

        # Should return a copy
        scale = rating_map.rating_scale
        assert scale == original_data
        assert scale is not rating_map._data  # Different object

        # Modifying returned dict shouldn't affect original
        scale[3] = 0.03
        assert 3 not in rating_map

    def test_rating_grades_method(self) -> None:
        """Test rating_grades() method."""
        rating_map = RatingScale({3: 0.05, 1: 0.01, 2: 0.02})
        grades = rating_map.rating_grades()

        assert isinstance(grades, list)
        assert set(grades) == {1, 2, 3}

    def test_rating_values_method(self) -> None:
        """Test rating_values() method."""
        rating_map = RatingScale({1: 0.01, 2: 0.02, 3: 0.05})
        values = rating_map.rating_values()

        assert isinstance(values, list)
        assert set(values) == {0.01, 0.02, 0.05}

    def test_rating_grade_value_pairs_method(self) -> None:
        """Test rating_grade_value_pairs() method."""
        rating_map = RatingScale({1: 0.01, 2: 0.02})
        pairs = rating_map.rating_grade_value_pairs()

        assert isinstance(pairs, list)
        assert set(pairs) == {(1, 0.01), (2, 0.02)}

    def test_subset_grades_single_grade(self) -> None:
        """Test subset_grades with single grade."""
        rating_map = RatingScale({1: 0.01, 2: 0.02, 3: 0.05})

        subset = rating_map.subset_grades(2)
        assert len(subset) == 1
        assert subset[2] == 0.02
        assert isinstance(subset, RatingScale)

    def test_subset_grades_multiple_grades(self) -> None:
        """Test subset_grades with multiple grades."""
        rating_map = RatingScale({1: 0.01, 2: 0.02, 3: 0.05, 4: 0.10})

        subset = rating_map.subset_grades([1, 3])
        assert len(subset) == 2
        assert subset[1] == 0.01
        assert subset[3] == 0.05
        assert 2 not in subset

    def test_subset_grades_missing_grade(self) -> None:
        """Test subset_grades with missing grades."""
        rating_map = RatingScale({1: 0.01, 2: 0.02})

        # Single missing grade
        with pytest.raises(RatingScaleError) as exc_info:
            rating_map.subset_grades(3)

        error = exc_info.value
        assert "Rating grades not found: [3]" in str(error)
        assert error.rating == 3
        assert set(error.available_ratings) == {1, 2}

        # Multiple missing grades
        with pytest.raises(RatingScaleError) as exc_info:
            rating_map.subset_grades([1, 3, 4])  # 1 exists, 3,4 don't

        error = exc_info.value
        assert "[3, 4]" in str(error)
        assert error.rating == 3  # First missing grade

    def test_subset_grades_all_missing(self) -> None:
        """Test subset_grades when all requested grades are missing."""
        rating_map = RatingScale({1: 0.01, 2: 0.02})

        with pytest.raises(RatingScaleError) as exc_info:
            rating_map.subset_grades([5, 6])

        error = exc_info.value
        assert "[5, 6]" in str(error)
        assert error.rating == 5

    def test_add_rating_grades(self) -> None:
        """Test add_rating_grades method."""
        rating_map = RatingScale({1: 0.01, 2: 0.02})

        # Add new grades
        expanded = rating_map.add_rating_grades({3: 0.05, 4: 0.10})
        assert len(expanded) == 4
        assert expanded[1] == 0.01  # Original data preserved
        assert expanded[3] == 0.05  # New data added
        assert isinstance(expanded, RatingScale)

        # Original unchanged
        assert len(rating_map) == 2

    def test_add_rating_grades_override(self) -> None:
        """Test add_rating_grades with overlapping grades."""
        rating_map = RatingScale({1: 0.01, 2: 0.02})

        # Override existing grade
        expanded = rating_map.add_rating_grades({1: 0.015, 3: 0.05})
        assert len(expanded) == 3
        assert expanded[1] == 0.015  # Overridden value
        assert expanded[2] == 0.02  # Original value
        assert expanded[3] == 0.05  # New value

    def test_add_rating_grades_empty(self) -> None:
        """Test add_rating_grades with empty dict."""
        rating_map = RatingScale({1: 0.01, 2: 0.02})

        expanded = rating_map.add_rating_grades({})
        assert len(expanded) == 2
        assert expanded.rating_scale == rating_map.rating_scale

    def test_add_rating_grades_validation(self) -> None:
        """Test that add_rating_grades validates new data."""
        rating_map = RatingScale({1: 0.01, 2: 0.02})

        # Should validate new grades and values
        with pytest.raises(TypeError):
            rating_map.add_rating_grades({1.5: 0.03})  # Invalid grade type

        with pytest.raises(TypeError):
            rating_map.add_rating_grades({3: "invalid"})  # Invalid value type

    def test_get_grade_value(self) -> None:
        """Test get_grade_value method."""
        rating_map = RatingScale({1: 0.01, "A": 0.10})

        assert rating_map.get_grade_value(1) == 0.01
        assert rating_map.get_grade_value("A") == 0.10

        # Test KeyError for missing grade
        with pytest.raises(KeyError):
            rating_map.get_grade_value(99)

    def test_has_grade(self) -> None:
        """Test has_grade method."""
        rating_map = RatingScale({1: 0.01, "A": 0.10})

        assert rating_map.has_grade(1) is True
        assert rating_map.has_grade("A") is True
        assert rating_map.has_grade(99) is False
        assert rating_map.has_grade("Z") is False

    def test_key_error_access(self) -> None:
        """Test KeyError when accessing non-existent grades."""
        rating_map = RatingScale({1: 0.01, 2: 0.02})

        with pytest.raises(KeyError):
            _ = rating_map[99]

        with pytest.raises(KeyError):
            _ = rating_map["nonexistent"]


class TestMetadata:
    """Test suite for Metadata class."""

    def test_valid_initialization(self) -> None:
        """Test valid initialization patterns."""
        # Valid Python identifiers
        metadata = Metadata({"model_version": "v2.1", "institution": "ABC"})
        assert len(metadata) == 2
        assert metadata["model_version"] == "v2.1"
        assert metadata.model_version == "v2.1"  # Attribute access

        # Underscore identifiers
        metadata = Metadata({"_private": "value", "valid_name": "test"})
        assert metadata._private == "value"
        assert metadata.valid_name == "test"

    def test_attribute_access(self) -> None:
        """Test attribute access functionality."""
        metadata = Metadata(
            {
                "model_version": "v2.1",
                "institution": "ABC Bank",
                "calibration_date": "2024-01-01",
            }
        )

        # All should be accessible as attributes
        assert metadata.model_version == "v2.1"
        assert metadata.institution == "ABC Bank"
        assert metadata.calibration_date == "2024-01-01"

        # And as dictionary items
        assert metadata["model_version"] == "v2.1"
        assert metadata["institution"] == "ABC Bank"

    def test_invalid_key_types(self) -> None:
        """Test that non-string keys raise MetadataError."""
        with pytest.raises(MetadataError, match="must be string"):
            Metadata({123: "value"})

        with pytest.raises(MetadataError, match="must be string"):
            Metadata({None: "value"})

        with pytest.raises(MetadataError, match="must be string"):
            Metadata({["list"]: "value"})

    def test_invalid_identifier_keys(self) -> None:
        """Test that invalid Python identifiers raise MetadataError."""
        with pytest.raises(MetadataError, match="not a valid Python identifier"):
            Metadata({"123invalid": "value"})

        with pytest.raises(MetadataError, match="not a valid Python identifier"):
            Metadata({"invalid-key": "value"})

        with pytest.raises(MetadataError, match="not a valid Python identifier"):
            Metadata({"invalid key": "value"})  # Space

        with pytest.raises(MetadataError, match="not a valid Python identifier"):
            Metadata({"if": "value"})  # Python keyword

    def test_metadata_property(self) -> None:
        """Test the metadata property."""
        original_data = {"key1": "value1", "key2": "value2"}
        metadata = Metadata(original_data)

        # Should return a copy
        meta_dict = metadata.metadata
        assert meta_dict == original_data
        assert meta_dict is not metadata._data  # Different object

        # Modifying returned dict shouldn't affect original
        meta_dict["key3"] = "value3"
        assert "key3" not in metadata

    def test_metadata_items_method(self) -> None:
        """Test metadata_items() method."""
        metadata = Metadata({"c": 3, "a": 1, "b": 2})
        items = metadata.metadata_items()

        assert isinstance(items, list)
        assert set(items) == {"a", "b", "c"}

    def test_metadata_values_method(self) -> None:
        """Test metadata_values() method."""
        metadata = Metadata({"key1": "value1", "key2": "value2"})
        values = metadata.metadata_values()

        assert isinstance(values, list)
        assert set(values) == {"value1", "value2"}

    def test_metadata_item_value_pairs_method(self) -> None:
        """Test metadata_item_value_pairs() method."""
        metadata = Metadata({"key1": "value1", "key2": "value2"})
        pairs = metadata.metadata_item_value_pairs()

        assert isinstance(pairs, list)
        assert set(pairs) == {("key1", "value1"), ("key2", "value2")}

    def test_subset_metadata_single_item(self) -> None:
        """Test subset_metadata with single item."""
        metadata = Metadata(
            {"model_version": "v2.1", "institution": "ABC", "date": "2024-01-01"}
        )

        subset = metadata.subset_metadata("model_version")
        assert len(subset) == 1
        assert subset["model_version"] == "v2.1"
        assert subset.model_version == "v2.1"
        assert isinstance(subset, Metadata)

    def test_subset_metadata_multiple_items(self) -> None:
        """Test subset_metadata with multiple items."""
        metadata = Metadata(
            {
                "model_version": "v2.1",
                "institution": "ABC",
                "date": "2024-01-01",
                "score": 0.85,
            }
        )

        subset = metadata.subset_metadata(["model_version", "score"])
        assert len(subset) == 2
        assert subset["model_version"] == "v2.1"
        assert subset["score"] == 0.85
        assert "institution" not in subset

    def test_subset_metadata_missing_item(self) -> None:
        """Test subset_metadata with missing items."""
        metadata = Metadata({"key1": "value1", "key2": "value2"})

        # Single missing item
        with pytest.raises(MetadataError) as exc_info:
            metadata.subset_metadata("missing")

        error = exc_info.value
        assert "Keys not found in metadata: ['missing']" in str(error)
        assert error.key == "missing"

        # Multiple missing items
        with pytest.raises(MetadataError) as exc_info:
            metadata.subset_metadata(["key1", "missing1", "missing2"])

        error = exc_info.value
        assert "['missing1', 'missing2']" in str(error)
        assert error.key == "missing1"  # First missing key

    def test_add_metadata(self) -> None:
        """Test add_metadata method."""
        metadata = Metadata({"key1": "value1", "key2": "value2"})

        # Add new metadata
        expanded = metadata.add_metadata({"key3": "value3", "key4": "value4"})
        assert len(expanded) == 4
        assert expanded["key1"] == "value1"  # Original data preserved
        assert expanded["key3"] == "value3"  # New data added
        assert expanded.key3 == "value3"  # Attribute access works
        assert isinstance(expanded, Metadata)

        # Original unchanged
        assert len(metadata) == 2

    def test_add_metadata_override(self) -> None:
        """Test add_metadata with overlapping keys."""
        metadata = Metadata({"key1": "value1", "key2": "value2"})

        # Override existing key
        expanded = metadata.add_metadata({"key1": "new_value", "key3": "value3"})
        assert len(expanded) == 3
        assert expanded["key1"] == "new_value"  # Overridden value
        assert expanded["key2"] == "value2"  # Original value
        assert expanded["key3"] == "value3"  # New value
        assert expanded.key1 == "new_value"  # Attribute access updated

    def test_add_metadata_empty(self) -> None:
        """Test add_metadata with empty dict."""
        metadata = Metadata({"key1": "value1", "key2": "value2"})

        expanded = metadata.add_metadata({})
        assert len(expanded) == 2
        assert expanded.metadata == metadata.metadata

    def test_add_metadata_validation(self) -> None:
        """Test that add_metadata validates new data."""
        metadata = Metadata({"valid_key": "value"})

        # Should validate new keys
        with pytest.raises(MetadataError):
            metadata.add_metadata({"123invalid": "value"})  # Invalid identifier

        with pytest.raises(MetadataError):
            metadata.add_metadata({123: "value"})  # Non-string key

    def test_key_error_access(self) -> None:
        """Test KeyError when accessing non-existent metadata."""
        metadata = Metadata({"key1": "value1"})

        with pytest.raises(KeyError):
            _ = metadata["nonexistent"]

    def test_attribute_error_access(self) -> None:
        """Test AttributeError when accessing non-existent attributes."""
        metadata = Metadata({"key1": "value1"})

        with pytest.raises(AttributeError):
            _ = metadata.nonexistent_attribute

    def test_complex_values(self) -> None:
        """Test that complex value types are supported."""
        complex_data = {
            "string_val": "text",
            "int_val": 42,
            "float_val": 3.14,
            "bool_val": True,
            "none_val": None,
            "list_val": [1, 2, 3],
            "dict_val": {"nested": "value"},
        }

        metadata = Metadata(complex_data)

        # All should be accessible
        assert metadata.string_val == "text"
        assert metadata.int_val == 42
        assert metadata.float_val == 3.14
        assert metadata.bool_val is True
        assert metadata.none_val is None
        assert metadata.list_val == [1, 2, 3]
        assert metadata.dict_val == {"nested": "value"}


class TestEdgeCases:
    """Test suite for edge cases and error conditions."""

    def test_empty_data_protection(self) -> None:
        """Test that empty internal data is protected."""
        rating_map = RatingScale({})
        metadata = Metadata({})

        # Should not be able to modify internal data
        with pytest.raises(AttributeError):
            rating_map._data = {1: 0.01}

        with pytest.raises(AttributeError):
            metadata._data = {"key": "value"}

    def test_data_copy_isolation(self) -> None:
        """Test that original data is isolated from external changes."""
        original_data = {1: 0.01, 2: 0.02}
        rating_map = RatingScale(original_data)

        # Modifying original data shouldn't affect the rating map
        original_data[3] = 0.03
        assert 3 not in rating_map
        assert len(rating_map) == 2

    def test_frozen_state_timing(self) -> None:
        """Test that _frozen attribute prevents modification at right time."""
        # During initialization, attributes can be set
        # After initialization, they cannot be
        rating_map = RatingScale({1: 0.01})

        # Should have _frozen attribute
        assert hasattr(rating_map, "_frozen")
        assert rating_map._frozen is True

        # Should not be able to modify _frozen
        with pytest.raises(AttributeError):
            rating_map._frozen = False

    def test_subset_with_empty_list(self) -> None:
        """Test subset methods with empty lists."""
        rating_map = RatingScale({1: 0.01, 2: 0.02})
        metadata = Metadata({"key1": "value1", "key2": "value2"})

        # Empty list should return empty instance
        empty_rating_subset = rating_map.subset_grades([])
        assert len(empty_rating_subset) == 0
        assert isinstance(empty_rating_subset, RatingScale)

        empty_metadata_subset = metadata.subset_metadata([])
        assert len(empty_metadata_subset) == 0
        assert isinstance(empty_metadata_subset, Metadata)

    def test_large_datasets(self) -> None:
        """Test with larger datasets to ensure performance."""
        # Large rating map
        large_rating_data = {i: float(i) * 0.01 for i in range(1000)}
        large_rating_map = RatingScale(large_rating_data)

        assert len(large_rating_map) == 1000
        assert large_rating_map[500] == 5.0

        # Large metadata
        large_metadata_data = {f"key_{i}": f"value_{i}" for i in range(100)}
        large_metadata = Metadata(large_metadata_data)

        assert len(large_metadata) == 100
        assert large_metadata.key_50 == "value_50"

    def test_unicode_and_special_characters(self) -> None:
        """Test handling of unicode and special characters."""
        # RatingScale with unicode grades (strings)
        unicode_rating_map = RatingScale({"α": 0.01, "β": 0.02, "γ": 0.03})
        assert unicode_rating_map["α"] == 0.01
        assert unicode_rating_map["β"] == 0.02

        # Metadata with unicode values (but valid identifier keys)
        unicode_metadata = Metadata(
            {
                "unicode_text": "Hello 世界",
                "emoji_value": "🚀📊",
                "special_chars": "Special: @#$%^&*()",
            }
        )

        assert unicode_metadata.unicode_text == "Hello 世界"
        assert unicode_metadata.emoji_value == "🚀📊"
        assert unicode_metadata.special_chars == "Special: @#$%^&*()"


class TestErrorMessages:
    """Test suite for error message quality and context."""

    def test_rating_map_error_context(self) -> None:
        """Test that RatingScaleError provides good context."""
        rating_map = RatingScale({1: 0.01, 2: 0.02, "A": 0.10})

        with pytest.raises(RatingScaleError) as exc_info:
            rating_map.subset_grades([1, "missing", "also_missing"])

        error = exc_info.value
        assert "missing" in str(error)
        assert "also_missing" in str(error)
        assert error.rating == "missing"  # First missing
        assert set(error.available_ratings) == {1, 2, "A"}

    def test_metadata_error_context(self) -> None:
        """Test that MetadataError provides good context."""
        metadata = Metadata({"key1": "value1", "key2": "value2", "key3": "value3"})

        with pytest.raises(MetadataError) as exc_info:
            metadata.subset_metadata(["key1", "missing", "also_missing"])

        error = exc_info.value
        assert "missing" in str(error)
        assert "also_missing" in str(error)
        assert error.key == "missing"  # First missing
        assert "Available keys: ['key1', 'key2', 'key3']" in str(error)

    def test_validation_error_messages(self) -> None:
        """Test specific validation error messages."""
        # RatingScale grade type errors
        with pytest.raises(TypeError) as exc_info:
            RatingScale({1.5: 0.01, None: 0.02})

        error_msg = str(exc_info.value)
        assert "Rating grades must be 'str' or 'int'" in error_msg
        assert "1.5" in error_msg
        assert "None" in error_msg

        # RatingScale value type errors
        with pytest.raises(TypeError) as exc_info:
            RatingScale({1: "invalid", 2: None})

        error_msg = str(exc_info.value)
        assert "must be numeric" in error_msg
        assert "'1'" in error_msg or "1" in error_msg
        assert "'2'" in error_msg or "2" in error_msg

        # Metadata key validation
        with pytest.raises(MetadataError) as exc_info:
            Metadata({"123invalid": "value"})

        error = exc_info.value
        assert "not a valid Python identifier" in str(error)
        assert error.key == "123invalid"


class TestMethodCoverage:
    """Test suite to ensure 100% method coverage."""

    def test_base_class_add_items_directly(self) -> None:
        """Test _add_items method coverage."""
        rating_map = RatingScale({1: 0.01, 2: 0.02})

        # This tests the _add_items method indirectly through add_rating_grades
        result = rating_map._add_items({3: 0.03, 4: 0.04})

        assert len(result) == 4
        assert result[1] == 0.01  # Original preserved
        assert result[3] == 0.03  # New added
        assert isinstance(result, RatingScale)

    def test_string_conversion_coverage(self) -> None:
        """Test string conversion edge cases."""
        # Test repr with various data types
        rating_map = RatingScale({"A": 1.0, 1: 2.0})
        repr_str = repr(rating_map)
        assert "RatingScale" in repr_str
        assert "A" in repr_str or "'A'" in repr_str

        metadata = Metadata({"key": [1, 2, 3], "other": {"nested": True}})
        repr_str = repr(metadata)
        assert "Metadata" in repr_str
        assert "key" in repr_str

    def test_iteration_patterns(self) -> None:
        """Test various iteration patterns."""
        rating_map = RatingScale({1: 0.01, 2: 0.02, 3: 0.03})

        # Test direct iteration
        keys_from_iter = [key for key in rating_map]
        assert set(keys_from_iter) == {1, 2, 3}

        # Test with builtin functions
        assert list(rating_map) == rating_map.keys()
        assert len(list(rating_map)) == 3

        metadata = Metadata({"a": 1, "b": 2, "c": 3})

        # Test direct iteration
        keys_from_iter = [key for key in metadata]
        assert set(keys_from_iter) == {"a", "b", "c"}

        # Test that iteration order is consistent with keys()
        assert list(metadata) == metadata.keys()

    def test_contains_operator_coverage(self) -> None:
        """Test __contains__ operator thoroughly."""
        rating_map = RatingScale({1: 0.01, "A": 0.10})

        # Test with various types
        assert 1 in rating_map
        assert "A" in rating_map
        assert 2 not in rating_map
        assert "B" not in rating_map
        assert None not in rating_map
        assert 1.0 not in rating_map  # Different type

        metadata = Metadata({"valid_key": "value"})

        assert "valid_key" in metadata
        assert "invalid_key" not in metadata
        assert None not in metadata
        assert 123 not in metadata

    def test_equality_edge_cases(self) -> None:
        """Test equality comparison edge cases."""
        rating_map1 = RatingScale({1: 0.01, 2: 0.02})
        rating_map2 = RatingScale({1: 0.01, 2: 0.02})
        rating_map3 = RatingScale({1: 0.01, 2: 0.03})  # Different value

        # Test equality
        assert rating_map1 == rating_map2
        assert rating_map1 != rating_map3

        # Test with different types
        assert rating_map1 != {1: 0.01, 2: 0.02}  # Dict
        assert rating_map1 != "not a rating map"  # String
        assert rating_map1 is not None  # None
        assert rating_map1 != 42  # Number

        # Test with Metadata (different class)
        metadata = Metadata({"key": "value"})
        assert rating_map1 != metadata

        # Metadata equality tests
        metadata1 = Metadata({"a": 1, "b": 2})
        metadata2 = Metadata({"a": 1, "b": 2})
        metadata3 = Metadata({"a": 1, "b": 3})

        assert metadata1 == metadata2
        assert metadata1 != metadata3
        assert metadata1 != rating_map1


class TestIntegrationScenarios:
    """Test suite for realistic integration scenarios."""

    def test_fcs_rating_scale_scenario(self) -> None:
        """Test realistic FCS rating scale scenario."""
        # Create a typical FCS PD rating scale
        fcs_pd_scale = {
            1: 0.0005,
            2: 0.0010,
            3: 0.0025,
            4: 0.0050,
            5: 0.0075,
            6: 0.0125,
            7: 0.0200,
            8: 0.0300,
            9: 0.0500,
            10: 0.0750,
            11: 0.1250,
            12: 0.2000,
            13: 0.4000,
            14: 0.8000,
        }

        rating_map = RatingScale(fcs_pd_scale)

        # Test typical operations
        assert len(rating_map) == 14
        assert rating_map[1] == 0.0005
        assert rating_map[14] == 0.8000

        # Create subset for investment grade (1-10)
        investment_grade = rating_map.subset_grades(list(range(1, 11)))
        assert len(investment_grade) == 10
        assert 11 not in investment_grade

        # Add custom grade
        expanded = rating_map.add_rating_grades({15: 1.0})
        assert len(expanded) == 15
        assert expanded[15] == 1.0

    def test_model_metadata_scenario(self) -> None:
        """Test realistic model metadata scenario."""
        # Create typical model metadata
        model_metadata = Metadata(
            {
                "model_name": "FCS_PD_Model_v2_1",
                "institution": "ABC_Farm_Credit",
                "calibration_date": "2024-01-01",
                "model_version": "2.1.0",
                "validation_score": 0.85,
                "sample_size": 50000,
                "approved": True,
                "methodology": "Logistic_Regression",
            }
        )

        # Test attribute access
        assert model_metadata.model_name == "FCS_PD_Model_v2_1"
        assert model_metadata.validation_score == 0.85
        assert model_metadata.approved is True

        # Create subset for reporting
        report_metadata = model_metadata.subset_metadata(
            ["model_name", "calibration_date", "validation_score"]
        )
        assert len(report_metadata) == 3
        assert report_metadata.model_name == "FCS_PD_Model_v2_1"

        # Add audit information
        audited_metadata = model_metadata.add_metadata(
            {
                "audit_date": "2024-07-01",
                "auditor": "External_Validator",
                "audit_passed": True,
            }
        )

        assert len(audited_metadata) == 11  # 8 original + 3 new
        assert audited_metadata.audit_passed is True
        assert audited_metadata.model_name == "FCS_PD_Model_v2_1"  # Original preserved

    def test_round_trip_serialization(self) -> None:
        """Test round-trip serialization scenarios."""
        # Test RatingScale round-trip
        original_rating_data = {1: 0.01, "A": 0.10, 5: 0.05}
        rating_map = RatingScale(original_rating_data)

        # Export and recreate
        exported_dict = rating_map.to_dict()
        recreated_rating_map = RatingScale.from_dict(exported_dict)

        assert rating_map == recreated_rating_map
        assert rating_map.rating_scale == recreated_rating_map.rating_scale

        # Test Metadata round-trip
        original_metadata_data = {
            "key1": "value1",
            "key2": 42,
            "key3": [1, 2, 3],
            "key4": {"nested": True},
        }
        metadata = Metadata(original_metadata_data)

        # Export and recreate
        exported_dict = metadata.to_dict()
        recreated_metadata = Metadata.from_dict(exported_dict)

        assert metadata == recreated_metadata
        assert metadata.metadata == recreated_metadata.metadata

        # Test attribute access still works
        assert recreated_metadata.key1 == "value1"
        assert recreated_metadata.key2 == 42


# Fixtures for complex testing scenarios
@pytest.fixture
def sample_fcs_rating_map() -> RatingScale:
    """Fixture providing a realistic FCS rating scale."""
    return RatingScale(
        {
            1: 0.0005,
            2: 0.0010,
            3: 0.0025,
            4: 0.0050,
            5: 0.0075,
            6: 0.0125,
            7: 0.0200,
            8: 0.0300,
            9: 0.0500,
            10: 0.0750,
            11: 0.1250,
            12: 0.2000,
            13: 0.4000,
            14: 0.8000,
        }
    )


@pytest.fixture
def sample_model_metadata() -> Metadata:
    """Fixture providing realistic model metadata."""
    return Metadata(
        {
            "model_name": "Test_Model",
            "version": "1.0.0",
            "institution": "Test_Bank",
            "calibration_date": "2024-01-01",
            "validation_score": 0.85,
            "approved": True,
        }
    )


class TestFixtures:
    """Test suite for fixture usage and validation."""

    def test_fcs_rating_map_fixture(self, sample_fcs_rating_map: RatingScale) -> None:
        """Test the FCS rating map fixture."""
        assert len(sample_fcs_rating_map) == 14
        assert sample_fcs_rating_map[1] == 0.0005
        assert sample_fcs_rating_map[14] == 0.8000
        assert isinstance(sample_fcs_rating_map, RatingScale)

    def test_model_metadata_fixture(self, sample_model_metadata: Metadata) -> None:
        """Test the model metadata fixture."""
        assert len(sample_model_metadata) == 6
        assert sample_model_metadata.model_name == "Test_Model"
        assert sample_model_metadata.approved is True
        assert isinstance(sample_model_metadata, Metadata)

    def test_fixture_immutability(
        self, sample_fcs_rating_map: RatingScale, sample_model_metadata: Metadata
    ) -> None:
        """Test that fixtures provide immutable objects."""
        # Should not be able to modify fixture objects
        with pytest.raises(AttributeError):
            sample_fcs_rating_map.new_attr = "value"

        with pytest.raises(AttributeError):
            sample_model_metadata.new_attr = "value"

    def test_fixture_independence(self, sample_fcs_rating_map: RatingScale) -> None:
        """Test that fixture objects are independent between tests."""
        # This test and the previous should get separate instances
        original_length = len(sample_fcs_rating_map)

        # Create a new instance by adding grades
        expanded = sample_fcs_rating_map.add_rating_grades({15: 1.0})

        # Original fixture should be unchanged
        assert len(sample_fcs_rating_map) == original_length
        assert len(expanded) == original_length + 1
        assert 15 not in sample_fcs_rating_map
        assert 15 in expanded
