from dataclasses import dataclass, field

from f1_analytics.domain.entities.prediction import GridEntry


@dataclass(frozen=True)
class RacePrediction:
    year: int
    round: int
    weekend_name: str
    grid: list[GridEntry]
    signals_used: list[str] = field(default_factory=list)
