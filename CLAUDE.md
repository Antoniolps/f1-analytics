# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

This project uses [uv](https://docs.astral.sh/uv/) for dependency management (Python >=3.11).

- Install / sync deps: `uv sync`
- Run the FastAPI server: `uv run uvicorn f1_analytics.interfaces.api.main:app --reload`
- CLI — predict qualifying: `uv run python -m f1_analytics.interfaces.cli.predict <year> <round> [--verbose]`
- CLI — predict race: `uv run python -m f1_analytics.interfaces.cli.predict_race <year> <round> [--verbose]`

There is no test suite, linter, or formatter configured in `pyproject.toml`.

## Architecture

The codebase follows a strict **hexagonal / clean architecture** layout under `src/f1_analytics/`. Dependencies point inward: `interfaces` → `application` → `domain`, with `infrastructure` plugged in at the edges. All wiring lives in `composition.py` — interface layers (FastAPI routes, CLIs) call `build_predict_*_use_case()` and never instantiate concrete adapters themselves.

Layers:

- `domain/` — pure entities (`RaceWeekend`, `Session`, `Lap`, `Driver`, `QualifyingPrediction`, `RacePrediction`) and value objects (`SessionType`, `WeekendFormat`, `Compound`). No I/O, no external deps.
- `application/ports/` — abstract repository interfaces (`WeekendRepository`, `QualifyingResultRepository`, `SeasonResultsRepository`).
- `application/services/` — small, single-responsibility analytical components (lap cleaning, pace extraction, ranking, tire-degradation analysis, season-form scoring, session/race aggregators). Use cases compose these.
- `application/use_cases/` — `PredictQualifyingUseCase` and `PredictRaceUseCase` orchestrate the prediction pipelines.
- `infrastructure/fastf1/` — concrete adapters that wrap [FastF1](https://docs.fastf1.dev/) and translate raw `pandas` data into domain entities.
- `interfaces/api/` — FastAPI app and routers (`/predictions/...`, `/predictions/race/...`, `/health`).
- `interfaces/cli/` — argparse entry points.

### Prediction pipeline (key conceptual flow)

`PredictRaceUseCase.execute` builds a set of named **signals** (each a `dict[driver_code, score]`) and hands them to `RaceAggregator` for weighted combination. Signals built today: `grid` (official quali if available, else delegated to `PredictQualifyingUseCase`), `race_pace` (long-run extraction over practice/sprint sessions, weighted differently for sprint vs. conventional weekends), `tire_deg`, `sprint_result` (sprint weekends only), and `season_form` (prior-rounds standings via `SeasonResultsRepository`). The `signals_used` field on `RacePrediction` records which signals contributed.

`PredictQualifyingUseCase` follows the same shape but operates over per-session pace deltas produced by `RelativeRanker`, then aggregated by `SessionAggregator`.

### Weekend formats

`WeekendFormat` (CONVENTIONAL vs SPRINT) controls which sessions are loaded by `FastF1WeekendRepository` (`FP1/FP2/FP3` vs `FP1/SPRINT_QUALIFYING/SPRINT`) and which weights aggregators apply. Format detection is based on the FastF1 event's `EventFormat` string.

### FastF1 caching

`FastF1WeekendRepository.__init__` enables FastF1's on-disk cache at `./cache` (default). The cache dir is created if missing and is the only persistence layer.
