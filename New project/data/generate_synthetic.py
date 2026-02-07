import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


OUTPUT_DIR = Path(__file__).parent / "out"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

USERS = 1000
EVENTS = 100_000
FEEDBACK = 5_000
EVENT_TYPES = ["signup", "login", "feature_use", "upgrade", "churn"]
FEATURES = ["export", "import", "dashboard", "alerts", "reports"]


def random_date(start_days_ago: int = 120):
    start = datetime.utcnow() - timedelta(days=start_days_ago)
    return start + timedelta(seconds=random.randint(0, start_days_ago * 86400))


def generate_users(path: Path):
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "created_at", "plan", "country"])
        for user_id in range(1, USERS + 1):
            writer.writerow([
                user_id,
                random_date().isoformat(),
                "pro" if user_id % 4 == 0 else "free",
                random.choice(["US", "CA", "GB", "IN", "DE"]),
            ])


def generate_events(path: Path):
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "event_type", "metadata", "timestamp"])
        for _ in range(EVENTS):
            user_id = random.randint(1, USERS)
            event_type = random.choice(EVENT_TYPES)
            metadata = {"feature": random.choice(FEATURES)} if event_type == "feature_use" else {}
            writer.writerow([
                user_id,
                event_type,
                metadata,
                random_date().isoformat(),
            ])


def generate_feedback(path: Path):
    positive = ["Love it", "Great product", "Very helpful"]
    negative = ["Confusing", "Buggy", "Frustrating experience"]
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "text", "rating", "timestamp"])
        for _ in range(FEEDBACK):
            user_id = random.randint(1, USERS)
            is_pos = random.random() > 0.35
            writer.writerow([
                user_id,
                random.choice(positive if is_pos else negative),
                5 if is_pos else random.randint(1, 3),
                random_date().isoformat(),
            ])


if __name__ == "__main__":
    generate_users(OUTPUT_DIR / "users.csv")
    generate_events(OUTPUT_DIR / "events.csv")
    generate_feedback(OUTPUT_DIR / "feedback.csv")
    print(f"Wrote CSVs to {OUTPUT_DIR}")
