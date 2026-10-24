"""Generate a small synthetic tweet archive so the pipeline can be tried without real data.

Usage:
    python -m data_processing.make_sample
"""

import json
import random
import zipfile
from datetime import datetime, timedelta, timezone

from config.paths import RAW_DATA

# Rough city centres, (longitude, latitude) as in Twitter's GeoJSON
CITIES = {
    "London": (-0.13, 51.51), "Paris": (2.35, 48.86), "Berlin": (13.40, 52.52),
    "Madrid": (-3.70, 40.42), "Rome": (12.50, 41.90), "Amsterdam": (4.90, 52.37),
}
WORDS = ["match", "weather", "concert", "traffic", "coffee", "election", "train", "festival", "goal", "rain"]


def fake_tweet(i, start, rng):
    city, (lon, lat) = rng.choice(list(CITIES.items()))
    when = start + timedelta(minutes=rng.randint(0, 14 * 24 * 60))
    return {
        "id_str": str(1_000_000 + i),
        "text": f"{' '.join(rng.sample(WORDS, 3))} in {city}",
        "user": {"id_str": str(rng.randint(1, 500))},
        "coordinates": {"type": "Point", "coordinates": [lon + rng.uniform(-0.1, 0.1), lat + rng.uniform(-0.1, 0.1)]},
        "timestamp_ms": str(int(when.timestamp() * 1000)),
        "entities": {"user_mentions": [{"id_str": str(rng.randint(1, 500))}] if rng.random() < 0.3 else []},
    }


def main(files=3, per_file=2000, seed=42):
    rng = random.Random(seed)
    start = datetime(2023, 1, 1, tzinfo=timezone.utc)
    path = RAW_DATA / "sample.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for f in range(files):
            tweets = [fake_tweet(f * per_file + i, start, rng) for i in range(per_file)]
            archive.writestr(f"tweets_{f:02d}.json", json.dumps(tweets))
    print(f"Wrote {files * per_file} synthetic tweets to {path}")


if __name__ == "__main__":
    main()
