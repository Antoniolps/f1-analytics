import logging
from pathlib import Path

import fastf1
import pandas as pd

from f1_analytics.application.ports.weekend_repository import WeekendRepository
from f1_analytics.domain.entities.driver import Driver
from f1_analytics.domain.entities.lap import Lap
from f1_analytics.domain.entities.session import Session
from f1_analytics.domain.entities.weekend import RaceWeekend
from f1_analytics.domain.value_objects.compound import Compound
from f1_analytics.domain.value_objects.session_type import SessionType, WeekendFormat

logger = logging.getLogger(__name__)

CONVENTIONAL_SESSIONS = (SessionType.FP1, SessionType.FP2, SessionType.FP3)
SPRINT_SESSIONS = (SessionType.FP1, SessionType.SPRINT_QUALIFYING, SessionType.SPRINT)


class FastF1WeekendRepository(WeekendRepository):
    def __init__(self, cache_dir: str = "./cache"):
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)

    def get_weekend(self, year: int, round_number: int) -> RaceWeekend:
        event = fastf1.get_event(year, round_number)
        weekend_format = self._detect_format(event)
        weekend_name = event.get("EventName", f"Round {round_number}")
        session_types = SPRINT_SESSIONS if weekend_format == WeekendFormat.SPRINT else CONVENTIONAL_SESSIONS

        sessions: list[Session] = []
        drivers: dict[str, Driver] = {}

        for stype in session_types:
            try:
                ff1_session = fastf1.get_session(year, round_number, stype.value)
                ff1_session.load(telemetry=False, weather=False, messages=False)
            except Exception as e:
                logger.warning("Failed to load %s for %d R%d: %s", stype.value, year, round_number, e)
                continue

            self._collect_drivers(ff1_session, drivers)
            sessions.append(Session(
                type=stype,
                laps=self._map_laps(ff1_session.laps),
                final_positions=self._extract_final_positions(ff1_session) if stype == SessionType.SPRINT else None,
            ))

        return RaceWeekend(
            year=year,
            round=round_number,
            name=weekend_name,
            format=weekend_format,
            sessions=sessions,
            drivers=drivers,
        )

    @staticmethod
    def _detect_format(event) -> WeekendFormat:
        raw = (event.get("EventFormat") or "").lower()
        if "sprint" in raw:
            return WeekendFormat.SPRINT
        return WeekendFormat.CONVENTIONAL

    @staticmethod
    def _collect_drivers(ff1_session, drivers: dict[str, Driver]) -> None:
        for code in ff1_session.drivers:
            try:
                info = ff1_session.get_driver(code)
                abbr = info.get("Abbreviation") or code
                team = info.get("TeamName") or "Unknown"
                if abbr not in drivers:
                    drivers[abbr] = Driver(code=abbr, team=team)
            except Exception:
                continue

    @staticmethod
    def _extract_final_positions(ff1_session) -> dict[str, int] | None:
        df = ff1_session.results
        if df is None or len(df) == 0:
            return None
        positions: dict[str, int] = {}
        for _, row in df.iterrows():
            abbr = row.get("Abbreviation")
            pos = row.get("Position")
            if pd.isna(abbr) or pd.isna(pos):
                continue
            positions[str(abbr)] = int(pos)
        return positions or None

    @staticmethod
    def _map_laps(df: pd.DataFrame) -> list[Lap]:
        laps: list[Lap] = []
        for _, row in df.iterrows():
            lap_time = row.get("LapTime")
            if pd.isna(lap_time):
                continue
            laps.append(
                Lap(
                    driver_code=str(row["Driver"]),
                    lap_number=int(row["LapNumber"]),
                    lap_time_seconds=lap_time.total_seconds(),
                    compound=Compound.parse(row.get("Compound")),
                    tyre_life=int(row["TyreLife"]) if not pd.isna(row.get("TyreLife")) else 0,
                    is_accurate=bool(row.get("IsAccurate", False)),
                    is_pit_in=not pd.isna(row.get("PitInTime")),
                    is_pit_out=not pd.isna(row.get("PitOutTime")),
                )
            )
        return laps
