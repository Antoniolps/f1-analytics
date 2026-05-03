import argparse
import logging

from f1_analytics.composition import build_predict_race_use_case


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict F1 race result for a race weekend.")
    parser.add_argument("year", type=int)
    parser.add_argument("round", type=int)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    use_case = build_predict_race_use_case()
    prediction = use_case.execute(args.year, args.round)

    print(f"\nPredicted race result — {prediction.weekend_name} ({prediction.year} R{prediction.round})")
    print(f"Signals used: {', '.join(prediction.signals_used)}\n")
    print(f"  {'Pos':>3}  {'Driver':<6}  {'Team':<28}  Score")
    print(f"  {'-'*3}  {'-'*6}  {'-'*28}  {'-'*6}")
    for entry in prediction.grid:
        print(f"  {entry.position:>3}  {entry.driver_code:<6}  {entry.team:<28}  {entry.score:.4f}")


if __name__ == "__main__":
    main()
