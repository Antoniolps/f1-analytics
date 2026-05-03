import logging

import fastf1
import pandas as pd

from f1_analytics.application.ports.qualifying_result_repository import QualifyingResultRepository

logger = logging.getLogger(__name__)


class FastF1QualifyingResultRepository(QualifyingResultRepository):
    def get_official_qualifying(self, year: int, round_number: int) -> list[str] | None:
        try:
            session = fastf1.get_session(year, round_number, "Q")
            session.load(telemetry=False, weather=False, messages=False)
        except Exception as e:
            logger.info("Q not available for %d R%d: %s", year, round_number, e)
            return None

        results = session.results
        if results is None or len(results) == 0:
            return None

        df = results.sort_values("Position")
        ordered = [str(abbr) for abbr in df["Abbreviation"].tolist() if not pd.isna(abbr)]
        return ordered or None
