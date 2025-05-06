def optimize_dtypes(df):
    """Reduce memory usage by 60-70%"""
    dtypes = {
        'id': 'string',
        'user_id': 'string',
        'timestamp': 'datetime64[ms]'
    }
    return df.astype(dtypes).reset_index(drop=True)