"""Tests for credit_risk_rating.exceptions module.

This module contains comprehensive tests for all exception classes defined in
the credit_risk_rating.exceptions module, ensuring proper inheritance,
initialization, and behavior.
"""

from __future__ import annotations

import pytest

from credit_risk_rating.exceptions import (
    MetadataError,
    RatingScaleError,
    RatingScaleInputError,
    RatingValidationError,
)


class BaseExceptionTest:
    """Base test class with common exception testing patterns.

    This class provides common test methods that can be inherited by
    specific exception test classes to avoid code duplication.
    """

    # Subclasses should override these
    exception_class = None
    expected_base_class = None

    def test_inheritance(self) -> None:
        """Test that exception inherits from expected base class."""
        assert issubclass(self.exception_class, self.expected_base_class)

    def test_basic_initialization(self) -> None:
        """Test basic initialization with message only."""
        message = "Test error message"
        error = self.exception_class(message)

        # Handle KeyError's string representation quirk
        if issubclass(self.exception_class, KeyError):
            assert str(error) == f"'{message}'"
        else:
            assert str(error) == message

        assert isinstance(error, self.expected_base_class)
        assert isinstance(error, self.exception_class)

    def test_initialization_with_args(self) -> None:
        """Test initialization with additional arguments."""
        message = "Test error"
        extra_arg = "additional context"
        error = self.exception_class(message, extra_arg)

        # All exceptions should include extra args in string representation
        assert extra_arg in str(error)

    def test_raise_and_catch(self) -> None:
        """Test raising and catching the exception."""
        message = "Test exception"

        with pytest.raises(self.exception_class) as exc_info:
            raise self.exception_class(message)

        assert isinstance(exc_info.value, self.expected_base_class)
        assert isinstance(exc_info.value, self.exception_class)

    def test_exception_in_inheritance_chain(self) -> None:
        """Test that exception can be caught as base Exception types."""
        error = self.exception_class("test")

        # Should be catchable as expected base class
        try:
            raise error
        except self.expected_base_class:
            pass  # Expected
        else:
            pytest.fail(
                f"Should have been caught as {self.expected_base_class.__name__}"
            )

        # Should be catchable as Exception
        try:
            raise error
        except Exception:
            pass  # Expected
        else:
            pytest.fail("Should have been caught as Exception")


class TestRatingScaleInputError(BaseExceptionTest):
    """Test suite for RatingScaleInputError exception."""

    exception_class = RatingScaleInputError
    expected_base_class = ValueError


class TestRatingValidationError(BaseExceptionTest):
    """Test suite for RatingValidationError exception."""

    exception_class = RatingValidationError
    expected_base_class = ValueError

    def test_initialization_with_rating(self) -> None:
        """Test initialization with rating parameter."""
        message = "Invalid rating value"
        rating = 5
        error = RatingValidationError(message, rating=rating)

        assert str(error) == message
        assert error.rating == rating
        assert error.value is None

    def test_initialization_with_value(self) -> None:
        """Test initialization with value parameter."""
        message = "Value out of range"
        value = 1.5
        error = RatingValidationError(message, value=value)

        assert str(error) == message
        assert error.rating is None
        assert error.value == value

    def test_initialization_with_rating_and_value(self) -> None:
        """Test initialization with both rating and value parameters."""
        message = "PD value invalid for rating"
        rating = "A"
        value = -0.1
        error = RatingValidationError(message, rating=rating, value=value)

        assert str(error) == message
        assert error.rating == rating
        assert error.value == value

    def test_initialization_with_additional_args(self) -> None:
        """Test initialization with additional positional arguments."""
        message = "Validation error"
        rating = 3
        value = 0.8
        extra_arg = "context"

        error = RatingValidationError(message, extra_arg, rating=rating, value=value)

        assert error.rating == rating
        assert error.value == value
        assert extra_arg in str(error)

    def test_raise_and_catch_with_context(self) -> None:
        """Test raising and catching with contextual information."""
        message = "PD must be between 0 and 1"
        rating = 5
        value = 1.2

        with pytest.raises(RatingValidationError) as exc_info:
            raise RatingValidationError(message, rating=rating, value=value)

        error = exc_info.value
        assert str(error) == message
        assert error.rating == rating
        assert error.value == value


class TestRatingScaleError(BaseExceptionTest):
    """Test suite for RatingScaleError exception."""

    exception_class = RatingScaleError
    expected_base_class = KeyError

    def test_initialization_with_rating(self) -> None:
        """Test initialization with rating parameter."""
        message = "Rating not found in scale"
        rating = "X"
        error = RatingScaleError(message, rating=rating)

        assert error.rating == rating
        assert error.available_ratings == []

    def test_initialization_with_available_ratings(self) -> None:
        """Test initialization with available_ratings parameter."""
        message = "Invalid rating"
        available_ratings = ["A", "B", "C", "D"]
        error = RatingScaleError(message, available_ratings=available_ratings)

        assert error.rating is None
        assert error.available_ratings == available_ratings

    def test_initialization_with_all_parameters(self) -> None:
        """Test initialization with all optional parameters."""
        message = "Rating 'Z' not found"
        rating = "Z"
        available_ratings = [1, 2, 3, 4, 5]

        error = RatingScaleError(
            message, rating=rating, available_ratings=available_ratings
        )

        assert error.rating == rating
        assert error.available_ratings == available_ratings

    def test_available_ratings_defaults_to_empty_list(self) -> None:
        """Test that available_ratings defaults to empty list when None passed."""
        error = RatingScaleError("test", available_ratings=None)
        assert error.available_ratings == []

    def test_raise_and_catch_with_context(self) -> None:
        """Test raising and catching with contextual information."""
        message = "Rating not found"
        rating = 10
        available_ratings = [1, 2, 3, 4, 5]

        with pytest.raises(RatingScaleError) as exc_info:
            raise RatingScaleError(
                message, rating=rating, available_ratings=available_ratings
            )

        error = exc_info.value
        assert error.rating == rating
        assert error.available_ratings == available_ratings


class TestMetadataError(BaseExceptionTest):
    """Test suite for MetadataError exception."""

    exception_class = MetadataError
    expected_base_class = ValueError

    def test_initialization_with_key(self) -> None:
        """Test initialization with key parameter."""
        message = "Invalid metadata key"
        key = "invalid-key"
        error = MetadataError(message, key=key)

        assert str(error) == message
        assert error.key == key

    def test_initialization_with_additional_args(self) -> None:
        """Test initialization with additional positional arguments."""
        message = "Metadata validation failed"
        key = "problematic_key"
        extra_arg = "additional context"

        error = MetadataError(message, extra_arg, key=key)

        assert error.key == key
        assert extra_arg in str(error)

    def test_raise_and_catch_with_key(self) -> None:
        """Test raising and catching with key context."""
        message = "Key is not a valid Python identifier"
        key = "123invalid"

        with pytest.raises(MetadataError) as exc_info:
            raise MetadataError(message, key=key)

        error = exc_info.value
        assert str(error) == message
        assert error.key == key


class TestExceptionModule:
    """Test suite for the exceptions module as a whole."""

    def test_all_exports(self) -> None:
        """Test that __all__ contains all expected exceptions."""
        from credit_risk_rating import exceptions

        expected_exceptions = [
            "RatingScaleInputError",
            "RatingValidationError",
            "RatingScaleError",
            "MetadataError",
        ]

        assert hasattr(exceptions, "__all__")
        assert set(exceptions.__all__) == set(expected_exceptions)

    def test_all_exceptions_importable(self) -> None:
        """Test that all exceptions in __all__ are importable."""
        from credit_risk_rating import exceptions

        for exception_name in exceptions.__all__:
            assert hasattr(exceptions, exception_name)
            exception_class = getattr(exceptions, exception_name)
            assert issubclass(exception_class, BaseException)

    def test_author_attribute(self) -> None:
        """Test that __author__ attribute is properly set."""
        from credit_risk_rating import exceptions

        assert hasattr(exceptions, "__author__")
        assert isinstance(exceptions.__author__, list)
        assert len(exceptions.__author__) > 0


# Parametrized tests for common patterns across all exceptions
@pytest.mark.parametrize(
    "exception_class,base_class,sample_message",
    [
        (RatingScaleInputError, ValueError, "Invalid input"),
        (RatingValidationError, ValueError, "Validation failed"),
        (RatingScaleError, KeyError, "Rating not found"),
        (MetadataError, ValueError, "Metadata error"),
    ],
)
class TestCommonExceptionBehavior:
    """Parametrized tests for behavior common to all exceptions."""

    def test_inheritance(self, exception_class, base_class, sample_message) -> None:
        """Test inheritance for all exception classes."""
        assert issubclass(exception_class, base_class)

    def test_basic_instantiation(
        self, exception_class, base_class, sample_message
    ) -> None:
        """Test basic instantiation for all exception classes."""
        error = exception_class(sample_message)
        assert isinstance(error, base_class)
        assert isinstance(error, exception_class)

    def test_raise_and_catch_generic(
        self, exception_class, base_class, sample_message
    ) -> None:
        """Test raising and catching for all exception classes."""
        with pytest.raises(exception_class):
            raise exception_class(sample_message)

        with pytest.raises(base_class):
            raise exception_class(sample_message)


# Fixtures for complex exception instances
@pytest.fixture
def sample_rating_validation_error() -> RatingValidationError:
    """Fixture providing a sample RatingValidationError for testing."""
    return RatingValidationError("Sample validation error", rating=5, value=1.2)


@pytest.fixture
def sample_rating_map_error() -> RatingScaleError:
    """Fixture providing a sample RatingScaleError for testing."""
    return RatingScaleError(
        "Sample mapping error", rating="X", available_ratings=["A", "B", "C"]
    )


@pytest.fixture
def sample_metadata_error() -> MetadataError:
    """Fixture providing a sample MetadataError for testing."""
    return MetadataError("Sample metadata error", key="invalid-key")


# Integration tests using fixtures
class TestExceptionFixtures:
    """Test suite for exception fixtures and complex scenarios."""

    def test_validation_error_fixture(self, sample_rating_validation_error) -> None:
        """Test the RatingValidationError fixture."""
        error = sample_rating_validation_error
        assert isinstance(error, RatingValidationError)
        assert error.rating == 5
        assert error.value == 1.2

    def test_map_error_fixture(self, sample_rating_map_error) -> None:
        """Test the RatingScaleError fixture."""
        error = sample_rating_map_error
        assert isinstance(error, RatingScaleError)
        assert error.rating == "X"
        assert error.available_ratings == ["A", "B", "C"]

    def test_metadata_error_fixture(self, sample_metadata_error) -> None:
        """Test the MetadataError fixture."""
        error = sample_metadata_error
        assert isinstance(error, MetadataError)
        assert error.key == "invalid-key"


# Performance and edge case tests
class TestExceptionEdgeCases:
    """Test suite for exception edge cases and performance."""

    @pytest.mark.parametrize(
        "exception_class",
        [
            RatingScaleInputError,
            RatingValidationError,
            RatingScaleError,
            MetadataError,
        ],
    )
    def test_empty_message(self, exception_class) -> None:
        """Test exceptions with empty messages."""
        error = exception_class("")
        assert str(error) in ["", "''"]  # KeyError adds quotes

    @pytest.mark.parametrize(
        "exception_class",
        [
            RatingScaleInputError,
            RatingValidationError,
            RatingScaleError,
            MetadataError,
        ],
    )
    def test_unicode_message(self, exception_class) -> None:
        """Test exceptions with unicode messages."""
        unicode_message = "Error with émojis 🚫 and ünïcödé"
        error = exception_class(unicode_message)
        # String representation should contain the unicode
        assert "émojis" in str(error) or "émojis" in repr(error)

    def test_exception_chaining(self) -> None:
        """Test exception chaining with custom exceptions."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise RatingScaleInputError("Wrapped error") from e
        except RatingScaleInputError as e:
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, ValueError)
