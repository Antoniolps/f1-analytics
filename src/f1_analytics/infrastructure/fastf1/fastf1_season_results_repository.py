import logging

import fastf1
import pandas as pd

from f1_analytics.application.ports.season_results_repository import SeasonResultsRepository
from f1_analytics.application.services.season_form_scorer import RaceResult

logger = logging.getLogger(__name__)


class FastF1SeasonResultsRepository(SeasonResultsRepository):
    def get_prior_race_results(self, year: int, before_round: int) -> list[RaceResult]:
        results: list[RaceResult] = []
        for r in range(1, before_round):
            try:
                session = fastf1.get_session(year, r, "R")
                session.load(telemetry=False, weather=False, messages=False)
            except Exception as e:
                logger.info("Race not available for %d R%d: %s", year, r, e)
                continue

            df = session.results
            if df is None or len(df) == 0:
                continue
            positions: dict[str, int] = {}
            for _, row in df.iterrows():
                abbr = row.get("Abbreviation")
                pos = row.get("Position")
                if pd.isna(abbr) or pd.isna(pos):
                    continue
                positions[str(abbr)] = int(pos)
            if positions:
                results.append(RaceResult(round=r, positions=positions))
        return results
