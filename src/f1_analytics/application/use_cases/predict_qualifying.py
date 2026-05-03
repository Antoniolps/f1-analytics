from f1_analytics.application.ports.weekend_repository import WeekendRepository
from f1_analytics.application.services.lap_cleaner import LapCleaner
from f1_analytics.application.services.pace_extractor import PaceExtractor
from f1_analytics.application.services.relative_ranker import RelativeRanker
from f1_analytics.application.services.session_aggregator import SessionAggregator
from f1_analytics.domain.entities.prediction import GridEntry, QualifyingPrediction
from f1_analytics.domain.value_objects.session_type import SessionType


class PredictQualifyingUseCase:
    def __init__(
        self,
        repo: WeekendRepository,
        cleaner: LapCleaner,
        extractor: PaceExtractor,
        ranker: RelativeRanker,
        aggregator: SessionAggregator,
    ):
        self.repo = repo
        self.cleaner = cleaner
        self.extractor = extractor
        self.ranker = ranker
        self.aggregator = aggregator

    def execute(self, year: int, round_number: int) -> QualifyingPrediction:
        weekend = self.repo.get_weekend(year, round_number)

        deltas_per_session: dict[SessionType, dict[str, float]] = {}
        for session in weekend.sessions:
            cleaned = self.cleaner.clean(session)
            pace = self.extractor.extract(cleaned)
            deltas = self.ranker.rank(pace)
            if deltas:
                deltas_per_session[session.type] = deltas

        scores = self.aggregator.aggregate(deltas_per_session, weekend.format)
        ordered = sorted(scores.items(), key=lambda kv: kv[1])

        grid: list[GridEntry] = []
        for position, (driver_code, score) in enumerate(ordered, start=1):
            driver = weekend.drivers.get(driver_code)
            grid.append(
                GridEntry(
                    position=position,
                    driver_code=driver_code,
                    team=driver.team if driver else "Unknown",
                    score=round(score, 4),
                )
            )

        return QualifyingPrediction(
            year=weekend.year,
            round=weekend.round,
            weekend_name=weekend.name,
            grid=grid,
        )
