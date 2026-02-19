import requests
import zipfile
import io
import re
import pandas as pd
import pickle

# FIDE IDs and display names for 2026 Candidates
OPEN_CANDIDATES = {
    '2016192': 'Nakamura, Hikaru',
    '2020009': 'Caruana, Fabiano',
    '24116068': 'Giri, Anish',
    '25059530': 'Praggnanandhaa R',
    '8603405': 'Wei, Yi',
    '14205483': 'Sindarov, Javokhir',
    '24175439': 'Esipenko, Andrey',
    '24651516': 'Bluebaum, Matthias',
}

WOMEN_CANDIDATES = {
    '8608059': 'Zhu, Jiner',
    '5008123': 'Koneru, Humpy',
    '4147103': 'Goryachkina, Aleksandra',
    '8603642': 'Tan, Zhongyi',
    '14109336': 'Lagno, Kateryna',
    '35006916': 'Deshmukh, Divya',
    '13708694': 'Assaubayeva, Bibisara',
    '5091756': 'Rameshbabu, Vaishali',
}

FIDE_URLS = {
    'Classic': 'https://ratings.fide.com/download/standard_rating_list.zip',
    'Rapid': 'https://ratings.fide.com/download/rapid_rating_list.zip',
    'Blitz': 'https://ratings.fide.com/download/blitz_rating_list.zip',
}


def download_and_extract(url):
    """Download a FIDE rating list ZIP and return the text content."""
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        filename = z.namelist()[0]
        return z.read(filename).decode('latin-1')


def parse_ratings(text_content, target_ids):
    """Parse a FIDE rating list and extract ratings for target FIDE IDs.

    The FIDE TXT format is fixed-width. The rating column header changes
    monthly (FEB26, MAR26, etc.) so we find it dynamically via regex.
    """
    lines = text_content.split('\n')
    header = lines[0]

    # Find rating column position (e.g., "FEB26", "MAR26")
    match = re.search(r'[A-Z]{3}\d{2}', header)
    if not match:
        raise RuntimeError(f"Could not find rating column in FIDE header: {header[:120]}")
    rating_start = match.start()
    rating_label = match.group()

    ratings = {}
    for line in lines[1:]:
        if len(line) < rating_start + 4:
            continue
        fide_id = line[:15].strip()
        if fide_id in target_ids:
            rating_str = line[rating_start:rating_start + 6].strip()
            if rating_str and rating_str.isdigit():
                ratings[fide_id] = int(rating_str)

    return ratings, rating_label


def scrape_fide_ratings(candidates_dict):
    """Download FIDE lists and build a DataFrame of ratings for candidates."""
    all_ids = set(candidates_dict.keys())

    results = {}
    for fide_id, name in candidates_dict.items():
        results[fide_id] = {'Name': name, 'Classic': 0, 'Rapid': 0, 'Blitz': 0}

    rating_label = None
    for format_name, url in FIDE_URLS.items():
        print(f"  Downloading FIDE {format_name} list...")
        text = download_and_extract(url)
        ratings, rating_label = parse_ratings(text, all_ids)
        for fide_id, rating in ratings.items():
            results[fide_id][format_name] = rating

    # Check for missing players
    for fide_id, data in results.items():
        if data['Classic'] == 0:
            print(f"  WARNING: No classical rating found for {data['Name']} (FIDE ID: {fide_id})")

    df = pd.DataFrame(list(results.values()))
    return df, rating_label


def main():
    try:
        print("Fetching FIDE ratings for Open Candidates...")
        open_df, label = scrape_fide_ratings(OPEN_CANDIDATES)
        pickle.dump(open_df, open("./chessSim/data/playerData.p", "wb"))

        print(f"\nOpen Candidates ({label}):")
        print(f"  {'Name':<28} {'Classic':>8} {'Rapid':>7} {'Blitz':>7}")
        print(f"  {'-'*52}")
        for _, row in open_df.iterrows():
            print(f"  {row['Name']:<28} {row['Classic']:>8} {row['Rapid']:>7} {row['Blitz']:>7}")

        print(f"\nFetching FIDE ratings for Women's Candidates...")
        women_df, label = scrape_fide_ratings(WOMEN_CANDIDATES)
        pickle.dump(women_df, open("./chessSim/data/playerDataWomen.p", "wb"))

        print(f"\nWomen's Candidates ({label}):")
        print(f"  {'Name':<28} {'Classic':>8} {'Rapid':>7} {'Blitz':>7}")
        print(f"  {'-'*52}")
        for _, row in women_df.iterrows():
            print(f"  {row['Name']:<28} {row['Classic']:>8} {row['Rapid']:>7} {row['Blitz']:>7}")

        print("\nFIDE ratings saved to playerData.p and playerDataWomen.p")

    except Exception as e:
        raise RuntimeError(f"FIDE ratings download failed. Use --ratings cached to skip. Error: {e}") from e


if __name__ == "__main__" or __name__ == "scrape_fide":
    main()
