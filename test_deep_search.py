"""
Deep search to find the shutdown market by trying different API parameters
"""

import asyncio
import aiohttp


async def search_for_shutdown_market():
    """Try different API configurations to find the shutdown market."""
    
    print("="*80)
    print("DEEP SEARCH FOR GOVERNMENT SHUTDOWN MARKET")
    print("="*80)
    
    base_url = "https://gamma-api.polymarket.com/markets"
    
    # Try different parameter combinations
    test_configs = [
        {"name": "Active only (closed=false)", "params": {'closed': 'false', 'limit': 500}},
        {"name": "All markets (no filter)", "params": {'limit': 500}},
        {"name": "Closed markets only", "params": {'closed': 'true', 'limit': 500}},
        {"name": "Active=true", "params": {'active': 'true', 'limit': 500}},
        {"name": "Active=false", "params": {'active': 'false', 'limit': 500}},
        {"name": "No limit, no closed filter", "params": {}},
    ]
    
    async with aiohttp.ClientSession() as session:
        for config in test_configs:
            print(f"\n{'='*80}")
            print(f"Testing: {config['name']}")
            print(f"Params: {config['params']}")
            print('-'*80)
            
            try:
                async with session.get(base_url, params=config['params'], timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        print(f"❌ Status {response.status}")
                        continue
                    
                    data = await response.json()
                    markets = data if isinstance(data, list) else data.get('data', [])
                    
                    print(f"✅ Fetched {len(markets)} markets")
                    
                    # Search for shutdown-related markets
                    shutdown_markets = [
                        m for m in markets 
                        if 'shutdown' in m.get('question', '').lower()
                    ]
                    
                    if shutdown_markets:
                        print(f"\n🎯 FOUND {len(shutdown_markets)} SHUTDOWN MARKET(S):")
                        for market in shutdown_markets:
                            print(f"\n  Question: {market['question']}")
                            print(f"  Slug: {market.get('slug', 'N/A')}")
                            print(f"  Active: {market.get('active', 'N/A')}")
                            print(f"  Closed: {market.get('closed', 'N/A')}")
                            print(f"  End Date: {market.get('endDate', 'N/A')}")
                            
                            # Check if it matches the specific one
                            if 'when will' in market['question'].lower() and 'end' in market['question'].lower():
                                print(f"  ⭐ THIS IS THE ONE WE'RE LOOKING FOR!")
                    else:
                        print("  ❌ No shutdown markets found in this set")
                        
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print("\n" + "="*80)
    print("DEEP SEARCH COMPLETE")
    print("="*80)


async def check_market_by_slug():
    """Try to fetch a specific market by slug if we know it."""
    
    print("\n\n" + "="*80)
    print("CHECKING SPECIFIC MARKET BY SLUG")
    print("="*80)
    
    # Common slug patterns for government shutdown markets
    possible_slugs = [
        "when-will-the-government-shutdown-end",
        "government-shutdown-end",
        "when-government-shutdown-end",
        "next-government-shutdown",
        "government-shutdown-2024",
        "government-shutdown-2025",
    ]
    
    base_url = "https://gamma-api.polymarket.com"
    
    async with aiohttp.ClientSession() as session:
        for slug in possible_slugs:
            url = f"{base_url}/markets/{slug}"
            print(f"\nTrying: {url}")
            
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        market = await response.json()
                        print(f"  ✅ FOUND!")
                        print(f"  Question: {market.get('question', 'N/A')}")
                        print(f"  Closed: {market.get('closed', 'N/A')}")
                        print(f"  Active: {market.get('active', 'N/A')}")
                        return
                    else:
                        print(f"  ❌ Status {response.status}")
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    print("\n❌ Could not find market by any common slug pattern")


async def search_by_keyword():
    """Search using a search endpoint if available."""
    
    print("\n\n" + "="*80)
    print("TRYING SEARCH ENDPOINT")
    print("="*80)
    
    base_url = "https://gamma-api.polymarket.com"
    search_endpoints = [
        "/search?query=shutdown",
        "/markets/search?q=shutdown",
        "/markets?search=shutdown",
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in search_endpoints:
            url = f"{base_url}{endpoint}"
            print(f"\nTrying: {url}")
            
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    print(f"  Status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        print(f"  ✅ Response received!")
                        print(f"  Data type: {type(data)}")
                        if isinstance(data, dict):
                            print(f"  Keys: {list(data.keys())}")
            except Exception as e:
                print(f"  ❌ Error: {e}")


def main():
    print("\n🔍 Starting deep search for government shutdown market...\n")
    asyncio.run(search_for_shutdown_market())
    asyncio.run(check_market_by_slug())
    asyncio.run(search_by_keyword())
    
    print("\n\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("\nConclusion:")
    print("If no shutdown markets were found in any configuration,")
    print("the market likely:")
    print("  1. Has already closed/resolved")
    print("  2. Doesn't exist in the API (only on website)")
    print("  3. Requires authentication to access")
    print("  4. Is in a different API endpoint we haven't tried")


if __name__ == "__main__":
    main()