"""
Fuzzy string matching for finding relevant Polymarket markets.

This module uses RapidFuzz to perform fuzzy string matching between
user queries and market questions, allowing for typos and approximate matches.
"""

from rapidfuzz import process, fuzz
from typing import List, Dict, Tuple


def find_matching_markets(query: str, markets: List[Dict]) -> List[Tuple[Dict, float]]:
    """
    Find markets matching the query using fuzzy string matching.
    
    This function uses the token_set_ratio scorer from RapidFuzz, which:
    - Ignores word order differences
    - Handles case insensitivity
    - Works well with partial matches
    - Is robust to extra or missing words
    
    Args:
        query: User's search query string
        markets: List of market dictionaries from the API
        
    Returns:
        List of tuples containing (market_object, similarity_score)
        Sorted by score in descending order (best matches first)
        Only includes matches with score >= 60
        Limited to top 5 matches
        
    Example:
        >>> markets = [{"question": "Will Bitcoin hit $200k by 2027?", ...}, ...]
        >>> matches = find_matching_markets("bitcoin 200k", markets)
        >>> for market, score in matches:
        ...     print(f"{market['question']}: {score}%")
    """
    # Handle edge cases
    if not markets:
        return []
    
    if not query or not query.strip():
        return []
    
    # Create mapping of questions to market objects
    # This allows us to easily retrieve the full market object after matching
    market_map = {market['question']: market for market in markets}
    
    # Extract all market questions for matching
    market_questions = list(market_map.keys())
    
    # Perform fuzzy matching
    # token_set_ratio: Best for queries where word order doesn't matter
    # limit=5: Return at most 5 matches
    # score_cutoff=60: Only return matches with 60% or higher similarity
    matches = process.extract(
        query,
        market_questions,
        scorer=fuzz.token_set_ratio,
        limit=5,
        score_cutoff=60
    )
    
    # Convert results to list of (market_object, score) tuples
    # matches format: [(question, score, index), ...]
    result = [(market_map[question], score) for question, score, _ in matches]
    
    return result


def get_match_quality(score: float) -> str:
    """
    Classify match quality based on similarity score.
    
    Args:
        score: Similarity score from 0-100
        
    Returns:
        String describing match quality: "excellent", "good", "fair", or "poor"
    """
    if score >= 90:
        return "excellent"
    elif score >= 80:
        return "good"
    elif score >= 70:
        return "fair"
    else:
        return "poor"


def should_show_single_market(matches: List[Tuple[Dict, float]]) -> bool:
    """
    Determine if we should show a single market or multiple matches.
    
    Args:
        matches: List of (market, score) tuples
        
    Returns:
        True if we should show single market detail view, False for list view
    """
    if not matches:
        return False
    
    # Show single market if:
    # 1. Only one match found, OR
    # 2. Top match has very high confidence (>85)
    return len(matches) == 1 or matches[0][1] > 85
