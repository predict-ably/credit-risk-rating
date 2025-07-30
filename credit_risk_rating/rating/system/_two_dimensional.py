"""Two-dimensional rating systems implementation.

This module provides the PDLGDRatingSystem class for managing rating systems
that use two dimensions: Probability of Default (PD) and Loss Given Default (LGD).
This is common in banking systems where both default probability and loss severity
are rated separately.

The module includes factory methods for creating custom two-dimensional rating
systems with configurable requirements for both dimensions.

Examples
--------
>>> from credit_risk_rating.rating.system._two_dimensional import \
    PDLGDRatingSystem
>>> from credit_risk_rating.rating.system._base import PDLGDRatingSystemConfig
>>>
>>> # Create custom two-dimensional rating system class
>>> config = PDLGDRatingSystemConfig(
...     required_grade_dimensions={
...         "pd": [1, 2, 3, 4, 5],
...         "lgd": ["A", "B", "C"]
...     },
...     required_metadata=["institution", "model_version"]
... )
>>> MySystem = PDLGDRatingSystem.create_custom_class("MyPDLGDSystem", config)
>>>
>>> # Create instance
>>> system = MySystem(
...     pd_rating_scale={1: 0.001, 2: 0.005, 3: 0.010, 4: 0.025, 5: 0.050},
...     lgd_rating_scale={"A": 0.10, "B": 0.25, "C": 0.45},
...     metadata={"institution": "ABC Bank", "model_version": "2.1.0"}
... )

See Also
--------
credit_risk_rating.rating.system._base : Base classes and configurations
credit_risk_rating.rating.system._one_dimensional : One-dimensional rating systems
credit_risk_rating.rating.system._predefined : Pre-built industry standard systems
"""

from __future__ import annotations

from typing import Any

from credit_risk_rating.exceptions import RatingScaleInputError, RatingValidationError
from credit_risk_rating.rating.system._base import (
    BaseRatingSystem,
    PDLGDRatingSystemConfig,
)
from credit_risk_rating.rating.system._mappings import Metadata, RatingGrade, RatingMap

__all__: list[str] = ["PDLGDRatingSystem"]
__author__: list[str] = ["RNKuhns"]


class PDLGDRatingSystem(BaseRatingSystem):
    """Two-dimensional rating system with separate PD and LGD scales.

    This class manages rating systems that use two dimensions: Probability of
    Default (PD) and Loss Given Default (LGD). The system validates that both
    rating scales contain exactly the required grades as specified in the class
    configuration.

    Parameters
    ----------
    pd_rating_scale : dict[RatingGrade, float] | RatingMap | None, optional
        PD rating scale mapping grades to values, by default None
    lgd_rating_scale : dict[RatingGrade, float] | RatingMap | None, optional
        LGD rating scale mapping grades to values, by default None
    metadata : dict[str, Any] | Metadata | None, optional
        Metadata about the rating system, by default None

    Attributes
    ----------
    pd_rating_scale : RatingMap
        Immutable PD rating scale mapping
    lgd_rating_scale : RatingMap
        Immutable LGD rating scale mapping
    metadata : Metadata
        Immutable metadata container

    Examples
    --------
    >>> system = PDLGDRatingSystem(
    ...     pd_rating_scale={1: 0.001, 2: 0.005, 3: 0.010},
    ...     lgd_rating_scale={"A": 0.10, "B": 0.25, "C": 0.45},
    ...     metadata={"institution": "ABC Bank"}
    ... )
    >>>
    >>> # Access grades for each dimension
    >>> system.pd_rating_grades  # [1, 2, 3]
    >>> system.lgd_rating_grades  # ["A", "B", "C"]
    >>>
    >>> # Validate ratings for each dimension
    >>> system.is_valid_pd_rating(1)   # True
    >>> system.is_valid_lgd_rating("A")  # True
    """

    def __init__(
        self,
        pd_rating_scale: dict[RatingGrade, float] | RatingMap | None = None,
        lgd_rating_scale: dict[RatingGrade, float] | RatingMap | None = None,
        metadata: dict[str, Any] | Metadata | None = None,
    ):
        """Initialize two-dimensional PD/LGD rating system.

        Parameters
        ----------
        pd_rating_scale : dict[RatingGrade, float] | RatingMap | None, optional
            PD rating scale mapping grades to values, by default None
        lgd_rating_scale : dict[RatingGrade, float] | RatingMap | None, optional
            LGD rating scale mapping grades to values, by default None
        metadata : dict[str, Any] | Metadata | None, optional
            Metadata about the rating system, by default None
        """
        # Process rating scale inputs
        self.pd_rating_scale = self._process_rating_scale_input(pd_rating_scale, "pd")
        self.lgd_rating_scale = self._process_rating_scale_input(
            lgd_rating_scale, "lgd"
        )

        # Initialize metadata (calls validation)
        super().__init__(metadata)

        # Validate rating scale requirements
        self._validate_required_grade_dimensions()

    def _process_rating_scale_input(
        self,
        rating_scale: dict[RatingGrade, float] | RatingMap | None,
        dimension_name: str,
    ) -> RatingMap:
        """Process and validate rating scale input for a specific dimension.

        Converts various rating scale input types into a standardized RatingMap
        object for a specific dimension (PD or LGD).

        Parameters
        ----------
        rating_scale : dict[RatingGrade, float] | RatingMap | None
            Input rating scale to process
        dimension_name : str
            Name of the dimension (for error messages)

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
                f"Expected {dimension_name}_rating_scale parameter to have type dict or RatingMap. "
                f"Found type {type(rating_scale)} instead."
            )

    def _validate_required_grade_dimensions(self) -> None:
        """Validate that both PD and LGD scales contain exactly the required grades.

        Checks that both rating scales contain exactly the grades specified in
        the class configuration for their respective dimensions.

        Raises
        ------
        RatingValidationError
            If required grades are missing or extra grades are present in either dimension
        """
        if not hasattr(self, "_CONFIG") or not self._CONFIG:
            return  # No requirements to validate

        required_dimensions = self._CONFIG.get("required_grade_dimensions", {})
        if not required_dimensions:
            return  # No dimension requirements

        error_messages = []

        # Validate PD dimension
        if "pd" in required_dimensions:
            pd_errors = self._validate_dimension_grades(
                self.pd_rating_scale, required_dimensions["pd"], "PD"
            )
            error_messages.extend(pd_errors)

        # Validate LGD dimension
        if "lgd" in required_dimensions:
            lgd_errors = self._validate_dimension_grades(
                self.lgd_rating_scale, required_dimensions["lgd"], "LGD"
            )
            error_messages.extend(lgd_errors)

        if error_messages:
            raise RatingValidationError(
                "Rating system validation failed:\n"
                + "\n".join(f"  - {msg}" for msg in error_messages)
            )

    def _validate_dimension_grades(
        self,
        rating_scale: RatingMap,
        required_grades: list[RatingGrade],
        dimension_name: str,
    ) -> list[str]:
        """Validate grades for a single dimension.

        Checks that a rating scale contains exactly the required grades for
        a specific dimension, providing detailed error information.

        Parameters
        ----------
        rating_scale : RatingMap
            Rating scale to validate
        required_grades : list[RatingGrade]
            Required grades for this dimension
        dimension_name : str
            Name of the dimension for error messages

        Returns
        -------
        list[str]
            List of error messages (empty if validation passes)
        """
        actual_grades = set(rating_scale.rating_grades())
        required_grades_set = set(required_grades)

        missing_grades = required_grades_set - actual_grades
        extra_grades = actual_grades - required_grades_set

        error_messages = []

        if missing_grades:
            error_messages.append(
                f"{dimension_name} missing required grades: {sorted(missing_grades)}"
            )

        if extra_grades:
            error_messages.append(
                f"{dimension_name} extra grades not allowed: {sorted(extra_grades)}"
            )

        if missing_grades or extra_grades:
            error_messages.append(
                f"{dimension_name} required grades: {required_grades}"
            )
            error_messages.append(
                f"{dimension_name} actual grades: {sorted(actual_grades)}"
            )

        return error_messages

    @property
    def pd_rating_grades(self) -> list[RatingGrade]:
        """Get the ordered list of PD rating grades.

        Returns
        -------
        list[RatingGrade]
            List of PD rating grades in the scale
        """
        return self.pd_rating_scale.rating_grades()

    @property
    def lgd_rating_grades(self) -> list[RatingGrade]:
        """Get the ordered list of LGD rating grades.

        Returns
        -------
        list[RatingGrade]
            List of LGD rating grades in the scale
        """
        return self.lgd_rating_scale.rating_grades()

    @property
    def pd_rating_values(self) -> list[float]:
        """Get the ordered list of PD rating values.

        Returns
        -------
        list[float]
            List of PD rating values in the scale
        """
        return self.pd_rating_scale.rating_values()

    @property
    def lgd_rating_values(self) -> list[float]:
        """Get the ordered list of LGD rating values.

        Returns
        -------
        list[float]
            List of LGD rating values in the scale
        """
        return self.lgd_rating_scale.rating_values()

    def get_rating_grades(self) -> dict[str, list[RatingGrade]]:
        """Get the rating grades for both dimensions of this system.

        Implementation of the abstract method from BaseRatingSystem.
        For two-dimensional systems, this returns a dictionary with both dimensions.

        Returns
        -------
        dict[str, list[RatingGrade]]
            Dictionary with 'pd' and 'lgd' keys containing respective grade lists
        """
        return {"pd": self.pd_rating_grades, "lgd": self.lgd_rating_grades}

    def is_valid_pd_rating(self, rating: RatingGrade) -> bool:
        """Check if a rating is valid for the PD scale.

        Parameters
        ----------
        rating : RatingGrade
            PD rating grade to validate

        Returns
        -------
        bool
            True if rating is valid for PD scale, False otherwise

        Examples
        --------
        >>> system = PDLGDRatingSystem(
        ...     pd_rating_scale={1: 0.001, 2: 0.005},
        ...     lgd_rating_scale={"A": 0.10, "B": 0.25}
        ... )
        >>> system.is_valid_pd_rating(1)   # True
        >>> system.is_valid_pd_rating(3)   # False
        """
        return self.pd_rating_scale.has_grade(rating)

    def is_valid_lgd_rating(self, rating: RatingGrade) -> bool:
        """Check if a rating is valid for the LGD scale.

        Parameters
        ----------
        rating : RatingGrade
            LGD rating grade to validate

        Returns
        -------
        bool
            True if rating is valid for LGD scale, False otherwise

        Examples
        --------
        >>> system = PDLGDRatingSystem(
        ...     pd_rating_scale={1: 0.001, 2: 0.005},
        ...     lgd_rating_scale={"A": 0.10, "B": 0.25}
        ... )
        >>> system.is_valid_lgd_rating("A")  # True
        >>> system.is_valid_lgd_rating("C")  # False
        """
        return self.lgd_rating_scale.has_grade(rating)

    def get_pd_rating_value(self, rating_grade: RatingGrade) -> float:
        """Get the numeric value for a PD rating grade.

        Parameters
        ----------
        rating_grade : RatingGrade
            PD rating grade to get value for

        Returns
        -------
        float
            Numeric value associated with the PD rating grade

        Raises
        ------
        KeyError
            If rating grade is not found in the PD scale

        Examples
        --------
        >>> system = PDLGDRatingSystem(pd_rating_scale={1: 0.001, 2: 0.005})
        >>> system.get_pd_rating_value(1)  # 0.001
        """
        return self.pd_rating_scale[rating_grade]

    def get_lgd_rating_value(self, rating_grade: RatingGrade) -> float:
        """Get the numeric value for an LGD rating grade.

        Parameters
        ----------
        rating_grade : RatingGrade
            LGD rating grade to get value for

        Returns
        -------
        float
            Numeric value associated with the LGD rating grade

        Raises
        ------
        KeyError
            If rating grade is not found in the LGD scale

        Examples
        --------
        >>> system = PDLGDRatingSystem(lgd_rating_scale={"A": 0.10, "B": 0.25})
        >>> system.get_lgd_rating_value("A")  # 0.10
        """
        return self.lgd_rating_scale[rating_grade]

    def get_expected_loss(
        self, pd_rating: RatingGrade, lgd_rating: RatingGrade, ead: float = 1.0
    ) -> float:
        """Calculate expected loss for given PD and LGD ratings.

        Calculates the expected loss using the formula: EL = PD × LGD × EAD

        Parameters
        ----------
        pd_rating : RatingGrade
            PD rating grade
        lgd_rating : RatingGrade
            LGD rating grade
        ead : float, optional
            Exposure at Default, by default 1.0

        Returns
        -------
        float
            Expected loss value

        Raises
        ------
        KeyError
            If either rating grade is not found in respective scales

        Examples
        --------
        >>> system = PDLGDRatingSystem(
        ...     pd_rating_scale={1: 0.001, 2: 0.005},
        ...     lgd_rating_scale={"A": 0.10, "B": 0.25}
        ... )
        >>> system.get_expected_loss(1, "A", 1000000)  # 100.0
        """
        pd_value = self.get_pd_rating_value(pd_rating)
        lgd_value = self.get_lgd_rating_value(lgd_rating)
        return pd_value * lgd_value * ead

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
        >>> system = PDLGDRatingSystem(
        ...     pd_rating_scale={1: 0.001, 2: 0.005},
        ...     lgd_rating_scale={"A": 0.10, "B": 0.25},
        ...     metadata={"institution": "ABC Bank"}
        ... )
        >>> data = system.to_dict()
        >>> data['rating_system_type']  # 'PDLGDRatingSystem'
        """
        return {
            "rating_system_type": self.__class__.__name__,
            "pd_rating_scale": self.pd_rating_scale.to_dict(),
            "lgd_rating_scale": self.lgd_rating_scale.to_dict(),
            "metadata": self.metadata.to_dict(),
            "config": self.get_config(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PDLGDRatingSystem:
        """Create rating system from dictionary representation.

        Reconstructs a rating system instance from a dictionary representation,
        typically created by the to_dict() method.

        Parameters
        ----------
        data : dict[str, Any]
            Dictionary containing rating system data

        Returns
        -------
        PDLGDRatingSystem
            Rating system instance created from dictionary

        Examples
        --------
        >>> data = {
        ...     "pd_rating_scale": {1: 0.001, 2: 0.005},
        ...     "lgd_rating_scale": {"A": 0.10, "B": 0.25},
        ...     "metadata": {"institution": "ABC Bank"}
        ... }
        >>> system = PDLGDRatingSystem.from_dict(data)
        """
        return cls(
            pd_rating_scale=data.get("pd_rating_scale", {}),
            lgd_rating_scale=data.get("lgd_rating_scale", {}),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def create_custom_class(
        cls, name: str, config: PDLGDRatingSystemConfig
    ) -> type[PDLGDRatingSystem]:
        """Create a custom two-dimensional rating system class.

        This factory method creates a new PD/LGD rating system class with the
        specified configuration. The resulting class will enforce the provided
        requirements for both PD and LGD dimensions.

        Parameters
        ----------
        name : str
            Name for the new rating system class
        config : PDLGDRatingSystemConfig
            Configuration specifying requirements for both dimensions

        Returns
        -------
        type[PDLGDRatingSystem]
            New rating system class with the specified configuration

        Raises
        ------
        RatingScaleInputError
            If configuration is missing required fields

        Examples
        --------
        >>> from credit_risk_rating.rating.system._base import PDLGDRatingSystemConfig
        >>> config = PDLGDRatingSystemConfig(
        ...     required_grade_dimensions={
        ...         "pd": [1, 2, 3, 4, 5],
        ...         "lgd": ["A", "B", "C"]
        ...     },
        ...     required_metadata=["institution", "model_version"],
        ...     name="Custom PD/LGD System"
        ... )
        >>> MySystem = PDLGDRatingSystem.create_custom_class(
        ...     name="MyBankPDLGDSystem",
        ...     config=config
        ... )
        >>>
        >>> # Use the new class
        >>> system = MySystem(
        ...     pd_rating_scale={1: 0.001, 2: 0.005, 3: 0.010, 4: 0.025, 5: 0.050},
        ...     lgd_rating_scale={"A": 0.10, "B": 0.25, "C": 0.45},
        ...     metadata={"institution": "ABC Bank", "model_version": "2.1.0"}
        ... )
        """
        # Validate configuration
        if "required_grade_dimensions" not in config:
            raise RatingScaleInputError(
                "Configuration must include 'required_grade_dimensions'"
            )

        dimensions = config["required_grade_dimensions"]
        if "pd" not in dimensions or "lgd" not in dimensions:
            raise RatingScaleInputError(
                "Configuration 'required_grade_dimensions' must include both 'pd' and 'lgd' keys"
            )

        # Create new class dynamically
        class_attrs = {
            "_CONFIG": config.copy(),
            "__module__": cls.__module__,
            "__qualname__": name,
        }

        new_class = type(name, (cls,), class_attrs)
        return new_class
