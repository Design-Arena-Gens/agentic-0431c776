import requests
from bs4 import BeautifulSoup
import csv
import re

def scrape_betting_odds(url):
    """Scrape betting odds from FDJ Parions Sport page"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    data = []

    # Find all betting sections
    bet_sections = soup.find_all(['div', 'section'], class_=re.compile('bet|pari|cote', re.I))

    # Also look for table rows and divs with betting data
    all_elements = soup.find_all(['tr', 'div', 'li'], recursive=True)

    for element in all_elements:
        text = element.get_text(strip=True)

        # Pattern matching for different bet types

        # 1/N/2 basic odds
        if re.search(r'N°\d+.*1.*N.*2', text):
            bet_type = re.search(r'(N°\d+.*?)(?:\d+,\d+|$)', text)
            if bet_type:
                bet_name = bet_type.group(1).strip()

                # Extract odds
                odds = re.findall(r'\d+,\d+', text)
                percentages = re.findall(r'(\d+)%', text)

                if len(odds) >= 3:
                    data.append({
                        'Type de pari': bet_name,
                        'Option 1': '1',
                        'Cote 1': odds[0],
                        'Option 2': 'N',
                        'Cote 2': odds[1],
                        'Option 3': '2',
                        'Cote 3': odds[2],
                        'Pourcentage 1': percentages[0] + '%' if len(percentages) > 0 else '',
                        'Pourcentage 2': percentages[1] + '%' if len(percentages) > 1 else '',
                        'Pourcentage 3': percentages[2] + '%' if len(percentages) > 2 else ''
                    })

        # Plus/Moins bets
        elif 'Plus/Moins' in text and re.search(r'Plus.*?\d+,?\d*.*?Moins.*?\d+,?\d*', text):
            bet_name_match = re.search(r'(N°\d+.*?(?:Plus/Moins|buts?).*?)(?:Plus|$)', text, re.I)
            bet_name = bet_name_match.group(1).strip() if bet_name_match else 'Plus/Moins'

            odds = re.findall(r'\d+,\d+', text)
            percentages = re.findall(r'(\d+)%', text)

            if len(odds) >= 2:
                data.append({
                    'Type de pari': bet_name,
                    'Option 1': 'Plus',
                    'Cote 1': odds[0],
                    'Option 2': 'Moins',
                    'Cote 2': odds[1],
                    'Option 3': '',
                    'Cote 3': '',
                    'Pourcentage 1': percentages[0] + '%' if len(percentages) > 0 else '',
                    'Pourcentage 2': percentages[1] + '%' if len(percentages) > 1 else '',
                    'Pourcentage 3': ''
                })

        # Les 2 équipes marquent
        elif 'équipes marquent' in text.lower():
            bet_name_match = re.search(r'(N°\d+.*?marquent.*?)(?:Oui|$)', text, re.I)
            bet_name = bet_name_match.group(1).strip() if bet_name_match else 'Les 2 équipes marquent'

            odds = re.findall(r'\d+,\d+', text)
            percentages = re.findall(r'(\d+)%', text)

            if len(odds) >= 2:
                data.append({
                    'Type de pari': bet_name,
                    'Option 1': 'Oui',
                    'Cote 1': odds[0],
                    'Option 2': 'Non',
                    'Cote 2': odds[1],
                    'Option 3': '',
                    'Cote 3': '',
                    'Pourcentage 1': percentages[0] + '%' if len(percentages) > 0 else '',
                    'Pourcentage 2': percentages[1] + '%' if len(percentages) > 1 else '',
                    'Pourcentage 3': ''
                })

        # Score Exact
        elif 'Score exact' in text or 'Score Exact' in text:
            scores = re.findall(r'(\d+\s*-\s*\d+)\s*(\d+,?\d*)', text)
            if scores:
                bet_name_match = re.search(r'(N°\d+.*?[Ss]core.*?)(?:\d|$)', text)
                bet_name = bet_name_match.group(1).strip() if bet_name_match else 'Score exact'

                for score, odds in scores[:3]:
                    data.append({
                        'Type de pari': bet_name,
                        'Option 1': score.replace(' ', ''),
                        'Cote 1': odds.replace(',', '.') if ',' in odds else odds,
                        'Option 2': '',
                        'Cote 2': '',
                        'Option 3': '',
                        'Cote 3': '',
                        'Pourcentage 1': '',
                        'Pourcentage 2': '',
                        'Pourcentage 3': ''
                    })

        # Double chance
        elif 'Double chance' in text:
            bet_name_match = re.search(r'(N°\d+.*?[Dd]ouble.*?chance.*?)(?:\d|1/N|$)', text)
            bet_name = bet_name_match.group(1).strip() if bet_name_match else 'Double chance'

            odds = re.findall(r'\d+,\d+', text)
            percentages = re.findall(r'(\d+)%', text)

            if len(odds) >= 3:
                data.append({
                    'Type de pari': bet_name,
                    'Option 1': '1/N',
                    'Cote 1': odds[0],
                    'Option 2': 'N/2',
                    'Cote 2': odds[1],
                    'Option 3': '1/2',
                    'Cote 3': odds[2],
                    'Pourcentage 1': percentages[0] + '%' if len(percentages) > 0 else '',
                    'Pourcentage 2': percentages[1] + '%' if len(percentages) > 1 else '',
                    'Pourcentage 3': percentages[2] + '%' if len(percentages) > 2 else ''
                })

        # Handicap
        elif 'Handicap' in text and 'Face' not in text:
            bet_name_match = re.search(r'(N°\d+.*?[Hh]andicap.*?)(?:\d+,\d+|$)', text)
            bet_name = bet_name_match.group(1).strip() if bet_name_match else 'Handicap'

            odds = re.findall(r'\d+,\d+', text)
            percentages = re.findall(r'(\d+)%', text)

            if len(odds) >= 3:
                data.append({
                    'Type de pari': bet_name,
                    'Option 1': '1',
                    'Cote 1': odds[0],
                    'Option 2': 'N',
                    'Cote 2': odds[1],
                    'Option 3': '2',
                    'Cote 3': odds[2],
                    'Pourcentage 1': percentages[0] + '%' if len(percentages) > 0 else '',
                    'Pourcentage 2': percentages[1] + '%' if len(percentages) > 1 else '',
                    'Pourcentage 3': percentages[2] + '%' if len(percentages) > 2 else ''
                })

    return data

def save_to_csv(data, filename='betting_odds.csv'):
    """Save scraped data to CSV file"""

    if not data:
        print("No data to save")
        return

    keys = ['Type de pari', 'Option 1', 'Cote 1', 'Option 2', 'Cote 2',
            'Option 3', 'Cote 3', 'Pourcentage 1', 'Pourcentage 2', 'Pourcentage 3']

    with open(filename, 'w', newline='', encoding='utf-8-sig') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

    print(f"Data saved to {filename}")
    print(f"Total rows: {len(data)}")

if __name__ == "__main__":
    url = "https://www.pointdevente.parionssport.fdj.fr/paris-ouverts/football/efl-cup/46491/match_arsenal_crystal-palace/1224009"

    print(f"Scraping data from: {url}")

    try:
        betting_data = scrape_betting_odds(url)
        save_to_csv(betting_data)
    except Exception as e:
        print(f"Error: {e}")
