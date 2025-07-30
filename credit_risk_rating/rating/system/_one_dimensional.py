"""One-dimensional rating systems implementation.

This module provides the OneDimensionalRatingSystem class for managing rating
systems that use a single scale to rate entities. Examples include credit ratings,
internal risk ratings, and regulatory classification systems.

The module includes factory methods for creating custom one-dimensional rating
systems with configurable requirements and validation rules.

Examples
--------
>>> from credit_risk_rating.rating.system._one_dimensional import \
    OneDimensionalRatingSystem
>>> from credit_risk_rating.rating.system._base import RatingSystemConfig
>>>
>>> # Create custom rating system class
>>> config = RatingSystemConfig(
...     required_grades=["A", "B", "C", "D", "F"],
...     required_metadata=["institution", "portfolio"]
... )
>>> MySystem = OneDimensionalRatingSystem.create_custom_class("MySystem", config)
>>>
>>> # Create instance
>>> system = MySystem(
...     rating_scale={"A": 0.01, "B": 0.05, "C": 0.10, "D": 0.25, "F": 0.60},
...     metadata={"institution": "ABC Bank", "portfolio": "Commercial"}
... )

See Also
--------
credit_risk_rating.rating.system._base : Base classes and configurations
credit_risk_rating.rating.system._two_dimensional : Two-dimensional rating systems
credit_risk_rating.rating.system._predefined : Pre-built industry standard systems
"""

from __future__ import annotations

from typing import Any

from credit_risk_rating.exceptions import RatingScaleInputError, RatingValidationError
from credit_risk_rating.rating.system._base import BaseRatingSystem, RatingSystemConfig
from credit_risk_rating.rating.system._mappings import Metadata, RatingGrade, RatingMap

__all__: list[str] = ["OneDimensionalRatingSystem"]
__author__: list[str] = ["RNKuhns"]


class OneDimensionalRatingSystem(BaseRatingSystem):
    """One-dimensional rating system with a single rating scale.

    This class manages rating systems that use a single dimension (scale)
    to rate entities. The system validates that the rating scale contains
    exactly the required grades as specified in the class configuration.

    Parameters
    ----------
    rating_scale : dict[RatingGrade, float] | RatingMap | None, optional
        Rating scale mapping grades to values, by default None
    metadata : dict[str, Any] | Metadata | None, optional
        Metadata about the rating system, by default None

    Attributes
    ----------
    rating_scale : RatingMap
        Immutable rating scale mapping
    metadata : Metadata
        Immutable metadata container

    Examples
    --------
    >>> # Create with dictionary input
    >>> system = OneDimensionalRatingSystem(
    ...     rating_scale={"A": 0.01, "B": 0.05, "C": 0.10},
    ...     metadata={"institution": "ABC Bank"}
    ... )

    >>> # Access grades and values
    >>> system.rating_grades  # ["A", "B", "C"]
    >>> system.rating_scale["A"]  # 0.01
    >>> system.is_valid_rating("A")  # True
    """

    def __init__(
        self,
        rating_scale: dict[RatingGrade, float] | RatingMap | None = None,
        metadata: dict[str, Any] | Metadata | None = None,
    ):
        """Initialize one-dimensional rating system.

        Parameters
        ----------
        rating_scale : dict[RatingGrade, float] | RatingMap | None, optional
            Rating scale mapping grades to values, by default None
        metadata : dict[str, Any] | Metadata | None, optional
            Metadata about the rating system, by default None
        """
        # Process rating scale input
        self.rating_scale = self._process_rating_scale_input(rating_scale)

        # Initialize metadata (calls validation)
        super().__init__(metadata)

        # Validate rating scale requirements
        self._validate_required_grades()

    def _process_rating_scale_input(
        self, rating_scale: dict[RatingGrade, float] | RatingMap | None
    ) -> RatingMap:
        """Process and validate rating scale input.

        Converts various rating scale input types into a standardized RatingMap
        object, ensuring type safety and consistency.

        Parameters
        ----------
        rating_scale : dict[RatingGrade, float] | RatingMap | None
            Input rating scale to process

        Returns
        -------
        RatingMap
            Processed rating scale object

        Raises
        ------
        RatingScaleInputError
            If rating scale input is invalid type
        """
        if isinstance(rating_scale, RatingMap):
            return rating_scale
        elif isinstance(rating_scale, dict) or rating_scale is None:
            return RatingMap.from_dict(rating_scale)
        else:
            raise RatingScaleInputError(
                f"Expected rating_scale parameter to have type dict or RatingMap. "
                f"Found type {type(rating_scale)} instead."
            )

    def _validate_required_grades(self) -> None:
        """Validate that rating scale contains exactly the required grades.

        Checks that the rating scale contains exactly the grades specified in
        the class configuration - no more, no less. This ensures compliance
        with the rating system requirements.

        Raises
        ------
        RatingValidationError
            If required grades are missing or extra grades are present
        """
        if not hasattr(self, "_CONFIG") or not self._CONFIG:
            return  # No requirements to validate

        required_grades = self._CONFIG.get("required_grades", [])
        if not required_grades:
            return  # No grade requirements

        actual_grades = set(self.rating_scale.rating_grades())
        required_grades_set = set(required_grades)

        missing_grades = required_grades_set - actual_grades
        extra_grades = actual_grades - required_grades_set

        error_messages = []

        if missing_grades:
            error_messages.append(f"Missing required grades: {sorted(missing_grades)}")

        if extra_grades:
            error_messages.append(f"Extra grades not allowed: {sorted(extra_grades)}")

        if error_messages:
            error_messages.append(f"Required grades: {required_grades}")
            error_messages.append(f"Actual grades: {sorted(actual_grades)}")

            raise RatingValidationError(
                "Rating scale validation failed:\n"
                + "\n".join(f"  - {msg}" for msg in error_messages)
            )

    @property
    def rating_grades(self) -> list[RatingGrade]:
        """Get the ordered list of rating grades.

        Returns
        -------
        list[RatingGrade]
            List of rating grades in the scale
        """
        return self.rating_scale.rating_grades()

    @property
    def rating_values(self) -> list[float]:
        """Get the ordered list of rating values.

        Returns
        -------
        list[float]
            List of rating values in the scale
        """
        return self.rating_scale.rating_values()

    def get_rating_grades(self) -> list[RatingGrade]:
        """Get the rating grades for this system.

        Implementation of the abstract method from BaseRatingSystem.
        For one-dimensional systems, this returns the list of grades.

        Returns
        -------
        list[RatingGrade]
            List of rating grades in the scale
        """
        return self.rating_grades

    def is_valid_rating(self, rating: RatingGrade) -> bool:
        """Check if a rating is valid for this scale.

        Parameters
        ----------
        rating : RatingGrade
            Rating grade to validate

        Returns
        -------
        bool
            True if rating is valid, False otherwise

        Examples
        --------
        >>> system = OneDimensionalRatingSystem(rating_scale={"A": 0.01, "B": 0.05})
        >>> system.is_valid_rating("A")  # True
        >>> system.is_valid_rating("C")  # False
        """
        return self.rating_scale.has_grade(rating)

    def get_rating_position(self, rating_grade: RatingGrade) -> int:
        """Get the position of a rating in the scale (0-indexed).

        Parameters
        ----------
        rating_grade : RatingGrade
            Rating grade to find position for

        Returns
        -------
        int
            Zero-indexed position of the rating in the scale

        Raises
        ------
        ValueError
            If rating grade is not found in the scale

        Examples
        --------
        >>> system = OneDimensionalRatingSystem(rating_scale={"A": 0.01, "B": 0.05, "C": 0.10})
        >>> system.get_rating_position("B")  # 1
        """
        if not self.is_valid_rating(rating_grade):
            raise ValueError(f"Rating {rating_grade} not found in rating scale.")
        return self.rating_grades.index(rating_grade)

    def get_rating_value(self, rating_grade: RatingGrade) -> float:
        """Get the numeric value for a rating grade.

        Parameters
        ----------
        rating_grade : RatingGrade
            Rating grade to get value for

        Returns
        -------
        float
            Numeric value associated with the rating grade

        Raises
        ------
        KeyError
            If rating grade is not found in the scale

        Examples
        --------
        >>> system = OneDimensionalRatingSystem(rating_scale={"A": 0.01, "B": 0.05})
        >>> system.get_rating_value("A")  # 0.01
        """
        return self.rating_scale[rating_grade]

    def to_dict(self) -> dict[str, Any]:
        """Export rating system to dictionary representation.

        Creates a complete dictionary representation of the rating system
        that includes all necessary information for reconstruction and
        serialization.

        Returns
        -------
        dict[str, Any]
            Dictionary containing rating system data

        Examples
        --------
        >>> system = OneDimensionalRatingSystem(
        ...     rating_scale={"A": 0.01, "B": 0.05},
        ...     metadata={"institution": "ABC Bank"}
        ... )
        >>> data = system.to_dict()
        >>> data['rating_system_type']  # 'OneDimensionalRatingSystem'
        """
        return {
            "rating_system_type": self.__class__.__name__,
            "rating_scale": self.rating_scale.to_dict(),
            "metadata": self.metadata.to_dict(),
            "config": self.get_config(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OneDimensionalRatingSystem:
        """Create rating system from dictionary representation.

        Reconstructs a rating system instance from a dictionary representation,
        typically created by the to_dict() method.

        Parameters
        ----------
        data : dict[str, Any]
            Dictionary containing rating system data

        Returns
        -------
        OneDimensionalRatingSystem
            Rating system instance created from dictionary

        Examples
        --------
        >>> data = {
        ...     "rating_scale": {"A": 0.01, "B": 0.05},
        ...     "metadata": {"institution": "ABC Bank"}
        ... }
        >>> system = OneDimensionalRatingSystem.from_dict(data)
        """
        return cls(
            rating_scale=data.get("rating_scale", {}), metadata=data.get("metadata", {})
        )

    @classmethod
    def create_custom_class(
        cls, name: str, config: RatingSystemConfig
    ) -> type[OneDimensionalRatingSystem]:
        """Create a custom one-dimensional rating system class.

        This factory method creates a new rating system class with the specified
        configuration. The resulting class can be used like any built-in rating
        system class and will enforce the provided requirements.

        Parameters
        ----------
        name : str
            Name for the new rating system class
        config : RatingSystemConfig
            Configuration specifying requirements for the rating system

        Returns
        -------
        type[OneDimensionalRatingSystem]
            New rating system class with the specified configuration

        Raises
        ------
        RatingScaleInputError
            If configuration is missing required fields

        Examples
        --------
        >>> from credit_risk_rating.rating.system._base import RatingSystemConfig
        >>> config = RatingSystemConfig(
        ...     required_grades=["A", "B", "C", "D", "F"],
        ...     required_metadata=["institution", "portfolio"],
        ...     name="Custom Bank Rating System",
        ...     description="Internal rating system for ABC Bank"
        ... )
        >>> MySystem = OneDimensionalRatingSystem.create_custom_class(
        ...     name="MyBankRatingSystem",
        ...     config=config
        ... )
        >>>
        >>> # Use the new class
        >>> system = MySystem(
        ...     rating_scale={"A": 0.01, "B": 0.05, "C": 0.10, "D": 0.25, "F": 0.60},
        ...     metadata={"institution": "ABC Bank", "portfolio": "Commercial"}
        ... )
        """
        # Validate configuration
        if "required_grades" not in config:
            raise RatingScaleInputError("Configuration must include 'required_grades'")

        # Create new class dynamically
        class_attrs = {
            "_CONFIG": config.copy(),
            "__module__": cls.__module__,
            "__qualname__": name,
        }

        new_class = type(name, (cls,), class_attrs)
        return new_class
