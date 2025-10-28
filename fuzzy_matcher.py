"""
Fuzzy string matching for Polymarket markets.
Uses multiple scoring strategies to improve match quality.
"""

from rapidfuzz import process, fuzz
from typing import List, Dict, Tuple


def find_matching_markets(query: str, markets: List[Dict]) -> List[Tuple[Dict, float]]:
    """
    Find markets matching the query using fuzzy string matching.
    
    Uses a combination of scorers to handle different query types:
    - token_set_ratio: Word order variations
    - token_sort_ratio: Alternative word ordering
    - partial_ratio: Substring/phrase matching
    
    Adaptive thresholds based on query length:
    - 1-2 words: threshold 50 (short queries need leniency)
    - 3-4 words: threshold 55 (moderate)
    - 5+ words: threshold 60 (standard precision)
    
    Args:
        query: User's search query string
        markets: List of market dictionaries from API
        
    Returns:
        List of tuples: (market_dict, similarity_score)
        Sorted by score descending, max 5 results
        
    Example:
        >>> markets = [{"question": "Will Bitcoin hit $200k?", ...}]
        >>> matches = find_matching_markets("Bitcoin 200k", markets)
        >>> [(market, score)] = matches
        >>> market["question"]
        'Will Bitcoin hit $200k?'
    """
    # Handle edge cases
    if not markets:
        return []
    
    if not query or not query.strip():
        return []
    
    # Create mapping of questions to market objects
    market_map = {market['question']: market for market in markets}
    questions = list(market_map.keys())
    
    # Normalize query (lowercase, strip extra whitespace)
    normalized_query = " ".join(query.lower().split())
    
    # Track results from multiple strategies
    results_map = {}
    
    # Strategy 1: token_set_ratio (handles word order)
    try:
        matches_token_set = process.extract(
            normalized_query,
            questions,
            scorer=fuzz.token_set_ratio,
            limit=10,
            score_cutoff=50  # Lower to catch more candidates
        )
        
        for question, score, _ in matches_token_set:
            if question not in results_map or score > results_map[question]:
                results_map[question] = score
    except Exception:
        pass  # Continue with other strategies if one fails
    
    # Strategy 2: token_sort_ratio (alternative word order)
    try:
        matches_token_sort = process.extract(
            normalized_query,
            questions,
            scorer=fuzz.token_sort_ratio,
            limit=10,
            score_cutoff=50
        )
        
        for question, score, _ in matches_token_sort:
            if question not in results_map or score > results_map[question]:
                results_map[question] = score
    except Exception:
        pass
    
    # Strategy 3: partial_ratio (substring matching)
    try:
        matches_partial = process.extract(
            normalized_query,
            questions,
            scorer=fuzz.partial_ratio,
            limit=10,
            score_cutoff=70  # Higher threshold for partial
        )
        
        for question, score, _ in matches_partial:
            if question in results_map:
                # Blend scores if found by multiple strategies
                results_map[question] = (results_map[question] * 0.6 + score * 0.4)
            elif score > 75:
                # Only add high-scoring partial-only matches
                results_map[question] = score * 0.9
    except Exception:
        pass
    
    # Determine threshold based on query length
    query_word_count = len(normalized_query.split())
    
    if query_word_count <= 2:
        final_threshold = 50
    elif query_word_count <= 4:
        final_threshold = 55
    else:
        final_threshold = 60
    
    # Filter and convert to list
    combined_matches = [
        (market_map[question], score)
        for question, score in results_map.items()
        if score >= final_threshold
    ]
    
    # Sort by score descending and return top 5
    combined_matches.sort(key=lambda x: x[1], reverse=True)
    return combined_matches[:5]