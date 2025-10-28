"""
Comprehensive test suite for Polymarket Discord Bot
Tests all core modules: API client, fuzzy matcher, embed builder, and bot connection
"""

# IMPORTANT: Some tests are currently failing. 

import asyncio
import time
from typing import List, Dict
import sys

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(test_name: str, passed: bool, details: str = ""):
    """Print formatted test result"""
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"{status} | {test_name}")
    if details:
        print(f"      {details}")

def print_section(section_name: str):
    """Print test section header"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{section_name}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

# =============================================================================
# TEST 1: API CLIENT TESTS
# =============================================================================

async def test_api_client():
    """Test Polymarket API client functionality"""
    print_section("TEST 1: API CLIENT")
    
    try:
        from api_client import PolymarketClient
        print_test("Import api_client", True)
    except ImportError as e:
        print_test("Import api_client", False, f"Import failed: {e}")
        return
    
    # Test 1.1: Client initialization
    try:
        client = PolymarketClient()
        print_test("Client initialization", True)
    except Exception as e:
        print_test("Client initialization", False, f"Error: {e}")
        return
    
    # Test 1.2: API connection and data retrieval
    try:
        markets = await client.get_markets()
        is_list = isinstance(markets, list)
        has_data = len(markets) > 0
        print_test("API data retrieval", is_list and has_data, 
                  f"Retrieved {len(markets)} markets" if has_data else "No markets returned")
    except Exception as e:
        print_test("API data retrieval", False, f"Error: {e}")
        return
    
    # Test 1.3: Market data structure validation
    if markets:
        market = markets[0]
        required_fields = ['question', 'slug', 'outcomePrices', 'volume', 'endDate']
        missing_fields = [field for field in required_fields if field not in market]
        
        print_test("Market data structure", len(missing_fields) == 0,
                  f"Missing fields: {missing_fields}" if missing_fields else "All required fields present")
        
        # Test 1.4: Data type validation
        try:
            question_valid = isinstance(market.get('question'), str)
            slug_valid = isinstance(market.get('slug'), str)
            prices_valid = isinstance(market.get('outcomePrices'), list)
            volume_valid = market.get('volume') is not None
            
            all_valid = question_valid and slug_valid and prices_valid and volume_valid
            print_test("Market field types", all_valid,
                      "All field types correct" if all_valid else "Some field types incorrect")
        except Exception as e:
            print_test("Market field types", False, f"Validation error: {e}")
    
    # Test 1.5: Cache functionality
    try:
        start_time = time.time()
        markets_cached = await client.get_markets()
        cached_time = time.time() - start_time
        
        # Cached response should be much faster (< 0.01 seconds)
        is_cached = cached_time < 0.1
        print_test("Cache functionality", is_cached,
                  f"Cached response time: {cached_time*1000:.2f}ms")
    except Exception as e:
        print_test("Cache functionality", False, f"Error: {e}")
    
    # Test 1.6: Error handling (timeout test)
    try:
        # This tests that the client has timeout configuration
        has_timeout = hasattr(client, 'timeout') and client.timeout > 0
        print_test("Timeout configuration", has_timeout,
                  f"Timeout: {client.timeout}s" if has_timeout else "No timeout set")
    except Exception as e:
        print_test("Timeout configuration", False, f"Error: {e}")
    
    return markets

# =============================================================================
# TEST 2: FUZZY MATCHER TESTS
# =============================================================================

def test_fuzzy_matcher(markets: List[Dict]):
    """Test fuzzy matching functionality"""
    print_section("TEST 2: FUZZY MATCHER")
    
    if not markets:
        print_test("Fuzzy matcher tests", False, "No markets data available")
        return
    
    try:
        from fuzzy_matcher import find_matching_markets
        print_test("Import fuzzy_matcher", True)
    except ImportError as e:
        print_test("Import fuzzy_matcher", False, f"Import failed: {e}")
        return
    
    # Test 2.1: Exact match scenario
    if markets:
        exact_query = markets[0]['question'][:50]  # Use part of actual market question
        matches = find_matching_markets(exact_query, markets)
        
        has_matches = len(matches) > 0
        high_score = matches[0][1] > 80 if has_matches else False
        
        print_test("Exact match scenario", has_matches and high_score,
                  f"Top score: {matches[0][1]:.1f}%" if has_matches else "No matches found")
    
    # Test 2.2: Partial match with typos
    test_queries = [
        ("Bitcoin 200k", "Cryptocurrency market"),
        ("Trump election", "Political market"),
        ("Ethereum price", "Cryptocurrency market"),
    ]
    
    for query, description in test_queries:
        matches = find_matching_markets(query, markets)
        has_results = len(matches) > 0
        print_test(f"Partial match: '{query}'", has_results,
                  f"Found {len(matches)} matches" if has_results else "No matches")
    
    # Test 2.3: No match scenario
    impossible_query = "xyzabc123impossible456"
    matches = find_matching_markets(impossible_query, markets)
    no_matches = len(matches) == 0
    print_test("No match scenario", no_matches,
              "Correctly returned no matches" if no_matches else f"Unexpectedly found {len(matches)} matches")
    
    # Test 2.4: Score threshold validation
    common_query = "market"
    matches = find_matching_markets(common_query, markets)
    
    if matches:
        all_above_threshold = all(score >= 60 for _, score in matches)
        sorted_correctly = all(matches[i][1] >= matches[i+1][1] for i in range(len(matches)-1))
        
        print_test("Score threshold (≥60)", all_above_threshold,
                  f"Scores: {[f'{s:.1f}' for _, s in matches]}")
        print_test("Results sorted by score", sorted_correctly,
                  "Highest to lowest" if sorted_correctly else "Sorting incorrect")
    
    # Test 2.5: Limit validation (max 5 results)
    broad_query = "will"
    matches = find_matching_markets(broad_query, markets)
    within_limit = len(matches) <= 5
    print_test("Result limit (max 5)", within_limit,
              f"Returned {len(matches)} matches")
    
    # Test 2.6: Case insensitivity
    if markets:
        test_query = "BITCOIN"
        matches = find_matching_markets(test_query, markets)
        case_insensitive = len(matches) > 0
        print_test("Case insensitivity", case_insensitive,
                  f"Found {len(matches)} matches with uppercase query")
    
    return matches if 'matches' in locals() else []

# =============================================================================
# TEST 3: EMBED BUILDER TESTS
# =============================================================================

def test_embed_builder(markets: List[Dict], matches: List[tuple]):
    """Test Discord embed builder functionality"""
    print_section("TEST 3: EMBED BUILDER")
    
    if not markets:
        print_test("Embed builder tests", False, "No markets data available")
        return
    
    try:
        from embed_builder import (
            build_single_market_embed,
            build_multiple_matches_embed,
            build_no_matches_embed
        )
        print_test("Import embed_builder", True)
    except ImportError as e:
        print_test("Import embed_builder", False, f"Import failed: {e}")
        return
    
    # Test 3.1: Single market embed
    try:
        market = markets[0]
        embed = build_single_market_embed(market)
        
        # Validate embed structure
        has_title = hasattr(embed, 'title') and embed.title
        has_url = hasattr(embed, 'url') and 'polymarket.com' in (embed.url or '')
        has_color = hasattr(embed, 'color') and embed.color
        has_fields = hasattr(embed, 'fields') and len(embed.fields) >= 3
        
        all_valid = has_title and has_url and has_color and has_fields
        print_test("Single market embed structure", all_valid,
                  f"Fields: {len(embed.fields) if has_fields else 0}")
        
        # Check for required field names
        if has_fields:
            field_names = [field.name for field in embed.fields]
            has_odds = any('Odds' in name or '📊' in name for name in field_names)
            has_volume = any('Volume' in name or '💰' in name for name in field_names)
            has_date = any('Close' in name or '📅' in name for name in field_names)
            
            required_fields_present = has_odds and has_volume and has_date
            print_test("Single market required fields", required_fields_present,
                      "Odds, Volume, and Close date present" if required_fields_present else "Missing required fields")
        
    except Exception as e:
        print_test("Single market embed", False, f"Error: {e}")
    
    # Test 3.2: Multiple matches embed
    try:
        if matches and len(matches) > 1:
            embed = build_multiple_matches_embed("test query", matches[:3])
            
            has_title = hasattr(embed, 'title') and '📍' in embed.title
            has_fields = hasattr(embed, 'fields') and len(embed.fields) > 0
            has_footer = hasattr(embed, 'footer') and embed.footer
            
            all_valid = has_title and has_fields and has_footer
            print_test("Multiple matches embed", all_valid,
                      f"Contains {len(embed.fields)} match fields" if has_fields else "")
        else:
            print_test("Multiple matches embed", False, "Insufficient match data for test")
    except Exception as e:
        print_test("Multiple matches embed", False, f"Error: {e}")
    
    # Test 3.3: No matches embed
    try:
        embed = build_no_matches_embed("impossible search query")
        
        has_title = hasattr(embed, 'title') and '❌' in embed.title
        has_description = hasattr(embed, 'description') and embed.description
        has_red_color = hasattr(embed, 'color') and embed.color == 0xEF4444
        
        all_valid = has_title and has_description and has_red_color
        print_test("No matches embed", all_valid,
                  "Red color, error title, and description present" if all_valid else "Missing elements")
    except Exception as e:
        print_test("No matches embed", False, f"Error: {e}")
    
    # Test 3.4: Data formatting
    try:
        market = markets[0]
        embed = build_single_market_embed(market)
        
        # Check if percentages are formatted correctly (should be between 0-100)
        field_values = [field.value for field in embed.fields]
        odds_field = next((val for val in field_values if '%' in val), None)
        
        if odds_field:
            # Extract percentage values
            import re
            percentages = re.findall(r'(\d+\.?\d*)%', odds_field)
            valid_percentages = all(0 <= float(p) <= 100 for p in percentages)
            
            print_test("Percentage formatting", valid_percentages,
                      f"Values: {percentages}" if percentages else "No percentages found")
    except Exception as e:
        print_test("Percentage formatting", False, f"Error: {e}")

# =============================================================================
# TEST 4: BOT CONNECTION TEST
# =============================================================================

def test_bot_structure():
    """Test bot structure and configuration"""
    print_section("TEST 4: BOT STRUCTURE")
    
    try:
        import bot
        print_test("Import bot.py", True)
    except ImportError as e:
        print_test("Import bot.py", False, f"Import failed: {e}")
        return
    
    # Test 4.1: Bot instance exists
    try:
        has_bot = hasattr(bot, 'bot')
        print_test("Bot instance exists", has_bot)
    except Exception as e:
        print_test("Bot instance exists", False, f"Error: {e}")
        return
    
    # Test 4.2: Intents configuration
    try:
        bot_instance = bot.bot
        has_intents = hasattr(bot_instance, 'intents')
        message_content = bot_instance.intents.message_content if has_intents else False
        
        print_test("Message content intent", message_content,
                  "Required for prefix commands")
    except Exception as e:
        print_test("Message content intent", False, f"Error: {e}")
    
    # Test 4.3: Command registration
    try:
        commands = bot_instance.all_commands
        has_market_cmd = 'market' in commands
        
        print_test("Market command registered", has_market_cmd)
        
        if has_market_cmd:
            market_cmd = commands['market']
            is_hybrid = hasattr(market_cmd, 'app_command')
            print_test("Hybrid command setup", is_hybrid,
                      "Supports both prefix and slash commands" if is_hybrid else "Only prefix command")
    except Exception as e:
        print_test("Command registration", False, f"Error: {e}")
    
    # Test 4.4: Cooldown configuration
    try:
        if has_market_cmd:
            has_cooldown = hasattr(market_cmd, '_buckets')
            print_test("Cooldown configured", has_cooldown,
                      "Prevents spam" if has_cooldown else "No cooldown set")
    except Exception as e:
        print_test("Cooldown configured", False, f"Error: {e}")

# =============================================================================
# TEST 5: INTEGRATION TESTS
# =============================================================================

async def test_integration(markets: List[Dict]):
    """Test integration between modules"""
    print_section("TEST 5: INTEGRATION TESTS")
    
    if not markets:
        print_test("Integration tests", False, "No markets data available")
        return
    
    # Test 5.1: Full command flow simulation
    try:
        from fuzzy_matcher import find_matching_markets
        from embed_builder import build_single_market_embed, build_multiple_matches_embed
        
        # Simulate user query
        test_query = "Bitcoin"
        matches = find_matching_markets(test_query, markets)
        
        # Determine which embed to use
        if matches and matches[0][1] > 85:
            embed = build_single_market_embed(matches[0][0])
            embed_type = "single"
        elif len(matches) >= 2:
            embed = build_multiple_matches_embed(test_query, matches)
            embed_type = "multiple"
        else:
            from embed_builder import build_no_matches_embed
            embed = build_no_matches_embed(test_query)
            embed_type = "no_matches"
        
        print_test("Full command flow", True,
                  f"Query '{test_query}' → {len(matches)} matches → {embed_type} embed")
        
    except Exception as e:
        print_test("Full command flow", False, f"Error: {e}")
    
    # Test 5.2: Performance test
    try:
        start_time = time.time()
        
        # Simulate full flow
        from api_client import PolymarketClient
        from fuzzy_matcher import find_matching_markets
        
        client = PolymarketClient()
        markets_perf = await client.get_markets()  # Should use cache
        matches = find_matching_markets("test", markets_perf)
        
        elapsed = time.time() - start_time
        fast_enough = elapsed < 0.5  # Should be under 500ms with cache
        
        print_test("Performance (cached)", fast_enough,
                  f"Response time: {elapsed*1000:.0f}ms")
        
    except Exception as e:
        print_test("Performance test", False, f"Error: {e}")

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

async def run_all_tests():
    """Run complete test suite"""
    print(f"\n{Colors.YELLOW}{'='*60}{Colors.RESET}")
    print(f"{Colors.YELLOW}POLYMARKET DISCORD BOT - TEST SUITE{Colors.RESET}")
    print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")
    
    # Test 1: API Client
    markets = await test_api_client()
    
    # Test 2: Fuzzy Matcher
    matches = []
    if markets:
        matches = test_fuzzy_matcher(markets)
    
    # Test 3: Embed Builder
    if markets:
        test_embed_builder(markets, matches)
    
    # Test 4: Bot Structure
    test_bot_structure()
    
    # Test 5: Integration
    if markets:
        await test_integration(markets)
    
    # Summary
    print(f"\n{Colors.YELLOW}{'='*60}{Colors.RESET}")
    print(f"{Colors.YELLOW}TEST SUITE COMPLETE{Colors.RESET}")
    print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}\n")
    
    print(f"{Colors.BLUE}Next Steps:{Colors.RESET}")
    print("1. Review any failed tests above")
    print("2. Fix issues in the corresponding module")
    print("3. Run tests again to verify fixes")
    print("4. Test bot manually in Discord server")
    print(f"\n{Colors.GREEN}Manual Testing Checklist:{Colors.RESET}")
    print("  [ ] Bot connects to Discord")
    print("  [ ] !market command responds")
    print("  [ ] /market slash command responds")
    print("  [ ] Embeds display correctly")
    print("  [ ] Links are clickable")
    print("  [ ] Cooldown prevents spam")
    print("  [ ] Error messages are helpful\n")

if __name__ == "__main__":
    # Run the test suite
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error running tests: {e}{Colors.RESET}")
        sys.exit(1)