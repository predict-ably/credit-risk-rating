"""API Classes for holding risk rating mappings and metadata.

This module provides immutable container classes for managing rating scale mappings
and metadata in credit risk applications. Both classes inherit from a common base
class that provides shared functionality for immutable dict-like behavior.

The classes are designed to be immutable after initialization, preventing accidental
modification of critical rating data while providing convenient access patterns
including dictionary-style access and attribute access for metadata.

Examples
--------
>>> from credit_risk_rating.rating.system._mappings import RatingScale, Metadata
>>> # Create a rating map
>>> rating_scale = RatingScale({1: 0.01, 2: 0.02, 3: 0.05})
>>> print(rating_scale[1])
0.01
>>> # Create metadata with attribute access
>>> metadata = Metadata({"model_version": "v2.1", "institution": "ABC Bank"})
>>> print(metadata.model_version)
"v2.1"

See Also
--------
:mod:`credit_risk_rating.rating.system._base` : Base rating scale classes
:mod:`credit_risk_rating.exceptions` : Custom exception classes
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar, Union

from credit_risk_rating.exceptions import MetadataError, RatingScaleError

__all__: list[str] = ["RatingScale", "Metadata"]
__author__: list[str] = ["RNKuhns"]

# Type alias for rating grades
RatingGrade = Union[int, str]

# Generic type variables for the base class
K = TypeVar("K")  # Key type
V = TypeVar("V")  # Value type


class _ImmutableMapping(ABC, Generic[K, V]):
    """Abstract base class for immutable mapping containers.

    This class provides common functionality for immutable dict-like containers
    that prevent modification after initialization while providing convenient
    access patterns.

    Parameters
    ----------
    data : dict[K, V] | None, optional
        Initial data for the mapping, by default None

    Attributes
    ----------
    _data : dict[K, V]
        Internal storage for the mapping data (frozen after init)
    """

    def __init__(self, data: dict[K, V] | None = None) -> None:
        """Initialize the immutable mapping."""
        # Create a deep copy to prevent external mutation
        self._data = dict(data) if data else {}
        self._validate_data()
        self._post_init_setup()
        # Mark as frozen to prevent __setattr__ from working
        object.__setattr__(self, "_frozen", True)

    @abstractmethod
    def _post_init_setup(self) -> None:
        """Set attributes dynamically for dot notation access."""
        pass

    @abstractmethod
    def _validate_data(self) -> None:
        """Validate the data during initialization.

        Subclasses should implement this to add specific validation logic.
        """
        pass

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent modification after initialization (immutable)."""
        # Allow setting during __init__
        if not hasattr(self, "_frozen"):
            object.__setattr__(self, name, value)
        else:
            class_name = self.__class__.__name__
            raise AttributeError(
                f"{class_name} objects are immutable. "
                f"Use add() or similar methods to create a new instance."
            )

    def __getitem__(self, key: K) -> V:
        """Dictionary-style access."""
        return self._data[key]

    def __contains__(self, key: K) -> bool:
        """Check if key exists."""
        return key in self._data

    def __iter__(self):
        """Iterate over keys."""
        return iter(self._data)

    def __len__(self) -> int:
        """Number of items in the mapping."""
        return len(self._data)

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, self.__class__):
            return False
        return self._data == other._data

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}({self._data})"

    def keys(self) -> tuple[K, ...]:
        """Get all keys."""
        return tuple(self._data.keys())

    def values(self) -> tuple[V, ...]:
        """Get all values."""
        return tuple(self._data.values())

    def items(self) -> list[tuple[K, V]]:
        """Get all key-value pairs."""
        return list(self._data.items())

    def to_dict(self) -> dict[K, V]:
        """Convert to regular dictionary.

        Returns
        -------
        dict[K, V]
            A new dictionary with the same key-value pairs
        """
        return dict(self._data)

    def to_json(self, indent: int = 2) -> str:
        """Export to a JSON string.

        Converts the _ImmutableMapping to a JSON string representation using
        the to_dict() method. The resulting JSON can be used for storage,
        transmission, or reconstruction of the _ImmutableMapping.

        Parameters
        ----------
        indent : int
            The number of spaces to indent the json hierarchy.

        Returns
        -------
        str
            JSON string representation of the rating system

        Examples
        --------
        >>> # Assuming 'system' is a rating system instance
        >>> json_str = system.to_json()
        >>> print(json_str)
        {
          "rating_system_type": "MyRatingSystem",
          "metadata": {...},
          ...
        }
        """
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict[K, V] | None = None):
        """Create instance from dictionary.

        Parameters
        ----------
        data : dict[K, V] | None, optional
            Data for the mapping, by default None

        Returns
        -------
        _ImmutableMapping
            New instance of the class
        """
        return cls(data)

    def _add_items(self, additional_items: dict[K, V]):
        """Generic method to add items and return new instance.

        This method provides the common functionality for adding new items
        to the mapping. Subclasses can use this in their specific add methods.

        Parameters
        ----------
        additional_items : dict[K, V]
            Dictionary of new items to add

        Returns
        -------
        _ImmutableMapping
            New instance with existing + new items

        Notes
        -----
        If keys overlap, additional_items values will override existing values.
        """
        combined_data = dict(self._data)  # Copy existing
        combined_data.update(additional_items)  # Add new data
        return self.__class__(combined_data)


class RatingScale(_ImmutableMapping[RatingGrade, float]):
    """Immutable mapping from rating grades to rating values.

    This class provides an immutable container for rating scale mappings where
    rating grades (int or str) map to numeric rating values (float). The mapping
    is frozen after initialization to prevent accidental modification of critical
    rating data.

    Parameters
    ----------
    rating_scale : dict[RatingGrade, float] | None
        Rating scale mapping.

    Attributes
    ----------
    rating_scale : dict[RatingGrade, float]
        The rating scale mapping (read-only property)

    Examples
    --------
    >>> rating_map = RatingScale({1: 0.01, 2: 0.02, 3: 0.05})
    >>> rating_map[1]
    0.01
    >>> rating_map.get_grade_value(2)
    0.02
    >>> len(rating_map)
    3

    >>> # Create subset
    >>> subset = rating_map.subset_grades([1, 2])
    >>> len(subset)
    2

    >>> # Add more grades
    >>> expanded = rating_map.add_rating_grades({4: 0.10, 5: 0.15})
    >>> len(expanded)
    5
    """

    def __init__(self, rating_scale: dict[RatingGrade, float] | None = None) -> None:
        """Initialize rating map with optional dictionary."""
        super().__init__(rating_scale)

    @abstractmethod
    def _post_init_setup(self) -> None:
        """Set attributes dynamically for dot notation access."""
        return None

    def _validate_data(self) -> None:
        """Validate that grades are string or integer values and values are float."""
        grade_errors, value_errors = [], []
        for grade, value in self._data.items():
            if not isinstance(grade, (str, int)):
                grade_errors.append(grade)
            if not isinstance(value, (float)):
                value_errors.append(value)

        if grade_errors or value_errors:
            raise TypeError(
                "Error in rating grades or values.\n"
                "Grades must be str or int and values must be float.\n"
                f"Rating grade errors: {', '.join([grade_errors])}.\n",
                f"Rating value errors: {', '.join([value_errors])}.",
            )

    @property
    def rating_scale(self) -> dict[RatingGrade, float]:
        """The rating scale mapping rating grades to rating values.

        Returns
        -------
        dict[RatingGrade, float]
            A copy of the internal rating scale mapping
        """
        return dict(self._data)

    def rating_grades(self) -> tuple[RatingGrade]:
        """Get all rating grades.

        Returns
        -------
        list[RatingGrade]
            List of all rating grades in the mapping
        """
        return self.keys()

    def rating_values(self) -> tuple[float]:
        """Get all rating values.

        Returns
        -------
        list[float]
            List of all rating values in the mapping
        """
        return self.values()

    def rating_grade_value_pairs(self) -> list[tuple[RatingGrade, float]]:
        """Get all grade-value pairs.

        Returns
        -------
        list[tuple[RatingGrade, float]]
            List of (grade, value) tuples
        """
        return self.items()

    @classmethod
    def from_dict(
        cls, rating_scale: dict[RatingGrade, float] | None = None
    ) -> RatingScale:
        """Create RatingScale from dictionary.

        Parameters
        ----------
        rating_scale : dict[RatingGrade, float] | None, optional
            Rating scale mapping, by default None

        Returns
        -------
        RatingScale
            New RatingScale instance
        """
        return super().from_dict(rating_scale)

    def subset_grades(self, grades: RatingGrade | list[RatingGrade]) -> RatingScale:
        """Create new RatingScale with subset of rating grades.

        Parameters
        ----------
        grades : RatingGrade | list[RatingGrade]
            Single rating grade or list of grades to include

        Returns
        -------
        RatingScale
            New RatingScale object with only specified grades

        Raises
        ------
        RatingScaleError
            If any requested grades are not found (reports all missing grades)
        """
        if not isinstance(grades, list):
            grades = [grades]

        # Validate all grades exist before creating subset
        missing_grades = [grade for grade in grades if grade not in self._data]
        if missing_grades:
            available_grades = list(self._data.keys())
            raise RatingScaleError(
                f"Rating grades not found: {missing_grades}",
                f"Available rating grades: {available_grades}",
            )

        # Create subset
        subset_data = {grade: self._data[grade] for grade in grades}
        return self.from_dict(rating_scale=subset_data)

    def add_rating_grades(
        self, additional_grades: dict[RatingGrade, float]
    ) -> RatingScale:
        """Create new RatingScale with additional grade-value pairs.

        Parameters
        ----------
        additional_grades : dict[RatingGrade, float]
            Dictionary of new rating mappings to add

        Returns
        -------
        RatingScale
            New RatingScale object with existing + new data

        Notes
        -----
        If rating grades overlap in the existing and new rating grades,
        the additional_grades values will override existing values.
        """
        return self._add_items(additional_grades)

    def get_grade_value(self, grade: RatingGrade) -> float:
        """Get rating value for a grade.

        Parameters
        ----------
        grade : RatingGrade
            The rating grade to look up

        Returns
        -------
        float
            The rating value for the specified grade

        Raises
        ------
        KeyError
            If the grade is not found in the mapping
        """
        return self._data[grade]

    def has_grade(self, grade: RatingGrade) -> bool:
        """Check if rating grade exists.

        Parameters
        ----------
        grade : RatingGrade
            The rating grade to check

        Returns
        -------
        bool
            True if the grade exists, False otherwise
        """
        return grade in self._data


class Metadata(_ImmutableMapping[str, Any]):
    """Immutable metadata container with attribute access.

    This class provides an immutable container for metadata with both dictionary-style
    access and attribute access. Keys must be valid Python identifiers to support
    attribute access. It also has methods to subset and add metadata, with each
    returning a new metadata object rather than updating the existing object.

    Parameters
    ----------
    metadata : dict[str, Any] | None
        Initial metadata dictionary, by default None.

    Attributes
    ----------
    metadata : dict[str, Any]
        The metadata dictionary (read-only property).

    Examples
    --------
    >>> metadata = Metadata({"model_version": "v2.1", "institution": "ABC Bank"})
    >>> metadata.model_version
    "v2.1"
    >>> metadata["institution"]
    "ABC Bank"
    >>> len(metadata)
    2

    >>> # Create subset
    >>> subset = metadata.subset_metadata(["model_version"])
    >>> len(subset)
    1

    >>> # Add more metadata
    >>> expanded = metadata.add_metadata({"calibration_date": "2024-01-01"})
    >>> len(expanded)
    3
    """

    def __init__(self, metadata: dict[str, Any] | None = None) -> None:
        """Initialize metadata with optional dictionary."""
        super().__init__(metadata)
        for key, value in self._data.items():
            object.__setattr__(self, key, value)

    def _validate_data(self) -> None:
        """Validate that all keys are valid Python identifiers."""
        key_errors = []
        for key in self._data.keys():
            err_msg = ""
            if not isinstance(key, str):
                err_msg = f"Metadata key must be string, got {type(key).__name__}"
            if not key.isidentifier():
                err_msg += f"Metadata key '{key}' is not a valid Python identifier"
            if err_msg != "":
                key_errors.append(
                    f"Metadata key must be string, got {type(key).__name__}"
                )
        raise MetadataError(
            "Some metadata keys are not strings and valid Python identifiers."
            f"Metadata key errors: {', '.join(key_errors)}.",
        )

    def _post_init_setup(self) -> None:
        """Set attributes dynamically for dot notation access."""
        for key, value in self._data.items():
            object.__setattr__(self, key, value)
        return None

    @property
    def metadata(self) -> dict[str, Any]:
        """The metadata dictionary mapping metadata items to values.

        Returns
        -------
        dict[str, Any]
            A copy of the internal metadata dictionary.
        """
        return dict(self._data)

    def metadata_items(self) -> list[str]:
        """Get all metadata item names.

        Returns
        -------
        list[str]
            List of all metadata item names.
        """
        return self.keys()

    def metadata_values(self) -> list[Any]:
        """Get all metadata values.

        Returns
        -------
        list[Any]
            List of all metadata values.
        """
        return self.values()

    def metadata_item_value_pairs(self) -> list[tuple[str, Any]]:
        """Get all metadata item-value pairs.

        Returns
        -------
        list[tuple[str, Any]]
            List of (item, value) tuples.
        """
        return self.items()

    @classmethod
    def from_dict(cls, metadata: dict[str, Any] | None = None) -> Metadata:
        """Create Metadata from dictionary.

        Parameters
        ----------
        metadata : dict[str, Any] | None
            Metadata dictionar.

        Returns
        -------
        Metadata
            New Metadata instance.
        """
        return super().from_dict(metadata)

    def subset_metadata(self, metadata_items: str | list[str]) -> Metadata:
        """Create new Metadata with subset of metadata items.

        Parameters
        ----------
        metadata_items : str | list[str]
            Metadata item or list of metadata items to include.

        Returns
        -------
        Metadata
            New Metadata object with only specified items.

        Raises
        ------
        MetadataError
            If any requested metadata items are not found.
        """
        if not isinstance(metadata_items, list):
            metadata_items = [metadata_items]

        # Validate all keys exist before creating subset
        missing_keys = [item for item in metadata_items if item not in self._data]
        if missing_keys:
            available_keys = list(self._data.keys())
            raise MetadataError(
                f"Keys not found in metadata: {missing_keys}. "
                f"Available keys: {available_keys}",
                key=missing_keys[0] if len(missing_keys) == 1 else None,
            )

        # Create subset
        subset_data = {key: self._data[key] for key in metadata_items}
        return self.__class__(subset_data)

    def add_metadata(self, additional_metadata: dict[str, Any]) -> Metadata:
        """Create new Metadata with additional metadata item-value pairs.

        Parameters
        ----------
        additional_metadata : dict[str, Any]
            Dictionary of new metadata to add.

        Returns
        -------
        Metadata
            New Metadata object with existing + new metadata.

        Notes
        -----
        If new and existing metadata items overlap, additional_metadata values
        will override existing values.
        """
        return self._add_items(additional_metadata)

    def has_metadata(self, metadata: str) -> bool:
        """Check if rating grade exists.

        Parameters
        ----------
        metadata : str
            The metadata key to check.

        Returns
        -------
        bool
            True if the grade exists, False otherwise.
        """
        return metadata in self._data
