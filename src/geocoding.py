"""Geocoding module: reverse geocoding and distance calculations.

Integrates Google Maps API and OpenStreetMap Nominatim for:
- Reverse geocoding (lat/lon -> address components).
- Distance calculations to landmarks (metro stations, CBD).

This module can be used standalone or integrated into the main cleaning pipeline.
"""
import os
from pathlib import Path
from typing import Tuple, Dict, Optional
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from dotenv import load_dotenv

# Try to load Google Maps API key from .env if available
load_dotenv()
GMAPS_KEY = os.getenv('GOOGLE_MAPS_API_KEY', None)

# Mumbai landmarks (lat, lon) for distance calculations
LANDMARKS = {
    'CBD_Bandra': (19.0596, 72.8295),
    'CST_Railway': (18.9432, 72.8236),
    'Mumbai_Airport': (19.0896, 72.8656),
    'Powai_IT_Hub': (19.1136, 72.9027),
}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two lat/lon points using Haversine formula."""
    R = 6371  # Earth radius in km
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    a = np.sin(delta_phi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c


def reverse_geocode_nominatim(lat: float, lon: float) -> Dict[str, str]:
    """
    Reverse geocode using Nominatim (OpenStreetMap) as fallback.
    Returns address components.
    """
    try:
        geolocator = Nominatim(user_agent="real_estate_ml_pipeline")
        location = geolocator.reverse((lat, lon), language='en', timeout=5)
        address = location.raw.get('address', {})
        return {
            'street': address.get('road', ''),
            'locality': address.get('city', address.get('town', '')),
            'district': address.get('county', ''),
            'postal_code': address.get('postcode', ''),
        }
    except Exception as e:
        return {'street': '', 'locality': '', 'district': '', 'postal_code': ''}


def add_distance_features(df: pd.DataFrame, lat_col='latitude', lon_col='longitude') -> pd.DataFrame:
    """
    Add distance-to-landmark columns (in km) to dataframe.
    
    Args:
        df: DataFrame with lat/lon columns.
        lat_col, lon_col: Column names for latitude and longitude.
    
    Returns:
        DataFrame with new distance columns.
    """
    df = df.copy()
    for landmark_name, (lm_lat, lm_lon) in LANDMARKS.items():
        col_name = f'dist_to_{landmark_name.lower()}_km'
        df[col_name] = df.apply(
            lambda row: haversine_distance(row[lat_col], row[lon_col], lm_lat, lm_lon)
            if pd.notna(row[lat_col]) and pd.notna(row[lon_col])
            else np.nan,
            axis=1
        )
    return df


def geocode_batch(df: pd.DataFrame, lat_col='latitude', lon_col='longitude',
                  use_nominatim=True) -> pd.DataFrame:
    """
    Apply reverse geocoding and distance features to a batch of records.
    
    Args:
        df: DataFrame with lat/lon columns.
        lat_col, lon_col: Column names for latitude and longitude.
        use_nominatim: If True, use Nominatim for reverse geocoding.
    
    Returns:
        DataFrame with added geocoding and distance columns.
    """
    df = df.copy()
    
    # Add distance features
    df = add_distance_features(df, lat_col, lon_col)
    
    # Reverse geocoding (optional, slower—use only if needed)
    if use_nominatim:
        print("Running reverse geocoding (this may take a while)...")
        geocoded = df[[lat_col, lon_col]].apply(
            lambda row: reverse_geocode_nominatim(row[lat_col], row[lon_col])
            if pd.notna(row[lat_col]) and pd.notna(row[lon_col])
            else {'street': '', 'locality': '', 'district': '', 'postal_code': ''},
            axis=1,
            result_type='expand'
        )
        df = pd.concat([df, geocoded], axis=1)
    
    return df


def main():
    """Demo: load processed data, add geocoding features, and save."""
    processed_path = Path('data/processed/scraped_data.csv')
    if not processed_path.exists():
        print(f"Processed data not found at {processed_path}. Run data_cleaner.py first.")
        return
    
    df = pd.read_csv(processed_path)
    print(f"Loaded {len(df)} records. Adding geocoding features...")
    
    # Add distance features (fast)
    df = add_distance_features(df)
    
    # Optionally reverse geocode (slow—skip for now)
    # df = geocode_batch(df, use_nominatim=False)
    
    out_path = processed_path.parent / 'scraped_data_with_geocoding.csv'
    df.to_csv(out_path, index=False)
    print(f"Saved geocoded data to {out_path}")
    print(f"New features added: {[c for c in df.columns if 'dist_to_' in c]}")


if __name__ == '__main__':
    main()
