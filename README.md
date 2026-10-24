# Large-Scale Twitter Data Analysis

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

A memory-efficient Python pipeline for processing and analysing large archives
of geotagged tweets. Built for an MSc assignment at the University of Exeter
(2023), where it processed 15M+ geotagged tweets from across Europe drawn from
450GB+ of compressed archives.

The core problem is that the data is far larger than a laptop's memory. The
pipeline never loads a whole file: it streams tweets one at a time out of the
zipped archives and writes them back out in fixed-size Parquet chunks.

## How it works

```
zipped JSON archives  ->  stream_tweets()  ->  50,000-tweet chunks  ->  optimize_dtypes()  ->  Parquet files  ->  analysis notebook
```

| File | Responsibility |
|---|---|
| `data_processing/extract_tweets.py` | Streams tweets out of `.zip` archives with `ijson`, an incremental JSON parser, keeping only the fields needed (id, text, user, coordinates, timestamp, mentions) |
| `data_processing/utils/memory.py` | Converts columns to compact types and the millisecond timestamp to a real datetime |
| `data_processing/process_tweets.py` | Command-line pipeline that groups tweets into chunks and writes each as Parquet |
| `data_processing/make_sample.py` | Generates a small synthetic archive so the pipeline can be tried without real data |
| `config/paths.py` | Project folder locations |
| `analysis/temporal_analysis.ipynb` | Daily and hourly tweet volume charts |

Design points:

- **Streaming, not loading.** `ijson` reads each JSON file incrementally, so
  memory use stays flat whether the archive is 100MB or 450GB.
- **Chunked output.** Only one chunk of tweets is held in memory at a time.
  Parquet is columnar and compressed, so later analysis reads only the
  columns it needs.
- **Field selection at the source.** A raw tweet object carries dozens of
  fields; keeping six of them cuts the data volume before it is ever stored.

## Quick start

Requires Python 3.9 or newer.

```bash
git clone https://github.com/Ash86-cpu/twitter-analysis-big-data.git
cd twitter-analysis-big-data
pip install -r requirements.txt

# Create a synthetic sample (6,000 fake tweets across six European cities)
python -m data_processing.make_sample

# Run the pipeline on it
python -m data_processing.process_tweets --input data/raw/sample.zip --output data/processed
```

Then open `analysis/temporal_analysis.ipynb` in Jupyter to plot the results.

Options for `process_tweets`:

| Option | Purpose |
|---|---|
| `--input` | Zip file containing JSON arrays of tweets |
| `--output` | Folder for the Parquet chunks |
| `--chunk-size` | Tweets per chunk (default 50,000) |
| `--max-files` | Only read the first N files, for quick tests |

## Data

The original dataset is not included: it is far too large for GitHub, and
Twitter's terms do not allow redistributing tweet content. `make_sample.py`
produces synthetic tweets in the same structure so the pipeline can be run end
to end. The pipeline expects each `.json` file in the archive to contain a JSON
array of tweet objects in Twitter's v1.1 format.

## License

MIT. See [LICENSE](LICENSE).
