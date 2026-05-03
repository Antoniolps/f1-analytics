from collections import defaultdict
from itertools import groupby

from f1_analytics.domain.entities.lap import Lap
from f1_analytics.domain.entities.session import Session

MIN_STINT_LAPS = 5


class LongRunExtractor:
    """Extracts mean pace per driver from stints of >=5 consecutive clean laps on the same compound."""

    def extract(self, session: Session) -> dict[str, float]:
        stints_per_driver: dict[str, list[float]] = defaultdict(list)
        laps_by_driver: dict[str, list[Lap]] = defaultdict(list)
        for lap in session.laps:
            laps_by_driver[lap.driver_code].append(lap)

        for driver, laps in laps_by_driver.items():
            laps.sort(key=lambda l: l.lap_number)
            for stint in self._group_stints(laps):
                if len(stint) >= MIN_STINT_LAPS:
                    avg = sum(l.lap_time_seconds for l in stint) / len(stint)
                    stints_per_driver[driver].append(avg)

        return {
            driver: sum(stint_avgs) / len(stint_avgs)
            for driver, stint_avgs in stints_per_driver.items()
            if stint_avgs
        }

    @staticmethod
    def _group_stints(laps: list[Lap]) -> list[list[Lap]]:
        stints: list[list[Lap]] = []
        current: list[Lap] = []
        for lap in laps:
            if not current:
                current = [lap]
                continue
            prev = current[-1]
            consecutive = lap.lap_number == prev.lap_number + 1
            same_compound = lap.compound == prev.compound
            if consecutive and same_compound:
                current.append(lap)
            else:
                stints.append(current)
                current = [lap]
        if current:
            stints.append(current)
        return stints
