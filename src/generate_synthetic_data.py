"""Generate synthetic real-estate listings to simulate scraped data.

Produces a CSV with 4,000+ rows and 18+ columns matching the assignment schema.
Run: python src/generate_synthetic_data.py
"""
import random
import uuid
from pathlib import Path
import pandas as pd
import numpy as np


def random_area():
    return round(random.uniform(250, 2500), 1)  # square feet


def random_rent(area, city_factor):
    base = area * city_factor * random.uniform(0.7, 1.5)
    return round(base, 2)


def gen_row(i, city='Mumbai'):
    city_factors = {'Mumbai': 6.0, 'Bengaluru':4.0, 'Delhi':5.0}
    factor = city_factors.get(city, 4.5)
    area = random_area()
    rooms = random.choice([1,1,1,2,2,3,3,4])
    floor = random.choice(list(range(1, 31)))
    total_floors = random.choice([4,5,6,7,8,10,12,15,20,25])
    furnished = random.choice(['Furnished','Semi-Furnished','Unfurnished'])
    amenities = random.sample(['Lift','Parking','Gym','Pool','PowerBackup','Security','Garden','ClubHouse'], k=random.randint(0,4))
    lat = round(19.0 + random.uniform(-0.2, 0.2), 6)  # approx Mumbai
    lon = round(72.8 + random.uniform(-0.2, 0.2), 6)
    price = random_rent(area, factor)
    return {
        'id': str(uuid.uuid4()),
        'title': f"{rooms} BHK Flat in {city} - Area {area} sq.ft",
        'city': city,
        'locality': random.choice(['Andheri','Bandra','Powai','Juhu','Mahim','Dadar','Goregaon','Malad']),
        'area_sqft': area,
        'bhk': rooms,
        'floor': floor,
        'total_floors': total_floors,
        'furnished': furnished,
        'amenities': '|'.join(amenities),
        'latitude': lat,
        'longitude': lon,
        'rent_per_month': price,
        'maintenance': round(max(0, random.gauss(4000, 1500))),
        'deposit': round(price * random.choice([2,3,4,5])),
        'listed_on': pd.Timestamp('2025-01-01') + pd.to_timedelta(random.randint(0, 365), unit='d'),
        'contact_available': random.choice([True, True, True, False]),
        'url': f"https://example.com/listing/{i}"
    }


def generate(n=4000, out_path=None):
    rows = [gen_row(i) for i in range(n)]
    df = pd.DataFrame(rows)
    out = Path(out_path or Path('data') / 'raw' / 'scraped_data_raw.csv')
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} rows to {out}")


if __name__ == '__main__':
    generate(4000)
