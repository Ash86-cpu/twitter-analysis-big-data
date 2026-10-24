"""Chunked processing pipeline: zipped tweet archives in, Parquet chunks out.

Usage:
    python -m data_processing.process_tweets --input data/raw/sample.zip --output data/processed
"""

import argparse
import logging
from pathlib import Path

import pandas as pd

from .extract_tweets import save_chunk, stream_tweets
from .utils.memory import optimize_dtypes

logger = logging.getLogger(__name__)


def _write(rows, chunk_num, output_dir) -> str:
    df = optimize_dtypes(pd.DataFrame(rows))
    return save_chunk(df, chunk_num, output_dir)


def process_large_data(input_zip, output_dir, chunk_size=50_000, max_files=None) -> int:
    """Stream tweets and write them out in fixed-size chunks.

    Only one chunk is ever held in memory, which is what lets the pipeline
    handle archives far larger than the machine's RAM. Returns the number of
    tweets processed.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    rows, chunk_num, total = [], 0, 0
    for tweet in stream_tweets(input_zip, max_files=max_files):
        rows.append(tweet)
        total += 1
        if len(rows) == chunk_size:
            _write(rows, chunk_num, output_dir)
            logger.info("Processed %d tweets", total)
            rows, chunk_num = [], chunk_num + 1

    if rows:  # final partial chunk
        _write(rows, chunk_num, output_dir)

    logger.info("Done: %d tweets written to %s", total, output_dir)
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="Process zipped tweet archives into Parquet chunks.")
    parser.add_argument("--input", required=True, help="zip file of JSON tweet arrays")
    parser.add_argument("--output", required=True, help="folder for the Parquet chunks")
    parser.add_argument("--chunk-size", type=int, default=50_000, help="tweets per chunk (default 50000)")
    parser.add_argument("--max-files", type=int, default=None, help="only read the first N files (for quick tests)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    process_large_data(args.input, args.output, args.chunk_size, args.max_files)


if __name__ == "__main__":
    main()
