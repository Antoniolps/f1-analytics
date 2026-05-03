from abc import ABC, abstractmethod

from f1_analytics.application.services.season_form_scorer import RaceResult


class SeasonResultsRepository(ABC):
    @abstractmethod
    def get_prior_race_results(self, year: int, before_round: int) -> list[RaceResult]:
        """Returns race results from rounds 1..before_round-1 in the given year."""
