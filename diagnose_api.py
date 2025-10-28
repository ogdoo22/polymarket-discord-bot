"""
Diagnostic script to check what the Polymarket API is actually returning
Run this to see what markets are available and test fuzzy matching
"""

import asyncio
import aiohttp
from fuzzy_matcher import find_matching_markets


async def diagnose_api():
    """Check what the API is returning and test matching."""
    
    print("="*80)
    print("POLYMARKET API DIAGNOSTIC TOOL")
    print("="*80)
    
    # Test the actual API endpoint
    api_url = "https://gamma-api.polymarket.com/markets"
    params = {
        'closed': 'false',
        'limit': 1000  # Increased to match bot configuration
    }
    
    print("\n[1] TESTING API CONNECTION")
    print(f"URL: {api_url}")
    print(f"Params: {params}")
    print("-"*80)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"Status Code: {response.status}")
                
                if response.status != 200:
                    print(f"❌ ERROR: API returned status {response.status}")
                    print(f"Response: {await response.text()}")
                    return
                
                data = await response.json()
                
                # Check response structure
                if isinstance(data, list):
                    markets = data
                    print(f"✅ API returned a list with {len(markets)} markets")
                elif isinstance(data, dict) and 'data' in data:
                    markets = data['data']
                    print(f"✅ API returned a dict with {len(markets)} markets in 'data' field")
                else:
                    print(f"❌ ERROR: Unexpected response structure")
                    print(f"Response type: {type(data)}")
                    print(f"Keys: {data.keys() if isinstance(data, dict) else 'N/A'}")
                    return
                
                print(f"\n[2] ANALYZING MARKETS")
                print("-"*80)
                
                # Show first 5 market questions
                print("\nFirst 10 market questions:")
                for i, market in enumerate(markets[:10], 1):
                    question = market.get('question', 'NO QUESTION FIELD')
                    print(f"{i:2d}. {question}")
                
                # Search for shutdown-related markets
                print("\n[3] SEARCHING FOR SHUTDOWN-RELATED MARKETS")
                print("-"*80)
                shutdown_markets = [m for m in markets if 'shutdown' in m.get('question', '').lower()]
                print(f"Found {len(shutdown_markets)} markets containing 'shutdown':")
                for i, market in enumerate(shutdown_markets[:5], 1):
                    print(f"{i}. {market['question']}")
                
                # Test specific query
                print("\n[4] TESTING FUZZY MATCHING")
                print("-"*80)
                test_queries = [
                    "When will the government shutdown end",
                    "government shutdown end",
                    "shutdown",
                    "Trump Department Education"
                ]
                
                for query in test_queries:
                    print(f"\nQuery: '{query}'")
                    matches = find_matching_markets(query, markets)
                    
                    if matches:
                        print(f"✅ Found {len(matches)} match(es):")
                        for j, (market, score) in enumerate(matches[:3], 1):
                            print(f"  {j}. [{score:5.1f}%] {market['question']}")
                    else:
                        print("❌ No matches found")
                
                # Check for the specific market
                print("\n[5] LOOKING FOR SPECIFIC MARKET")
                print("-"*80)
                target = "When will the government shutdown end?"
                found = False
                for market in markets:
                    if target.lower() in market.get('question', '').lower():
                        print(f"✅ FOUND: '{market['question']}'")
                        print(f"   Slug: {market.get('slug', 'N/A')}")
                        print(f"   Active: {market.get('active', 'N/A')}")
                        print(f"   Closed: {market.get('closed', 'N/A')}")
                        found = True
                        break
                
                if not found:
                    print(f"❌ Market '{target}' NOT FOUND in API response")
                    print("\nPossible reasons:")
                    print("  1. Market might be closed (we filter closed=false)")
                    print("  2. Market might be outside the limit=100 range")
                    print("  3. Market question text might be slightly different")
                    print("  4. API endpoint might need different parameters")
                
                # Show a sample market structure
                print("\n[6] SAMPLE MARKET STRUCTURE")
                print("-"*80)
                if markets:
                    import json
                    print(json.dumps(markets[0], indent=2))
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("DIAGNOSTIC COMPLETE")
    print("="*80)


async def check_alternative_endpoints():
    """Try different API endpoints to see what data is available."""
    
    print("\n\n[BONUS] CHECKING ALTERNATIVE ENDPOINTS")
    print("="*80)
    
    endpoints = [
        "/markets?closed=false&limit=100",
        "/markets?limit=100",
        "/markets?active=true&limit=100",
        "/markets?closed=false&limit=500",
    ]
    
    base_url = "https://gamma-api.polymarket.com"
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                print(f"\nTrying: {url}")
                
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, list):
                            count = len(data)
                        elif isinstance(data, dict) and 'data' in data:
                            count = len(data['data'])
                        else:
                            count = "unknown"
                        print(f"  ✅ Status 200 - {count} markets")
                    else:
                        print(f"  ❌ Status {response.status}")
            except Exception as e:
                print(f"  ❌ Error: {e}")


def main():
    """Run the diagnostic."""
    print("\n🔍 Starting Polymarket API Diagnostics...\n")
    asyncio.run(diagnose_api())
    asyncio.run(check_alternative_endpoints())
    print("\n✅ Diagnostic complete. Check the output above.\n")


if __name__ == "__main__":
    main()