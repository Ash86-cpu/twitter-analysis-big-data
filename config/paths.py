from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'

RAW_DATA = DATA_DIR / 'raw'
PROCESSED_DATA = DATA_DIR / 'processed'
OUTPUTS = BASE_DIR / 'outputs'

# Create directories
for path in [RAW_DATA, PROCESSED_DATA, OUTPUTS]:
    path.mkdir(parents=True, exist_ok=True)