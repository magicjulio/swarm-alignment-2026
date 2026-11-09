import csv, sys
from datetime import date


def main(month: str):
    rows = load_sessions(month)  # from the analytics export
    with open(f"data/web_traffic_{month}.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "sessions", "users", "bounce_rate", "avg_session_s"])
        w.writerows(rows)


if __name__ == "__main__":
    main(sys.argv[1])
