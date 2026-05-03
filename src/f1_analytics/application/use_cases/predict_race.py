from f1_analytics.application.ports.qualifying_result_repository import QualifyingResultRepository
from f1_analytics.application.ports.season_results_repository import SeasonResultsRepository
from f1_analytics.application.ports.weekend_repository import WeekendRepository
from f1_analytics.application.services.lap_cleaner import LapCleaner
from f1_analytics.application.services.long_run_extractor import LongRunExtractor
from f1_analytics.application.services.race_aggregator import RaceAggregator
from f1_analytics.application.services.season_form_scorer import SeasonFormScorer
from f1_analytics.application.services.tire_degradation_analyzer import TireDegradationAnalyzer
from f1_analytics.application.use_cases.predict_qualifying import PredictQualifyingUseCase
from f1_analytics.domain.entities.prediction import GridEntry
from f1_analytics.domain.entities.race_prediction import RacePrediction
from f1_analytics.domain.entities.weekend import RaceWeekend
from f1_analytics.domain.value_objects.session_type import SessionType, WeekendFormat


class PredictRaceUseCase:
    def __init__(
        self,
        weekend_repo: WeekendRepository,
        qualifying_repo: QualifyingResultRepository,
        season_repo: SeasonResultsRepository,
        predict_qualifying: PredictQualifyingUseCase,
        cleaner: LapCleaner,
        long_run: LongRunExtractor,
        tire_deg: TireDegradationAnalyzer,
        season_form: SeasonFormScorer,
        aggregator: RaceAggregator,
    ):
        self.weekend_repo = weekend_repo
        self.qualifying_repo = qualifying_repo
        self.season_repo = season_repo
        self.predict_qualifying = predict_qualifying
        self.cleaner = cleaner
        self.long_run = long_run
        self.tire_deg = tire_deg
        self.season_form = season_form
        self.aggregator = aggregator

    def execute(self, year: int, round_number: int) -> RacePrediction:
        weekend = self.weekend_repo.get_weekend(year, round_number)
        signals_used: list[str] = []
        signals: dict[str, dict[str, float]] = {}

        grid_signal, grid_source = self._build_grid_signal(year, round_number)
        if grid_signal:
            signals["grid"] = grid_signal
            signals_used.append(f"grid:{grid_source}")

        race_pace = self._build_race_pace_signal(weekend)
        if race_pace:
            signals["race_pace"] = race_pace
            signals_used.append("race_pace")

        tire_deg = self._build_tire_deg_signal(weekend)
        if tire_deg:
            signals["tire_deg"] = tire_deg
            signals_used.append("tire_deg")

        sprint_signal = self._build_sprint_signal(weekend)
        if sprint_signal:
            signals["sprint_result"] = sprint_signal
            signals_used.append("sprint_result")

        season = self._build_season_signal(year, round_number)
        if season:
            signals["season_form"] = season
            signals_used.append("season_form")

        scores = self.aggregator.aggregate(signals, weekend.format)
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

        return RacePrediction(
            year=weekend.year,
            round=weekend.round,
            weekend_name=weekend.name,
            grid=grid,
            signals_used=signals_used,
        )

    def _build_grid_signal(self, year: int, round_number: int) -> tuple[dict[str, float], str]:
        official = self.qualifying_repo.get_official_qualifying(year, round_number)
        if official:
            return {driver: float(pos) for pos, driver in enumerate(official, start=1)}, "official"
        predicted = self.predict_qualifying.execute(year, round_number)
        return {entry.driver_code: float(entry.position) for entry in predicted.grid}, "predicted"

    def _build_race_pace_signal(self, weekend: RaceWeekend) -> dict[str, float]:
        weights_by_session: dict[SessionType, float] = (
            {SessionType.FP1: 0.2, SessionType.SPRINT: 0.5, SessionType.SPRINT_QUALIFYING: 0.3}
            if weekend.format == WeekendFormat.SPRINT
            else {SessionType.FP1: 0.2, SessionType.FP2: 0.4, SessionType.FP3: 0.4}
        )
        accum: dict[str, float] = {}
        wsum: dict[str, float] = {}
        for session in weekend.sessions:
            cleaned = self.cleaner.clean(session)
            pace = self.long_run.extract(cleaned)
            w = weights_by_session.get(session.type, 0.0)
            if w == 0.0 or not pace:
                continue
            for driver, p in pace.items():
                accum[driver] = accum.get(driver, 0.0) + p * w
                wsum[driver] = wsum.get(driver, 0.0) + w
        return {d: accum[d] / wsum[d] for d in accum if wsum[d] > 0}

    def _build_tire_deg_signal(self, weekend: RaceWeekend) -> dict[str, float]:
        accum: dict[str, list[float]] = {}
        for session in weekend.sessions:
            cleaned = self.cleaner.clean(session)
            slopes = self.tire_deg.analyze(cleaned)
            for driver, slope in slopes.items():
                accum.setdefault(driver, []).append(slope)
        return {d: sum(v) / len(v) for d, v in accum.items() if v}

    def _build_sprint_signal(self, weekend: RaceWeekend) -> dict[str, float] | None:
        if weekend.format != WeekendFormat.SPRINT:
            return None
        for session in weekend.sessions:
            if session.type == SessionType.SPRINT and session.final_positions:
                return {d: float(p) for d, p in session.final_positions.items()}
        return None

    def _build_season_signal(self, year: int, round_number: int) -> dict[str, float]:
        prior = self.season_repo.get_prior_race_results(year, round_number)
        return self.season_form.score(prior)
