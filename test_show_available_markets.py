"""
Display all available markets from the API so you know what's searchable
"""

import asyncio
import aiohttp
from collections import defaultdict


async def show_available_markets():
    """Fetch and display all available markets organized by category."""
    
    print("="*80)
    print("AVAILABLE MARKETS IN POLYMARKET API")
    print("="*80)
    print("\nFetching markets from API...")
    
    url = "https://gamma-api.polymarket.com/markets"
    params = {'closed': 'false', 'limit': 500}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status != 200:
                print(f"❌ Error: Status {response.status}")
                return
            
            data = await response.json()
            markets = data if isinstance(data, list) else data.get('data', [])
            
            print(f"✅ Fetched {len(markets)} active markets\n")
            
            # Categorize markets by keywords
            categories = defaultdict(list)
            
            for market in markets:
                question = market.get('question', '')
                question_lower = question.lower()
                
                # Categorize
                if any(word in question_lower for word in ['trump', 'biden', 'president', 'election']):
                    categories['Politics'].append(question)
                elif any(word in question_lower for word in ['bitcoin', 'eth', 'crypto', 'btc', 'ethereum']):
                    categories['Crypto'].append(question)
                elif any(word in question_lower for word in ['fed', 'rate', 'inflation', 'recession', 'economy']):
                    categories['Economy'].append(question)
                elif any(word in question_lower for word in ['war', 'ukraine', 'russia', 'nato', 'military']):
                    categories['Geopolitics'].append(question)
                elif any(word in question_lower for word in ['ai', 'technology', 'tech', 'google', 'apple']):
                    categories['Technology'].append(question)
                elif any(word in question_lower for word in ['sport', 'nfl', 'nba', 'soccer', 'football']):
                    categories['Sports'].append(question)
                else:
                    categories['Other'].append(question)
            
            # Display by category
            for category, questions in sorted(categories.items()):
                if not questions:
                    continue
                    
                print(f"\n{'='*80}")
                print(f"📁 {category.upper()} ({len(questions)} markets)")
                print('='*80)
                
                for i, question in enumerate(questions[:15], 1):  # Show max 15 per category
                    print(f"{i:2d}. {question}")
                
                if len(questions) > 15:
                    print(f"    ... and {len(questions) - 15} more")
            
            # Show most popular/high volume markets
            print(f"\n\n{'='*80}")
            print("🔥 TOP 20 MARKETS (by API order - likely by volume)")
            print('='*80)
            
            for i, market in enumerate(markets[:20], 1):
                question = market.get('question', 'N/A')
                print(f"{i:2d}. {question}")
            
            # Suggest good test queries
            print(f"\n\n{'='*80}")
            print("💡 SUGGESTED TEST QUERIES FOR YOUR BOT")
            print('='*80)
            
            suggestions = [
                ("!market Trump", "Politics - High volume"),
                ("!market Bitcoin", "Crypto - Always popular"),
                ("!market Fed rate", "Economy - Fed-related markets"),
                ("!market Ukraine", "Geopolitics - War-related"),
                ("!market recession 2025", "Economy - Specific market"),
                ("!market Department Education", "Politics - Trump policy"),
                ("!market AI", "Technology - AI markets"),
                ("!market Tether", "Crypto - Stablecoin markets"),
            ]
            
            for query, description in suggestions:
                print(f"\n{query}")
                print(f"  → {description}")
            
            print(f"\n{'='*80}")
            print("NOTE: Markets you see on polymarket.com might not appear here")
            print("if they have low volume or are outside the top 500 markets.")
            print('='*80)


async def search_for_specific_keywords():
    """Search for markets containing specific keywords."""
    
    print("\n\n" + "="*80)
    print("🔍 KEYWORD SEARCH")
    print("="*80)
    
    keywords = ['trump', 'bitcoin', 'fed', 'ukraine', 'recession', 'ai', 'ethereum']
    
    url = "https://gamma-api.polymarket.com/markets"
    params = {'closed': 'false', 'limit': 500}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status != 200:
                return
            
            data = await response.json()
            markets = data if isinstance(data, list) else data.get('data', [])
            
            for keyword in keywords:
                matches = [m for m in markets if keyword.lower() in m.get('question', '').lower()]
                print(f"\n'{keyword}': {len(matches)} markets")
                for m in matches[:3]:
                    print(f"  - {m['question']}")


def main():
    print("\n🔍 Loading all available markets from Polymarket API...\n")
    asyncio.run(show_available_markets())
    asyncio.run(search_for_specific_keywords())
    print("\n✅ Complete! Use the suggestions above to test your bot.\n")


if __name__ == "__main__":
    main()