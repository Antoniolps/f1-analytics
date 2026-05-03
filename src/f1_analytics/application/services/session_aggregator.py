from f1_analytics.domain.value_objects.session_type import SessionType, WeekendFormat

CONVENTIONAL_WEIGHTS: dict[SessionType, float] = {
    SessionType.FP1: 0.2,
    SessionType.FP2: 0.3,
    SessionType.FP3: 0.5,
}

SPRINT_WEIGHTS: dict[SessionType, float] = {
    SessionType.FP1: 0.20,
    SessionType.SPRINT_QUALIFYING: 0.70,
    SessionType.SPRINT: 0.10,
}


class SessionAggregator:
    def __init__(
        self,
        conventional_weights: dict[SessionType, float] | None = None,
        sprint_weights: dict[SessionType, float] | None = None,
    ):
        self._weights_by_format = {
            WeekendFormat.CONVENTIONAL: conventional_weights or CONVENTIONAL_WEIGHTS,
            WeekendFormat.SPRINT: sprint_weights or SPRINT_WEIGHTS,
        }

    def aggregate(
        self,
        deltas_per_session: dict[SessionType, dict[str, float]],
        weekend_format: WeekendFormat = WeekendFormat.CONVENTIONAL,
    ) -> dict[str, float]:
        weights = self._weights_by_format[weekend_format]

        all_drivers: set[str] = set()
        for d in deltas_per_session.values():
            all_drivers.update(d.keys())

        scores: dict[str, float] = {}
        for driver in all_drivers:
            total_weight = 0.0
            weighted_sum = 0.0
            for stype, deltas in deltas_per_session.items():
                weight = weights.get(stype, 0.0)
                if weight == 0.0 or not deltas:
                    continue
                delta = deltas.get(driver)
                if delta is None:
                    delta = max(deltas.values())
                weighted_sum += delta * weight
                total_weight += weight
            scores[driver] = weighted_sum / total_weight if total_weight else float("inf")
        return scores
