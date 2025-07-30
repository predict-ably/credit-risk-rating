"""Pre-built industry standard rating systems.

This module contains pre-built rating systems for common industry standards,
created using the same factory pattern available to users. These systems
demonstrate the factory usage and provide ready-to-use implementations for
standard rating scales.

All systems are created using the factory methods from OneDimensionalRatingSystem
and PDLGDRatingSystem, ensuring consistency with user-defined systems.

Notes
-----
While pre-built rating systems for common industry standards are provided, these
systems require the user to provide the rating_scale as an input.

Examples
--------
>>> from credit_risk_rating.rating.system._predefined import UniformClassificationSystem
>>> from credit_risk_rating.rating.system._predefined import FCSRatingSystem
>>>
>>> # Use Uniform Classification System
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
>>>
>>> # Use Farm Credit System (two-dimensional)
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
credit_risk_rating.rating.system._one_dimensional : Factory for one-dimensional systems
credit_risk_rating.rating.system._two_dimensional : Factory for two-dimensional systems
credit_risk_rating.rating.system._base : Base classes and configurations
"""

from __future__ import annotations

from credit_risk_rating.rating.system._base import (
    PDLGDRatingSystemConfig,
    RatingSystemConfig,
)
from credit_risk_rating.rating.system._one_dimensional import OneDimensionalRatingSystem
from credit_risk_rating.rating.system._two_dimensional import PDLGDRatingSystem

__all__: list[str] = [
    "UniformClassificationSystem",
    "MoodysRatingSystem",
    "MoodysRatingSystemUnnotched",
    "FCSRatingSystem",
]
__author__: list[str] = ["RNKuhns"]

# Uniform Classification System (Federal Financial Institution Regulators)
# Used by FDIC, OCC, and Federal Reserve for asset classification
UniformClassificationSystem = OneDimensionalRatingSystem.create_custom_class(
    name="UniformClassificationSystem",
    config=RatingSystemConfig(
        required_grades=[
            "Acceptable",
            "Special Mention",
            "Substandard",
            "Doubtful",
            "Loss",
        ],
        required_metadata=["institution", "examination_date"],
        name="Uniform Classification System",
        description=(
            "Federal financial institution regulatory asset classification system used by "
            "FDIC, OCC, and Federal Reserve. Provides standardized approach to classifying "
            "credit risk in bank loan portfolios with five categories from Acceptable "
            "(minimal risk) to Loss (uncollectible)."
        ),
        reference_url="https://www.fdic.gov/regulations/safety/manual/section3-1.pdf",
    ),
)


# Moody's Long-term Credit Rating Scale (Notched)
# 21-grade scale with notching for fine-grained distinctions
MoodysRatingSystem = OneDimensionalRatingSystem.create_custom_class(
    name="MoodysRatingSystem",
    config=RatingSystemConfig(
        required_grades=[
            "Aaa",
            "Aa1",
            "Aa2",
            "Aa3",
            "A1",
            "A2",
            "A3",
            "Baa1",
            "Baa2",
            "Baa3",
            "Ba1",
            "Ba2",
            "Ba3",
            "B1",
            "B2",
            "B3",
            "Caa1",
            "Caa2",
            "Caa3",
            "Ca",
            "C",
        ],
        required_metadata=["rating_date", "issuer"],
        name="Moody's Long-term Credit Rating Scale (Notched)",
        description=(
            "Moody's long-term credit rating scale with notching provides 21 distinct "
            "rating grades from Aaa (highest quality, minimal credit risk) to C "
            "(lowest quality, typically in default). Notched ratings (1, 2, 3) "
            "provide finer distinctions within major rating categories."
        ),
        reference_url="https://www.moodys.com/sites/products/productattachments/ap075378_1_1408_ki.pdf",
    ),
)


# Moody's Long-term Credit Rating Scale (Un-notched)
# 9-grade scale without notching for broader categories
MoodysRatingSystemUnnotched = OneDimensionalRatingSystem.create_custom_class(
    name="MoodysRatingSystemUnnotched",
    config=RatingSystemConfig(
        required_grades=["Aaa", "Aa", "A", "Baa", "Ba", "B", "Caa", "Ca", "C"],
        required_metadata=["rating_date", "issuer"],
        name="Moody's Long-term Credit Rating Scale (Un-notched)",
        description=(
            "Moody's long-term credit rating scale without notching provides 9 broad "
            "rating categories from Aaa (highest quality, minimal credit risk) to C "
            "(lowest quality, typically in default). This scale groups ratings into "
            "major categories without the finer distinctions of notched ratings."
        ),
        reference_url="https://www.moodys.com/sites/products/productattachments/ap075378_1_1408_ki.pdf",
    ),
)


# Farm Credit System PD/LGD Rating System
# Two-dimensional system used by FCS institutions
FCSRatingSystem = PDLGDRatingSystem.create_custom_class(
    name="FCSRatingSystem",
    config=PDLGDRatingSystemConfig(
        required_grade_dimensions={
            "pd": list(range(1, 15)),  # 1-14 PD scale
            "lgd": ["A", "B", "C", "D", "E", "F"],  # A-F LGD scale
        },
        required_metadata=["institution", "model_version", "calibration_date"],
        name="Farm Credit System Rating Scale",
        description=(
            "Two-dimensional rating system used by Farm Credit System institutions "
            "for agricultural lending. Uses a 14-point PD scale (1-14, where 1 represents "
            "lowest default probability) and a 6-point LGD scale (A-F, where A represents "
            "lowest loss given default). This system allows for comprehensive risk "
            "assessment covering both default probability and loss severity."
        ),
        reference_url="https://www.fca.gov/template-fca/about/regulations-guidance",
    ),
)
