from dataclasses import dataclass


@dataclass(frozen=True)
class GridEntry:
    position: int
    driver_code: str
    team: str
    score: float


@dataclass(frozen=True)
class QualifyingPrediction:
    year: int
    round: int
    weekend_name: str
    grid: list[GridEntry]
