from collections import defaultdict

from f1_analytics.domain.entities.lap import Lap
from f1_analytics.domain.entities.session import Session

MIN_STINT_LAPS = 5


class TireDegradationAnalyzer:
    """Computes mean degradation slope (s/lap) per driver from long stints."""

    def analyze(self, session: Session) -> dict[str, float]:
        slopes_per_driver: dict[str, list[float]] = defaultdict(list)
        laps_by_driver: dict[str, list[Lap]] = defaultdict(list)
        for lap in session.laps:
            laps_by_driver[lap.driver_code].append(lap)

        for driver, laps in laps_by_driver.items():
            laps.sort(key=lambda l: l.lap_number)
            for stint in self._group_stints(laps):
                if len(stint) >= MIN_STINT_LAPS:
                    slope = self._linear_slope(stint)
                    if slope is not None:
                        slopes_per_driver[driver].append(slope)

        return {
            driver: sum(slopes) / len(slopes)
            for driver, slopes in slopes_per_driver.items()
            if slopes
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
            if lap.lap_number == prev.lap_number + 1 and lap.compound == prev.compound:
                current.append(lap)
            else:
                stints.append(current)
                current = [lap]
        if current:
            stints.append(current)
        return stints

    @staticmethod
    def _linear_slope(stint: list[Lap]) -> float | None:
        n = len(stint)
        xs = [lap.tyre_life for lap in stint]
        ys = [lap.lap_time_seconds for lap in stint]
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        denom = sum((x - mean_x) ** 2 for x in xs)
        if denom == 0:
            return None
        return sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / denom
