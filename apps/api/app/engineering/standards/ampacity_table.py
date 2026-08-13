"""Simplified conductor ampacity reference table.

IMPORTANT: this is an internal engineering placeholder for the MVP, loosely modeled on
publicly known ampacity ranges for PVC-insulated copper conductors in commonly used
installation methods (conduit embedded in wall / conduit on wall surface). It is NOT a
transcription of ABNT NBR 5410's official Table 36 and must not be presented to the user
as such. Before this platform is used for real installations, this table must be
replaced/validated against the current official standard by a qualified engineer —
every result derived from it carries `needs_professional_review=True` for that reason
(see app.engineering.calculations.sizing).

Structure: {installation_method: {cross_section_mm2: ampacity_a}}
"""

AMPACITY_TABLE_A: dict[str, dict[float, float]] = {
    "B1_conduit_wall": {
        1.5: 15.5,
        2.5: 21.0,
        4.0: 28.0,
        6.0: 36.0,
        10.0: 50.0,
        16.0: 68.0,
        25.0: 89.0,
        35.0: 110.0,
        50.0: 134.0,
    },
}

# Standard breaker (miniature circuit breaker) current ratings, ascending.
STANDARD_BREAKER_RATINGS_A: list[float] = [
    6,
    10,
    16,
    20,
    25,
    32,
    40,
    50,
    63,
    70,
    80,
    100,
]

# Minimum cross-sections commonly required for residential low-voltage circuits.
MIN_CROSS_SECTION_LIGHTING_MM2 = 1.5
MIN_CROSS_SECTION_POWER_MM2 = 2.5
