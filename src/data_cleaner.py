"""Clean raw scraped data and produce processed dataset with 15+ columns.

This module reads `data/raw/scraped_data_raw.csv` (or the example scraper file) and
produces `data/processed/scraped_data.csv` with cleaned types and engineered features.
"""
from pathlib import Path
import pandas as pd
import numpy as np


def load_raw(path=None):
    p = Path(path or 'data/raw/scraped_data_raw.csv')
    if not p.exists():
        # fallback to scraper example if synthetic raw doesn't exist
        p = Path('data/raw/scraper_example.csv')
    return pd.read_csv(p)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    # Standardize column names
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]

    # Convert numeric
    for col in ['area_sqft','rent_per_month','maintenance','deposit']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Dates
    if 'listed_on' in df.columns:
        df['listed_on'] = pd.to_datetime(df['listed_on'], errors='coerce')
    else:
        df['listed_on'] = pd.NaT

    # Fill locality
    if 'locality' not in df.columns:
        df['locality'] = 'Unknown'

    # Feature: price per sqft
    df['price_per_sqft'] = df['rent_per_month'] / df['area_sqft']

    # Feature: amenity count
    if 'amenities' in df.columns:
        df['amenity_count'] = df['amenities'].fillna('').apply(lambda x: 0 if x == '' else len(str(x).split('|')))
    else:
        df['amenity_count'] = 0

    # Fill categorical
    for col in ['furnished','city']:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')

    # Coordinates
    for col in ['latitude','longitude']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows without price or area
    df = df.dropna(subset=['rent_per_month','area_sqft'])

    # Keep at least 15 columns; add safe derived columns
    df['is_ground_floor'] = df.get('floor', 0) == 0
    df['floor_ratio'] = df.get('floor', 0) / df.get('total_floors', 1)

    # Reorder and select
    desired = ['id','title','city','locality','area_sqft','bhk','floor','total_floors','furnished',
               'amenities','amenity_count','latitude','longitude','rent_per_month','maintenance',
               'deposit','listed_on','price_per_sqft','is_ground_floor','floor_ratio']

    for col in desired:
        if col not in df.columns:
            df[col] = np.nan

    return df[desired]


def save(df: pd.DataFrame, out_path=None):
    out = Path(out_path or 'data/processed/scraped_data.csv')
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Saved processed data to {out} ({len(df)} rows)")


def main():
    raw = load_raw()
    df = clean(raw)
    save(df)


if __name__ == '__main__':
    main()
