"""Stream tweets out of zipped JSON archives without loading them into memory."""

import zipfile
from typing import Dict, Iterator, Optional

import ijson
from tqdm import tqdm


def stream_tweets(zip_path, max_files: Optional[int] = None) -> Iterator[Dict]:
    """Yield one slimmed-down tweet at a time from every .json file in a zip.

    ijson parses each file incrementally, so memory use stays flat no matter
    how large the archive is. Each file must contain a JSON array of tweets.
    """
    with zipfile.ZipFile(zip_path) as archive:
        files = sorted(f for f in archive.namelist() if f.endswith(".json"))
        if max_files is not None:
            files = files[:max_files]

        for name in tqdm(files, desc="Processing files"):
            with archive.open(name) as handle:
                for obj in ijson.items(handle, "item"):
                    yield {
                        "id": obj.get("id_str"),
                        "text": obj.get("text"),
                        "user_id": (obj.get("user") or {}).get("id_str"),
                        "coordinates": (obj.get("coordinates") or {}).get("coordinates"),
                        "timestamp": obj.get("timestamp_ms"),
                        "mentions": [
                            u["id_str"]
                            for u in (obj.get("entities") or {}).get("user_mentions", [])
                        ],
                    }


def save_chunk(df, chunk_num: int, output_dir) -> str:
    """Save one processed chunk as a Parquet file."""
    path = f"{output_dir}/chunk_{chunk_num:04d}.parquet"
    df.to_parquet(path, index=False)
    return path
