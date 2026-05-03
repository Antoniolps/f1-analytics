from abc import ABC, abstractmethod

from f1_analytics.domain.entities.weekend import RaceWeekend


class WeekendRepository(ABC):
    @abstractmethod
    def get_weekend(self, year: int, round_number: int) -> RaceWeekend: ...
