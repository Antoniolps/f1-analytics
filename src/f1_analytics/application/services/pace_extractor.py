from f1_analytics.domain.entities.session import Session


class PaceExtractor:
    """MVP: best clean lap per driver per session."""

    def extract(self, session: Session) -> dict[str, float]:
        pace: dict[str, float] = {}
        for lap in session.laps:
            current = pace.get(lap.driver_code)
            if current is None or lap.lap_time_seconds < current:
                pace[lap.driver_code] = lap.lap_time_seconds
        return pace
