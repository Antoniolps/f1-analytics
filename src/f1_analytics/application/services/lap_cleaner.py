from f1_analytics.domain.entities.lap import Lap
from f1_analytics.domain.entities.session import Session

OUTLIER_THRESHOLD = 1.07


class LapCleaner:
    def clean(self, session: Session) -> Session:
        valid = [
            lap for lap in session.laps
            if lap.lap_time_seconds > 0
            and not lap.is_pit_in
            and not lap.is_pit_out
        ]
        if not valid:
            return Session(type=session.type, laps=[])

        best = min(lap.lap_time_seconds for lap in valid)
        cutoff = best * OUTLIER_THRESHOLD
        kept: list[Lap] = [lap for lap in valid if lap.lap_time_seconds <= cutoff]
        return Session(type=session.type, laps=kept)
