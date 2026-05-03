from dataclasses import dataclass

from f1_analytics.domain.value_objects.compound import Compound


@dataclass(frozen=True)
class Lap:
    driver_code: str
    lap_number: int
    lap_time_seconds: float
    compound: Compound
    tyre_life: int
    is_accurate: bool
    is_pit_in: bool
    is_pit_out: bool
