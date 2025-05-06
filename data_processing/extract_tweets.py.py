import zipfile
import ijson
import json
from tqdm import tqdm

def stream_tweets(zip_path, max_files=3):
    """Memory-efficient tweet streaming from compressed archives"""
    with zipfile.ZipFile(zip_path) as z:
        files = [f for f in z.namelist() if f.endswith('.json')][:max_files]
        
        for file in tqdm(files, desc="Processing files"):
            with z.open(file) as f:
                parser = ijson.items(f, 'item')
                for obj in parser:
                    yield {
                        'id': obj.get('id_str'),
                        'text': obj.get('text'),
                        'user_id': obj.get('user', {}).get('id_str'),
                        'coordinates': obj.get('coordinates'),
                        'timestamp': obj.get('timestamp_ms'),
                        'mentions': [u['id_str'] for u in obj.get('entities', {}).get('user_mentions', [])]
                    }

def save_chunk(df, chunk_num, output_dir):
    """Save processed chunks as parquet"""
    path = f"{output_dir}/chunk_{chunk_num:04d}.parquet"
    df.to_parquet(path)
    return path