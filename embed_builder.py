"""
Discord embed builders for displaying Polymarket market data.

This module contains functions to create beautifully formatted Discord embeds
for different scenarios: single market details, multiple matches, and no results.
"""

import discord
import json
from datetime import datetime
from typing import Dict, List, Tuple


def build_single_market_embed(market: Dict) -> discord.Embed:
    """Build detailed embed for a single market."""
    yes_price, no_price = parse_outcome_prices(market)
    
    if yes_price is not None and no_price is not None:
        odds_text = f"**Yes**: {yes_price:.1f}%\n**No**: {no_price:.1f}%"
    else:
        odds_text = "Odds unavailable"

    # Parse outcome prices (they're stored as JSON strings)
    try:
        if isinstance(market.get('outcomePrices'), str):
            prices = json.loads(market['outcomePrices'])
        else:
            prices = market.get('outcomePrices', [])
        
        if len(prices) >= 2:
            yes_price = float(prices[0]) * 100
            no_price = float(prices[1]) * 100
            odds_text = f"**Yes**: {yes_price:.1f}%\n**No**: {no_price:.1f}%"
        else:
            odds_text = "Odds unavailable"
    except (json.JSONDecodeError, ValueError, IndexError):
        odds_text = "Odds unavailable"
    
    # Create embed
    embed = discord.Embed(
        title=market.get('question', 'Unknown Market'),
        description=market.get('description', '')[:200] + "..." if len(market.get('description', '')) > 200 else market.get('description', ''),
        url=f"https://polymarket.com/market/{market.get('slug', '')}",
        color=0x7C3AED
    )
    
    # Add odds field
    embed.add_field(
        name="📊 Current Odds",
        value=odds_text,
        inline=True
    )
    
    # Add volume field
    try:
        volume = float(market.get('volume', 0))
        embed.add_field(
            name="💰 Volume",
            value=f"${volume:,.0f}",
            inline=True
        )
    except (ValueError, TypeError):
        embed.add_field(
            name="💰 Volume",
            value="N/A",
            inline=True
        )
    
    # Add close date field
    try:
        end_date = datetime.fromisoformat(market.get('endDate', '').replace('Z', '+00:00'))
        date_str = end_date.strftime('%b %d, %Y at %I:%M %p ET')
        embed.add_field(
            name="📅 Closes",
            value=date_str,
            inline=True
        )
    except (ValueError, AttributeError):
        embed.add_field(
            name="📅 Closes",
            value="Date unavailable",
            inline=True
        )
    
    embed.set_footer(text="Data from Polymarket")
    embed.timestamp = datetime.utcnow()
    
    return embed


def build_multiple_matches_embed(query: str, matches: List[Tuple[Dict, float]]) -> discord.Embed:
    """Build embed showing multiple market matches."""
    
    embed = discord.Embed(
        title=f"🔍 Found {len(matches)} markets matching '{query}'",
        description="Here are the closest matches:",
        color=0x7C3AED
    )
    
    for i, (market, score) in enumerate(matches, 1):
        # Parse outcome prices
        try:
            if isinstance(market.get('outcomePrices'), str):
                prices = json.loads(market['outcomePrices'])
            else:
                prices = market.get('outcomePrices', [])
            
            if len(prices) >= 2:
                yes_price = float(prices[0]) * 100
                no_price = float(prices[1]) * 100
                odds_text = f"**Yes**: {yes_price:.1f}% | **No**: {no_price:.1f}%"
            else:
                odds_text = "Odds unavailable"
        except (json.JSONDecodeError, ValueError, IndexError):
            odds_text = "Odds unavailable"
        
        # Truncate long questions
        question = market.get('question', 'Unknown')
        if len(question) > 100:
            question = question[:97] + "..."
        
        embed.add_field(
            name=f"{i}. {question}",
            value=f"{odds_text} | Match: {score:.0f}%",
            inline=False
        )
    
    embed.set_footer(text="Data from Polymarket • Use the command with a more specific query for details")
    
    return embed


def build_no_matches_embed(query: str) -> discord.Embed:
    """
    Build an embed for when no markets match the query.
    
    Args:
        query: Original search query that had no matches
        
    Returns:
        Discord embed with helpful suggestions
    """
    embed = discord.Embed(
        title="❌ No Markets Found",
        description=f"No active markets found matching **'{query}'**",
        color=0xEF4444,  # Red color
        timestamp=datetime.utcnow()
    )
    
    # Add suggestions field
    suggestions = (
        "• Try different keywords\n"
        "• Check for typos in your query\n"
        "• Use broader search terms\n"
        "• Browse active markets at [Polymarket](https://polymarket.com)"
    )
    
    embed.add_field(
        name="💡 Suggestions",
        value=suggestions,
        inline=False
    )
    
    # Footer with tip
    embed.set_footer(text="Tip: Markets must be actively trading to appear in search")
    
    return embed


def format_date(iso_date_string: str) -> str:
    """
    Format an ISO date string into a readable format.
    
    Args:
        iso_date_string: ISO 8601 date string (e.g., "2027-12-31T23:59:59Z")
        
    Returns:
        Formatted date string (e.g., "Dec 31, 2027 at 11:59 PM")
    """
    try:
        # Parse ISO date
        dt = datetime.fromisoformat(iso_date_string.replace('Z', '+00:00'))
        
        # Format as readable string
        return dt.strftime("%b %d, %Y at %I:%M %p UTC")
    except (ValueError, AttributeError):
        # Return original string if parsing fails
        return iso_date_string


def format_currency(amount: float) -> str:
    """
    Format a number as currency with thousands separators.
    
    Args:
        amount: Numeric amount to format
        
    Returns:
        Formatted currency string (e.g., "$1,250,000")
    """
    return f"${amount:,.0f}"


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: String to append when truncating (default: "...")
        
    Returns:
        Truncated text with suffix if needed
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def parse_outcome_prices(market: Dict) -> tuple:
    """
    Parse outcome prices from various possible formats.
    
    Returns:
        (yes_price, no_price) as floats, or (None, None) if unavailable
    """
    prices_field = market.get('outcomePrices')
    
    if not prices_field:
        return None, None
    
    try:
        # Case 1: It's a JSON string like "[\"0.18\", \"0.82\"]"
        if isinstance(prices_field, str):
            prices = json.loads(prices_field)
        # Case 2: It's already a list
        elif isinstance(prices_field, list):
            prices = prices_field
        else:
            return None, None
        
        # Extract yes/no prices
        if len(prices) >= 2:
            yes_price = float(prices[0]) * 100
            no_price = float(prices[1]) * 100
            return yes_price, no_price
        
    except (json.JSONDecodeError, ValueError, IndexError, TypeError):
        pass
    
    return None, None
