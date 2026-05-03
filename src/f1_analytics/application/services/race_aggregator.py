from f1_analytics.domain.value_objects.session_type import WeekendFormat

CONVENTIONAL_RACE_WEIGHTS: dict[str, float] = {
    "grid": 0.40,
    "race_pace": 0.30,
    "tire_deg": 0.20,
    "season_form": 0.10,
}

SPRINT_RACE_WEIGHTS: dict[str, float] = {
    "grid": 0.35,
    "race_pace": 0.20,
    "tire_deg": 0.15,
    "sprint_result": 0.20,
    "season_form": 0.10,
}


class RaceAggregator:
    """Aggregates rank signals into a single score per driver. Lower = better predicted finish."""

    def __init__(
        self,
        conventional_weights: dict[str, float] | None = None,
        sprint_weights: dict[str, float] | None = None,
    ):
        self._weights_by_format = {
            WeekendFormat.CONVENTIONAL: conventional_weights or CONVENTIONAL_RACE_WEIGHTS,
            WeekendFormat.SPRINT: sprint_weights or SPRINT_RACE_WEIGHTS,
        }

    def aggregate(
        self,
        signals: dict[str, dict[str, float]],
        weekend_format: WeekendFormat,
    ) -> dict[str, float]:
        weights = self._weights_by_format[weekend_format]
        all_drivers: set[str] = set()
        for s in signals.values():
            all_drivers.update(s.keys())

        ranks_per_signal: dict[str, dict[str, float]] = {
            name: self._to_rank(values) for name, values in signals.items()
        }

        scores: dict[str, float] = {}
        for driver in all_drivers:
            total_w = 0.0
            weighted_sum = 0.0
            for name, rank_map in ranks_per_signal.items():
                weight = weights.get(name, 0.0)
                if weight == 0.0 or not rank_map:
                    continue
                rank = rank_map.get(driver, max(rank_map.values()) + 1)
                weighted_sum += rank * weight
                total_w += weight
            scores[driver] = weighted_sum / total_w if total_w else float("inf")
        return scores

    @staticmethod
    def _to_rank(values: dict[str, float]) -> dict[str, float]:
        ordered = sorted(values.items(), key=lambda kv: kv[1])
        return {driver: rank for rank, (driver, _) in enumerate(ordered, start=1)}
