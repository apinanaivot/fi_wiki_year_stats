import requests
from datetime import datetime
import pandas as pd
from typing import List, Dict
import os
from pathlib import Path

def get_most_viewed_articles(year: int, month: int) -> List[Dict]:
    """
    Fetch most viewed articles for Finnish Wikipedia for a specific month
    """
    base_url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/fi.wikipedia.org/all-access"
    date = f"{year}/{str(month).zfill(2)}/all-days"
    url = f"{base_url}/{date}"
    
    headers = {
        'User-Agent': 'PageviewsAnalysis/1.0 (contact@example.com) Finnish Wikipedia analysis script',
        'accept': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()['items'][0]['articles']

def generate_wiki_markup(df: pd.DataFrame, title: str) -> str:
    """
    Generate Wikipedia markup for the articles
    """
    wiki_text = f"== {title} ==\n\n"
    wiki_text += "{| class=\"wikitable sortable\"\n"
    wiki_text += "! Sija !! Artikkeli !! Katselumäärä\n"
    
    # Make sure data is sorted by views in descending order
    df_sorted = df.sort_values('views', ascending=False).reset_index(drop=True)
    for idx, row in df_sorted.iterrows():
        rank = idx + 1
        article = row['article'].replace('_', ' ')
        if article.startswith('Luokka:'):
            article = ':' + article
        # Store number without spaces for sorting
        # Store number without spaces for sorting
        views = str(int(row['views']))
        formatted_views = f"{int(views):_}".replace('_', ' ')
        wiki_text += f"|-\n| {rank} || [[{article}]] || data-sort-value=\"{views}\" | {formatted_views}\n"
    
    wiki_text += "|}"
    return wiki_text

def ensure_directory(year: int) -> None:
    """Create year directory and its months subdirectory if they don't exist"""
    Path(f"{year}").mkdir(exist_ok=True)
    Path(f"{year}/kuukaudet").mkdir(exist_ok=True)

def save_to_file(content: str, filepath: str) -> None:
    """Save content to specified file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def process_month(year: int, month: int) -> pd.DataFrame:
    """Process a single month's data"""
    try:
        monthly_data = get_most_viewed_articles(year, month)
        df = pd.DataFrame(monthly_data)
        df = df.sort_values('views', ascending=False)
        
        if df.empty:
            print(f"Ei dataa kuukaudelle {month}/{year}")
            return None
            
        # Generate and save monthly file
        month_name = ["tammikuu", "helmikuu", "maaliskuu", "huhtikuu", 
                     "toukokuu", "kesäkuu", "heinäkuu", "elokuu", 
                     "syyskuu", "lokakuu", "marraskuu", "joulukuu"][month-1]
        
        title = f"Suomenkielisen Wikipedian luetuimmat artikkelit {month_name}ssa {year}"
        monthly_markup = generate_wiki_markup(df.head(1000), title)
        save_to_file(monthly_markup, f"{year}/kuukaudet/{month:02d}_{month_name}_{year}.txt")
        
        return df
    except requests.exceptions.HTTPError as e:
        print(f"Virhe haettaessa dataa kuukaudelle {month}/{year}: {e}")
        return None

def main():
    # Get user input
    while True:
        try:
            year = int(input("Anna vuosi (esim. 2024): "))
            break
        except ValueError:
            print("Virheellinen vuosi. Anna kelvollinen vuosiluku.")
    
    while True:
        mode = input("Haluatko datan: \n1) Koko vuodelta\n2) Yhdeltä kuukaudelta\nValitse (1/2): ")
        if mode in ['1', '2']:
            break
        print("Virheellinen valinta. Valitse 1 tai 2.")

    ensure_directory(year)
    
    if mode == '1':
        # Process whole year
        all_data = []
        current_date = datetime.now()
        max_month = current_date.month if current_date.year == year else 12
        
        for month in range(1, max_month + 1):
            print(f"Käsitellään kuukautta {month}/{year}...")
            df = process_month(year, month)
            if df is not None:
                all_data.append(df)
        
        if all_data:
            # Combine all months and aggregate
            combined_df = pd.concat(all_data)
            aggregated = combined_df.groupby('article')['views'].sum().reset_index()
            aggregated = aggregated.sort_values('views', ascending=False)
            
            title = f"Suomenkielisen Wikipedian luetuimmat artikkelit vuonna {year}"
            yearly_markup = generate_wiki_markup(aggregated.head(1000), title)
            save_to_file(yearly_markup, f"{year}/koko_vuosi_{year}.txt")
            print(f"\nTulokset tallennettu kansioon '{year}'")
        else:
            print("Ei dataa saatavilla valitulle vuodelle.")
    
    else:
        # Process single month
        while True:
            try:
                month = int(input("Anna kuukausi (1-12): "))
                if 1 <= month <= 12:
                    break
                print("Anna kuukausi väliltä 1-12.")
            except ValueError:
                print("Virheellinen kuukausi. Anna numero 1-12.")
        
        print(f"Käsitellään kuukautta {month}/{year}...")
        df = process_month(year, month)
        if df is not None:
            print(f"\nTulokset tallennettu kansioon '{year}/kuukaudet'")
        else:
            print("Ei dataa saatavilla valitulle kuukaudelle.")

if __name__ == "__main__":
    main()