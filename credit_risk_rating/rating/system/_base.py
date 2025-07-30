"""Core rating system abstractions and configurations.

This module provides the base classes, type definitions, and common functionality
for all rating systems in the credit risk management package. It defines the
abstract interfaces and shared validation logic used by concrete rating system
implementations.

Examples
--------
>>> from credit_risk_rating.rating.system._base import BaseRatingSystem, \
RatingSystemConfig
>>> config = RatingSystemConfig(
...     required_grades=["A", "B", "C", "D", "F"],
...     required_metadata=["institution", "model_version"]
... )

See Also
--------
credit_risk_rating.rating.system._one_dimensional : One-dimensional rating systems
credit_risk_rating.rating.system._two_dimensional : Two-dimensional rating systems
credit_risk_rating.rating.system._predefined : Pre-built industry standard systems
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, TypedDict

from credit_risk_rating.exceptions import RatingScaleInputError, RatingValidationError
from credit_risk_rating.rating.system._mappings import Metadata, RatingGrade

__all__: list[str] = [
    "RatingSystemConfig",
    "PDLGDRatingSystemConfig",
    "BaseRatingSystem",
]
__author__: list[str] = ["RNKuhns"]


class RatingSystemConfig(TypedDict, total=False):
    """Configuration dictionary for one-dimensional rating systems.

    This TypedDict defines the structure for configuring one-dimensional rating
    systems, specifying requirements and metadata for validation.

    Attributes
    ----------
    required_grades : list[RatingGrade]
        Exhaustive list of required rating grades. The rating system must
        contain exactly these grades, no more and no less.
    required_metadata : list[str]
        List of required metadata field names that must be present.
    name : str, optional
        Human-readable name for the rating system.
    description : str, optional
        Detailed description of the rating system.
    reference_url : str, optional
        URL to official documentation or specification.

    Examples
    --------
    >>> config = RatingSystemConfig(
    ...     required_grades=["A", "B", "C", "D", "F"],
    ...     required_metadata=["institution", "portfolio"],
    ...     name="Custom Bank Rating System",
    ...     description="Internal rating system for credit assessment"
    ... )
    """

    required_grades: list[RatingGrade]
    required_metadata: list[str]
    name: str
    description: str
    reference_url: str


class TwoDimensionsalRatingSystemConfig(TypedDict, total=False):
    """Configuration dictionary for two-dimensional PD/LGD rating systems.

    This TypedDict defines the structure for configuring two-dimensional rating
    systems that include both Probability of Default (PD) and Loss Given Default
    (LGD) dimensions.

    Attributes
    ----------
    required_grade_dimensions : dict[str, list[RatingGrade]]
        Dictionary specifying required grades for each dimension.
        Must contain 'pd' and 'lgd' keys with exhaustive grade lists.
    required_metadata : list[str]
        List of required metadata field names that must be present.
    name : str, optional
        Human-readable name for the rating system.
    description : str, optional
        Detailed description of the rating system.
    reference_url : str, optional
        URL to official documentation or specification.

    Examples
    --------
    >>> config = PDLGDRatingSystemConfig(
    ...     required_grade_dimensions={
    ...         "pd": [1, 2, 3, 4, 5],
    ...         "lgd": ["A", "B", "C"]
    ...     },
    ...     required_metadata=["institution", "model_version"],
    ...     name="Custom PD/LGD System"
    ... )
    """

    required_grade_dimensions: dict[str, list[RatingGrade]]
    required_metadata: list[str]
    name: str
    description: str
    reference_url: str


class BaseRatingSystem(ABC):
    """Abstract base class for all rating systems.

    This class provides common functionality for rating system validation,
    serialization, and metadata management. Subclasses implement specific
    logic for one-dimensional or multi-dimensional rating systems.

    The base class handles metadata processing and validation, leaving rating
    scale validation to concrete implementations.

    Parameters
    ----------
    metadata : dict[str, Any] | Metadata | None, optional
        Metadata about the rating system instance, by default None

    Attributes
    ----------
    metadata : Metadata
        Immutable metadata container for the rating system

    Examples
    --------
    This is an abstract class and cannot be instantiated directly.
    See OneDimensionalRatingSystem or PDLGDRatingSystem for concrete examples.
    """

    # Subclasses should override this with their configuration
    _CONFIG: RatingSystemConfig | TwoDimensionsalRatingSystemConfig = {}

    def __init__(self, metadata: dict[str, Any] | Metadata | None = None):
        """Initialize the base rating system.

        Parameters
        ----------
        metadata : dict[str, Any] | Metadata | None, optional
            Metadata about the rating system, by default None
        """
        self.metadata = self._process_metadata_input(metadata)
        self._validate_required_metadata()

    def _process_metadata_input(
        self, metadata: dict[str, Any] | Metadata | None
    ) -> Metadata:
        """Process and validate metadata input.

        Converts various metadata input types into a standardized Metadata object,
        ensuring type safety and consistency across the rating system.

        Parameters
        ----------
        metadata : dict[str, Any] | Metadata | None
            Input metadata to process

        Returns
        -------
        Metadata
            Processed metadata object

        Raises
        ------
        RatingScaleInputError
            If metadata input is invalid type
        """
        if isinstance(metadata, Metadata):
            return metadata
        elif isinstance(metadata, dict) or metadata is None:
            return Metadata.from_dict(metadata)
        else:
            raise RatingScaleInputError(
                f"Expected metadata parameter to have type dict or Metadata. "
                f"Found type {type(metadata)} instead."
            )

    def _validate_required_metadata(self) -> None:
        """Validate that all required metadata fields are present.

        Checks the class configuration to determine required metadata fields
        and validates that all required fields are present in the instance
        metadata.

        Raises
        ------
        RatingValidationError
            If required metadata fields are missing
        """
        if not hasattr(self, "_CONFIG") or not self._CONFIG:
            return None  # No requirements to validate

        required_metadata = self._CONFIG.get("required_metadata", [])
        if not required_metadata:
            return None  # No metadata requirements

        missing_metadata = [
            field for field in required_metadata if field not in self.metadata
        ]

        if missing_metadata:
            available_metadata = list(self.metadata.keys())
            raise RatingValidationError(
                f"Missing required metadata fields: {missing_metadata}. "
                f"Required: {required_metadata}. "
                f"Available: {available_metadata}"
            )

    @abstractmethod
    def get_rating_grades(self) -> list[RatingGrade] | dict[str, list[RatingGrade]]:
        """Get the rating grades for this system.

        This method must be implemented by subclasses to return the rating
        grades in the appropriate format for the system type.

        Returns
        -------
        list[RatingGrade] | dict[str, list[RatingGrade]]
            For one-dimensional systems, returns list of grades.
            For multi-dimensional systems, returns dict with dimension names as keys.
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Export rating system to dictionary representation.

        This method must be implemented by subclasses to provide a complete
        dictionary representation of the rating system that can be used for
        serialization and reconstruction.

        Returns
        -------
        dict[str, Any]
            Dictionary representation of the rating system
        """
        pass

    def to_json(self, indent: int = 2) -> str:
        """Export rating system to JSON string.

        Converts the rating system to a JSON string representation using
        the to_dict() method. The resulting JSON can be used for storage,
        transmission, or reconstruction of the rating system.

        Parameters
        ----------
        indent : int, default=2
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
    def get_config(cls) -> RatingSystemConfig | TwoDimensionsalRatingSystemConfig:
        """Get the configuration for this rating system class.

        Returns a copy of the class configuration dictionary, which defines
        the requirements and metadata for instances of this rating system.

        Returns
        -------
        RatingSystemConfig | PDLGDRatingSystemConfig
            Configuration dictionary for this rating system

        Examples
        --------
        >>> from credit_risk_rating.rating.system._predefined import \
            UniformClassificationSystem
        >>> config = UniformClassificationSystem.get_config()
        >>> print(config['required_grades'])
        ['Acceptable', 'Special Mention', 'Substandard', 'Doubtful', 'Loss']
        """
        return cls._CONFIG.copy() if cls._CONFIG else {}
