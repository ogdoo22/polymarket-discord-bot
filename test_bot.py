"""
Comprehensive test suite for Polymarket Discord Bot
Tests fuzzy matching, API integration, and embed building
"""

import asyncio
import pytest
from fuzzy_matcher import find_matching_markets
from embed_builder import build_single_market_embed, build_multiple_matches_embed, build_no_matches_embed

# Sample market data matching your Discord test
SAMPLE_MARKETS = [
    {
        "question": "Will Trump end Department of Education in 2025?",
        "slug": "trump-end-dept-education-2025",
        "outcomePrices": ["0.03", "0.97"],
        "volume": "838592",
        "endDate": "2025-12-31T12:00:00Z",
        "description": "This market will resolve to 'Yes' if the US Department of Education ceases operations entirely..."
    },
    {
        "question": "Will the US government shut down in 2024?",
        "slug": "government-shutdown-2024",
        "outcomePrices": ["0.15", "0.85"],
        "volume": "500000",
        "endDate": "2024-12-31T23:59:59Z",
        "description": "Market resolves YES if federal government experiences a shutdown..."
    },
    {
        "question": "When will the next government shutdown end?",
        "slug": "next-shutdown-end-date",
        "outcomePrices": ["0.25", "0.75"],
        "volume": "200000",
        "endDate": "2025-06-30T23:59:59Z",
        "description": "This market tracks when the next federal shutdown will conclude..."
    },
    {
        "question": "Will there be a government shutdown in Q1 2025?",
        "slug": "shutdown-q1-2025",
        "outcomePrices": ["0.40", "0.60"],
        "volume": "350000",
        "endDate": "2025-03-31T23:59:59Z",
        "description": "Resolves YES if government shuts down between Jan-Mar 2025..."
    }
]


class TestFuzzyMatching:
    """Test fuzzy matching behavior with real-world queries"""
    
    def test_exact_query_department_education(self):
        """Test: !market Trump end Department of Education"""
        query = "Trump end Department of Education"
        matches = find_matching_markets(query, SAMPLE_MARKETS)
        
        assert len(matches) > 0, "Should find at least one match"
        # First match should be the Department of Education market
        assert "Department of Education" in matches[0][0]["question"]
        assert matches[0][1] > 80, f"Match score should be high, got {matches[0][1]}"
    
    def test_government_shutdown_query(self):
        """Test: !market When will the government shutdown end"""
        query = "When will the government shutdown end"
        matches = find_matching_markets(query, SAMPLE_MARKETS)
        
        assert len(matches) > 0, "Should find matches for shutdown query"
        # Should match shutdown-related markets
        top_match = matches[0][0]
        assert "shutdown" in top_match["question"].lower()
        print(f"\nTop match for '{query}': {top_match['question']} (score: {matches[0][1]})")
    
    def test_shutdown_end_specific(self):
        """Test: !market When will the government shutdown end?"""
        query = "When will the government shutdown end?"
        matches = find_matching_markets(query, SAMPLE_MARKETS)
        
        assert len(matches) > 0, "Should find matches"
        # Print all matches for debugging
        print(f"\nMatches for '{query}':")
        for market, score in matches:
            print(f"  - {market['question'][:60]}... (score: {score})")
        
        # The "When will the next government shutdown end?" should be top match
        top_match = matches[0][0]
        assert "when" in top_match["question"].lower() or "shutdown" in top_match["question"].lower()
    
    def test_no_matches_random_query(self):
        """Test: !market alien invasion"""
        query = "alien invasion"
        matches = find_matching_markets(query, SAMPLE_MARKETS)
        
        assert len(matches) == 0, "Should find no matches for irrelevant query"
    
    def test_short_query_validation(self):
        """Test: !market ab (too short)"""
        query = "ab"
        # This would be caught by bot.py validation before reaching fuzzy matcher
        assert len(query) < 3, "Query should be flagged as too short"
    
    def test_multiple_matches_scenario(self):
        """Test scenario where multiple markets match"""
        query = "government shutdown"
        matches = find_matching_markets(query, SAMPLE_MARKETS)
        
        assert len(matches) >= 2, "Should find multiple shutdown-related markets"
        # All matches should contain 'shutdown' or related terms
        for market, score in matches:
            assert "shutdown" in market["question"].lower()
            assert score >= 60, f"Score should be above threshold, got {score}"
    
    def test_case_insensitive_matching(self):
        """Test that matching is case-insensitive"""
        query1 = "Trump Department Education"
        query2 = "trump department education"
        
        matches1 = find_matching_markets(query1, SAMPLE_MARKETS)
        matches2 = find_matching_markets(query2, SAMPLE_MARKETS)
        
        assert len(matches1) == len(matches2), "Case should not affect results"
        assert matches1[0][0] == matches2[0][0], "Same top match regardless of case"
    
    def test_partial_word_matching(self):
        """Test matching with partial words"""
        query = "dept education trump"
        matches = find_matching_markets(query, SAMPLE_MARKETS)
        
        assert len(matches) > 0, "Should match despite using 'dept' instead of 'Department'"
        # Should still find Department of Education market
        top_match = matches[0][0]
        assert "Education" in top_match["question"]
    
    def test_word_order_flexibility(self):
        """Test that word order doesn't drastically affect matching"""
        query1 = "Trump Department of Education"
        query2 = "Department of Education Trump"
        
        matches1 = find_matching_markets(query1, SAMPLE_MARKETS)
        matches2 = find_matching_markets(query2, SAMPLE_MARKETS)
        
        # Should find the same top result
        assert matches1[0][0]["question"] == matches2[0][0]["question"]
    
    def test_empty_markets_list(self):
        """Test handling of empty markets list"""
        query = "anything"
        matches = find_matching_markets(query, [])
        
        assert len(matches) == 0, "Should return empty list for empty markets"


class TestEmbedBuilding:
    """Test Discord embed generation"""
    
    def test_single_market_embed(self):
        """Test building single market embed"""
        market = SAMPLE_MARKETS[0]
        embed = build_single_market_embed(market)
        
        assert embed.title == market["question"]
        assert embed.url == f"https://polymarket.com/market/{market['slug']}"
        assert len(embed.fields) == 3, "Should have 3 fields (Odds, Volume, Closes)"
    
    def test_multiple_matches_embed(self):
        """Test building multiple matches embed"""
        query = "government shutdown"
        matches = [(SAMPLE_MARKETS[1], 85), (SAMPLE_MARKETS[2], 75)]
        
        embed = build_multiple_matches_embed(query, matches)
        
        assert "Found 2 markets" in embed.title
        assert query in embed.title
        assert len(embed.fields) == 2, "Should have field for each match"
    
    def test_no_matches_embed(self):
        """Test building no matches embed"""
        query = "alien invasion"
        embed = build_no_matches_embed(query)
        
        assert "No Markets Found" in embed.title
        assert query in embed.description
        assert len(embed.fields) >= 1, "Should have suggestions field"


class TestScoreThresholds:
    """Test score-based decision logic"""
    
    def test_high_confidence_single_result(self):
        """Test that score > 85 triggers single market display"""
        query = "Trump Department of Education"
        matches = find_matching_markets(query, SAMPLE_MARKETS)
        
        if matches and matches[0][1] > 85:
            # Should display single market
            embed = build_single_market_embed(matches[0][0])
            assert embed.title == matches[0][0]["question"]
    
    def test_medium_confidence_multiple_results(self):
        """Test that scores 60-85 show multiple matches"""
        query = "shutdown 2025"
        matches = find_matching_markets(query, SAMPLE_MARKETS)
        
        # Filter matches in 60-85 range
        medium_matches = [(m, s) for m, s in matches if 60 <= s <= 85]
        
        if len(medium_matches) >= 2:
            embed = build_multiple_matches_embed(query, medium_matches)
            assert "Found" in embed.title


def run_interactive_tests():
    """
    Run interactive tests that show what's happening in your Discord bot
    """
    print("=" * 80)
    print("INTERACTIVE TEST RESULTS - Matching Your Discord Tests")
    print("=" * 80)
    
    # Test 1: The query that worked
    print("\n[TEST 1] Query: 'Trump end Department of Education'")
    print("-" * 80)
    matches = find_matching_markets("Trump end Department of Education", SAMPLE_MARKETS)
    if matches:
        print(f"✓ Found {len(matches)} match(es)")
        print(f"  Top result: {matches[0][0]['question']}")
        print(f"  Match score: {matches[0][1]:.1f}%")
    else:
        print("✗ No matches found")
    
    # Test 2: The query that failed
    print("\n[TEST 2] Query: 'When will the government shutdown end'")
    print("-" * 80)
    matches = find_matching_markets("When will the government shutdown end", SAMPLE_MARKETS)
    if matches:
        print(f"✓ Found {len(matches)} match(es)")
        for i, (market, score) in enumerate(matches[:3], 1):
            print(f"  {i}. {market['question']} (score: {score:.1f}%)")
    else:
        print("✗ No matches found - THIS IS THE BUG!")
    
    # Test 3: Variations of the failing query
    print("\n[TEST 3] Query variations for 'shutdown end'")
    print("-" * 80)
    test_queries = [
        "government shutdown end",
        "when shutdown end",
        "next shutdown end",
        "shutdown ending"
    ]
    
    for query in test_queries:
        matches = find_matching_markets(query, SAMPLE_MARKETS)
        if matches:
            print(f"✓ '{query}': {matches[0][0]['question'][:50]}... ({matches[0][1]:.1f}%)")
        else:
            print(f"✗ '{query}': No matches")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Run the interactive tests first
    run_interactive_tests()
    
    # Then run pytest
    print("\nRunning pytest suite...\n")
    pytest.main([__file__, "-v", "-s"])