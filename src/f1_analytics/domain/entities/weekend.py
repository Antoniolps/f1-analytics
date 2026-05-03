from dataclasses import dataclass, field

from f1_analytics.domain.entities.driver import Driver
from f1_analytics.domain.entities.session import Session
from f1_analytics.domain.value_objects.session_type import WeekendFormat


@dataclass
class RaceWeekend:
    year: int
    round: int
    name: str
    format: WeekendFormat = WeekendFormat.CONVENTIONAL
    sessions: list[Session] = field(default_factory=list)
    drivers: dict[str, Driver] = field(default_factory=dict)
