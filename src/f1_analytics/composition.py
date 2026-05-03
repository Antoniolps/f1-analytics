from f1_analytics.application.services.lap_cleaner import LapCleaner
from f1_analytics.application.services.long_run_extractor import LongRunExtractor
from f1_analytics.application.services.pace_extractor import PaceExtractor
from f1_analytics.application.services.race_aggregator import RaceAggregator
from f1_analytics.application.services.relative_ranker import RelativeRanker
from f1_analytics.application.services.season_form_scorer import SeasonFormScorer
from f1_analytics.application.services.session_aggregator import SessionAggregator
from f1_analytics.application.services.tire_degradation_analyzer import TireDegradationAnalyzer
from f1_analytics.application.use_cases.predict_qualifying import PredictQualifyingUseCase
from f1_analytics.application.use_cases.predict_race import PredictRaceUseCase
from f1_analytics.infrastructure.fastf1.fastf1_qualifying_result_repository import (
    FastF1QualifyingResultRepository,
)
from f1_analytics.infrastructure.fastf1.fastf1_season_results_repository import (
    FastF1SeasonResultsRepository,
)
from f1_analytics.infrastructure.fastf1.fastf1_weekend_repository import FastF1WeekendRepository


def build_predict_use_case(cache_dir: str = "./cache") -> PredictQualifyingUseCase:
    return PredictQualifyingUseCase(
        repo=FastF1WeekendRepository(cache_dir=cache_dir),
        cleaner=LapCleaner(),
        extractor=PaceExtractor(),
        ranker=RelativeRanker(),
        aggregator=SessionAggregator(),
    )


def build_predict_race_use_case(cache_dir: str = "./cache") -> PredictRaceUseCase:
    weekend_repo = FastF1WeekendRepository(cache_dir=cache_dir)
    cleaner = LapCleaner()
    quali_uc = PredictQualifyingUseCase(
        repo=weekend_repo,
        cleaner=cleaner,
        extractor=PaceExtractor(),
        ranker=RelativeRanker(),
        aggregator=SessionAggregator(),
    )
    return PredictRaceUseCase(
        weekend_repo=weekend_repo,
        qualifying_repo=FastF1QualifyingResultRepository(),
        season_repo=FastF1SeasonResultsRepository(),
        predict_qualifying=quali_uc,
        cleaner=cleaner,
        long_run=LongRunExtractor(),
        tire_deg=TireDegradationAnalyzer(),
        season_form=SeasonFormScorer(),
        aggregator=RaceAggregator(),
    )
