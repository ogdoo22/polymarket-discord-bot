"""
Fuzzy string matching for finding relevant Polymarket markets.

This module uses RapidFuzz to perform fuzzy string matching between
user queries and market questions, allowing for typos and approximate matches.
"""

from rapidfuzz import process, fuzz
from typing import List, Dict, Tuple
import re


def find_matching_markets(query: str, markets: List[Dict]) -> List[Tuple[Dict, float]]:
    """Find markets matching the query using fuzzy string matching."""
    
    if not markets:
        return []
    
    if not query or not query.strip():
        return []
    
    # Extract years from query
    query_years = extract_year(query.lower())
    
    # Create mapping of questions to market objects
    market_map = {market['question']: market for market in markets}
    market_questions = list(market_map.keys())
    
    # Use different threshold for short vs long queries
    query_words = len(query.split())
    if query_words <= 2:
        scorer = fuzz.partial_ratio
        cutoff = 70
    else:
        scorer = fuzz.token_set_ratio
        cutoff = 45
    
    # Perform fuzzy matching
    matches = process.extract(
        query,
        market_questions,
        scorer=scorer,
        limit=10,  # Get more candidates
        score_cutoff=cutoff
    )
    
    # Adjust scores based on year matching
    adjusted_matches = []
    for question, score, _ in matches:
        market = market_map[question]
        question_years = extract_year(question.lower())
        
        # If query has a year and market has a different year, penalize
        if query_years and question_years and not query_years.intersection(question_years):
            score = score * 0.6  # Reduce score by 40%
        
        adjusted_matches.append((market, score))
    
    # Re-sort by adjusted score and filter
    adjusted_matches.sort(key=lambda x: x[1], reverse=True)
    
    # Filter out scores below cutoff after adjustment
    adjusted_matches = [(m, s) for m, s in adjusted_matches if s >= cutoff]
    
    # Return top 5
    return adjusted_matches[:5]


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

def extract_year(text: str) -> set:
    """Extract years from text (e.g., 2025, 2027)."""
    return set(re.findall(r'\b(20\d{2})\b', text))