"""Exceptions used in credit_risk_rating package.

This module defines custom exception classes used throughout the credit_risk_rating
package to provide specific error handling for rating scale operations, validation
failures, and data integrity issues.

The exceptions in this module inherit from standard Python exceptions but provide
more specific error context for credit risk rating operations, making debugging
and error handling more clear.

Examples
--------
>>> from credit_risk_rating.exceptions import RatingScaleInputError
>>> try:
...     # Some rating scale operation that fails
...     pass
... except RatingScaleInputError as e:
...     print(f"Rating scale input error: {e}")

See Also
--------
:mod:`credit_risk_rating.rating` : Main rating scale classes
"""

from __future__ import annotations

__all__: list[str] = [
    "RatingScaleInputError",
    "RatingValidationError",
    "RatingScaleError",
    "MetadataError",
]
__author__: list[str] = ["RNKuhns"]


class RatingScaleInputError(ValueError):
    """Exception raised for invalid input to RatingScale classes.

    This exception is raised when input parameters to rating scale constructors
    or methods are invalid, malformed, or inconsistent with expected formats.

    Parameters
    ----------
    message : str
        Human readable string describing the exception.
    *args : tuple
        Variable length argument list passed to the base ValueError.
    **kwargs : dict
        Arbitrary keyword arguments passed to the base ValueError.

    Examples
    --------
    >>> raise RatingScaleInputError("Invalid rating grades")
    Traceback (most recent call last):
        ...
    credit_risk_rating.exceptions.RatingScaleInputError: Invalid rating grades

    >>> try:
    ...     # Code that validates rating scale input
    ...     if not valid_input:
    ...         raise RatingScaleInputError("Rating grades must be unique")
    ... except RatingScaleInputError as e:
    ...     print(f"Input validation failed: {e}")
    """


class RatingValidationError(ValueError):
    """Exception raised when rating values fail validation checks.

    This exception is raised when rating values (PD, LGD) are outside acceptable
    ranges, fail monotonicity checks, or violate other business rules.

    Parameters
    ----------
    message : str
        Human readable string describing the validation failure.
    rating : str or int, optional
        The specific rating that failed validation, if applicable.
    value : float, optional
        The specific value that failed validation, if applicable.
    *args : tuple
        Variable length argument list passed to the base ValueError.
    **kwargs : dict
        Arbitrary keyword arguments passed to the base ValueError.

    Examples
    --------
    >>> raise RatingValidationError("Valid PDs are between 0 and 1",
    ...                           rating=5, value=1.5)
    Traceback (most recent call last):
        ...
    credit_risk_rating.exceptions.RatingValidationError: Valid PDs are between 0 and 1
    """

    def __init__(
        self,
        message: str,
        rating: str | int | None = None,
        value: float | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Initialize RatingValidationError with optional context."""
        super().__init__(message, *args, **kwargs)
        self.rating = rating
        self.value = value


class RatingScaleError(KeyError):
    """Exception raised for errors in rating-to-value mappings.

    This exception is raised when attempting to access ratings that don't exist
    in the rating scale, or when rating mappings are inconsistent or malformed.

    Parameters
    ----------
    message : str
        Human readable string describing the mapping error.
    rating : str or int, optional
        The specific rating that caused the mapping error, if applicable.
    available_ratings : list, optional
        List of available ratings in the scale, if applicable.
    *args : tuple
        Variable length argument list passed to the base KeyError.
    **kwargs : dict
        Arbitrary keyword arguments passed to the base KeyError.

    Examples
    --------
    >>> raise RatingScaleError("Rating 'X' not found in scale",
    ...                      rating='X', available_ratings=['A', 'B', 'C'])
    Traceback (most recent call last):
        ...
    credit_risk_rating.exceptions.RatingScaleError: Rating 'X' not found in scale
    """

    def __init__(
        self,
        message: str,
        rating: str | int | None = None,
        available_ratings: list | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Initialize RatingScaleError with optional context."""
        super().__init__(message, *args, **kwargs)
        self.rating = rating
        self.available_ratings = available_ratings or []


class MetadataError(ValueError):
    """Exception raised for metadata-related errors.

    This exception is raised when metadata operations fail, such as invalid
    keys, subsetting errors, or attribute access issues.

    Parameters
    ----------
    message : str
        Human readable string describing the metadata error.
    key : str, optional
        The specific metadata key that caused the error, if applicable.
    *args : tuple
        Variable length argument list passed to the base ValueError.
    **kwargs : dict
        Arbitrary keyword arguments passed to the base ValueError.

    Examples
    --------
    >>> raise MetadataError("Metadata key 'key1' is not a valid",
    ...                    key='key1')
    Traceback (most recent call last):
        ...
    credit_risk_rating.exceptions.MetadataError: Metadata key 'key1' is not a valid
    """

    def __init__(self, message: str, key: str | None = None, *args, **kwargs) -> None:
        """Initialize MetadataError with optional context."""
        super().__init__(message, *args, **kwargs)
        self.key = key
