import pandas as pd
from pathlib import Path
from .utils.memory import optimize_dtypes
from .utils.helpers import logger

def process_large_data(input_zip, output_dir, chunk_size=50000):
    """Chunked processing pipeline"""
    Path(output_dir).mkdir(exist_ok=True)
    
    chunk = []
    for i, tweet in enumerate(stream_tweets(input_zip)):
        chunk.append(tweet)
        
        if (i + 1) % chunk_size == 0:
            df = pd.DataFrame(chunk)
            df = optimize_dtypes(df)
            save_chunk(df, i//chunk_size, output_dir)
            chunk = []
            logger.info(f"Processed {i+1} tweets")
    
    if chunk:  # Final partial chunk
        df = pd.DataFrame(chunk)
        save_chunk(df, (i//chunk_size)+1, output_dir)