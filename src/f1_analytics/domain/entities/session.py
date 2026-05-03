from dataclasses import dataclass, field

from f1_analytics.domain.entities.lap import Lap
from f1_analytics.domain.value_objects.session_type import SessionType


@dataclass
class Session:
    type: SessionType
    laps: list[Lap] = field(default_factory=list)
    final_positions: dict[str, int] | None = None

    def driver_codes(self) -> set[str]:
        return {lap.driver_code for lap in self.laps}
