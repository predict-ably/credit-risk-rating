"""Rating systems for credit risk management.

This package provides a comprehensive framework for creating and managing
rating systems used in credit risk assessment. It supports both one-dimensional
rating systems (single scale) and two-dimensional systems (PD and LGD scales).

The package includes pre-built industry-standard rating systems and factories
for creating custom systems with configurable requirements.

Main Components
---------------
Core Classes:
    RatingScale : Immutable mapping from rating grades to values
    Metadata : Immutable metadata container with attribute access

Base Classes:
    BaseRatingSystem : Abstract base for all rating systems
    RatingSystemConfig : Configuration for one-dimensional systems
    PDLGDRatingSystemConfig : Configuration for two-dimensional systems

Concrete Classes:
    OneDimensionalRatingSystem : Single-scale rating systems
    PDLGDRatingSystem : Two-dimensional PD/LGD rating systems

Pre-built Systems:
    UniformClassificationSystem : Federal regulatory classification system
    MoodysRatingSystem : Moody's 21-grade notched scale
    MoodysRatingSystemUnnotched : Moody's 9-grade un-notched scale
    FCSRatingSystem : Farm Credit System PD/LGD scale

Examples
--------
>>> # Use core classes directly
>>> from credit_risk_rating.rating.system import RatingScale, Metadata
>>> rating_scale = RatingScale({1: 0.01, 2: 0.05, 3: 0.10})
>>> metadata = Metadata({"institution": "ABC Bank", "model_version": "2.1"})

>>> # Use pre-built system
>>> from credit_risk_rating.rating.system import UniformClassificationSystem
>>> ucs = UniformClassificationSystem(
...     rating_scale={
...         "Acceptable": 0.01,
...         "Special Mention": 0.05,
...         "Substandard": 0.15,
...         "Doubtful": 0.50,
...         "Loss": 0.95
...     },
...     metadata={
...         "institution": "ABC Bank",
...         "examination_date": "2024-01-01"
...     }
... )

>>> # Create custom system
>>> from credit_risk_rating.rating.system import OneDimensionalRatingSystem, \
    RatingSystemConfig
>>> config = RatingSystemConfig(
...     required_grades=["A", "B", "C", "D", "F"],
...     required_metadata=["institution", "portfolio"]
... )
>>> MySystem = OneDimensionalRatingSystem.create_custom_class("MySystem", config)
>>> system = MySystem(
...     rating_scale={"A": 0.01, "B": 0.05, "C": 0.10, "D": 0.25, "F": 0.60},
...     metadata={"institution": "ABC Bank", "portfolio": "Commercial"}
... )

>>> # Two-dimensional system
>>> from credit_risk_rating.rating.systems import FCSRatingSystem
>>> fcs = FCSRatingSystem(
...     pd_rating_scale={1: 0.001, 2: 0.002, ..., 14: 0.800},
...     lgd_rating_scale={"A": 0.10, "B": 0.20, ..., "F": 0.90},
...     metadata={
...         "institution": "Farm Credit East",
...         "model_version": "2.1.0",
...         "calibration_date": "2024-01-01"
...     }
... )

See Also
--------
credit_risk_rating.exceptions : Custom exception classes
credit_risk_rating.rating.system._mappings : Core mapping classes
"""

from __future__ import annotations

# Import base classes and configurations
from credit_risk_rating.rating.system._base import (
    BaseRatingSystem,
    PDLGDRatingSystemConfig,
    RatingSystemConfig,
)

# Import core mapping classes (note: RatingMap is now RatingScale)
from credit_risk_rating.rating.system._mappings import Metadata, RatingScale

# Import concrete rating system classes
from credit_risk_rating.rating.system._one_dimensional import OneDimensionalRatingSystem

# Import pre-built industry standard systems
from credit_risk_rating.rating.system._predefined import (
    FCSRatingSystem,
    MoodysRatingSystem,
    MoodysRatingSystemUnnotched,
    UniformClassificationSystem,
)
from credit_risk_rating.rating.system._two_dimensional import PDLGDRatingSystem

# Public API - what users should import
__all__: list[str] = [
    # Core mapping classes
    "RatingScale",
    "Metadata",
    # Base classes and configurations
    "BaseRatingSystem",
    "RatingSystemConfig",
    "PDLGDRatingSystemConfig",
    # Concrete rating system classes
    "OneDimensionalRatingSystem",
    "PDLGDRatingSystem",
    # Pre-built industry standard systems
    "UniformClassificationSystem",
    "MoodysRatingSystem",
    "MoodysRatingSystemUnnotched",
    "FCSRatingSystem",
]
__author__: list[str] = ["RNKuhns"]
