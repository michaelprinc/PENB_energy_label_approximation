"""
Test WeatherAPI Search/Autocomplete API pro získání Location ID
"""

from core.config import get_api_key
import requests
import json


def test_search_api():
    """
    Testuje Search API pro zjištění location ID
    """
    print("="*70)
    print("TEST SEARCH/AUTOCOMPLETE API")
    print("="*70)
    
    api_key = get_api_key()
    if not api_key:
        print("\nCHYBA: API klic neni nastaven!")
        return
    
    print(f"\nOK: API klic nacten\n")
    
    # Testovací lokace
    test_queries = [
        "Praha",
        "50.0755,14.4378",  # GPS Praha
        "London",
        "New York"
    ]
    
    results = {}
    
    for query in test_queries:
        print(f"-"*70)
        print(f"QUERY: {query}")
        print(f"-"*70)
        
        try:
            url = "http://api.weatherapi.com/v1/search.json"
            params = {
                'key': api_key,
                'q': query
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data:
                print(f"\nNalezeno {len(data)} lokaci:\n")
                
                for i, loc in enumerate(data, 1):
                    print(f"{i}. {loc['name']}, {loc['region']}, {loc['country']}")
                    print(f"   ID: {loc['id']}")
                    print(f"   GPS: {loc['lat']}, {loc['lon']}")
                    print(f"   URL: {loc['url']}")
                    print()
                
                # Ulož první výsledek
                results[query] = data[0]
            else:
                print(f"\nZadna lokace nenalezena")
                results[query] = None
                
        except Exception as e:
            print(f"\nCHYBA: {e}")
            results[query] = None
    
    # Souhrn
    print(f"\n{'='*70}")
    print("SOUHRN - LOCATION ID MAPPING")
    print(f"{'='*70}\n")
    
    for query, loc in results.items():
        if loc:
            print(f"{query:30} -> ID: {loc['id']:10} ({loc['name']}, {loc['country']})")
        else:
            print(f"{query:30} -> NENALEZENO")
    
    print(f"\n{'='*70}\n")
    
    # Test použití ID pro dotaz
    if results.get("Praha"):
        praha_id = results["Praha"]["id"]
        print(f"TEST: Pouziti Location ID pro dotaz")
        print(f"-"*70)
        print(f"Location ID pro Prahu: {praha_id}")
        
        try:
            url = "http://api.weatherapi.com/v1/current.json"
            params = {
                'key': api_key,
                'q': f'id:{praha_id}'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            print(f"\nOK: Dotaz s ID funguje!")
            print(f"Lokace: {data['location']['name']}")
            print(f"Teplota: {data['current']['temp_c']}°C")
            print(f"Pocasi: {data['current']['condition']['text']}")
            
        except Exception as e:
            print(f"\nCHYBA pri pouziti ID: {e}")
    
    print(f"\n{'='*70}\n")


def test_location_caching():
    """
    Ukázka jak cachovat location ID
    """
    print("="*70)
    print("UKAZKA: LOCATION ID CACHING")
    print("="*70)
    
    # Simulace cache
    cache = {}
    
    def get_location_id(query, api_key):
        """Získá ID s cachingem"""
        
        # Check cache
        if query in cache:
            print(f"  [CACHE HIT] {query} -> ID: {cache[query]}")
            return cache[query]
        
        # Fetch from API
        print(f"  [API CALL] Fetching ID for {query}...")
        url = "http://api.weatherapi.com/v1/search.json"
        params = {'key': api_key, 'q': query}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data:
                loc_id = data[0]['id']
                cache[query] = loc_id
                print(f"  [CACHED] {query} -> ID: {loc_id}")
                return loc_id
        except:
            pass
        
        return None
    
    api_key = get_api_key()
    if not api_key:
        return
    
    # Test
    print("\nPrvni dotazy (API calls):")
    get_location_id("Praha", api_key)
    get_location_id("London", api_key)
    
    print("\nDruhe dotazy (z cache):")
    get_location_id("Praha", api_key)
    get_location_id("London", api_key)
    
    print(f"\nCache obsah:")
    print(json.dumps(cache, indent=2))
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    test_search_api()
    test_location_caching()
