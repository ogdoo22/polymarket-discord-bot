"""
Discord embed builders for displaying Polymarket market data.

This module contains functions to create beautifully formatted Discord embeds
for different scenarios: single market details, multiple matches, and no results.
"""

import discord
from datetime import datetime
from typing import Dict, List, Tuple


def build_single_market_embed(market: Dict) -> discord.Embed:
    """
    Build a detailed embed for a single market.
    
    Args:
        market: Market dictionary from API
        
    Returns:
        Discord embed with market details
    """
    # Create embed with market question as title
    embed = discord.Embed(
        title=market['question'],
        url=f"https://polymarket.com/market/{market['slug']}",
        color=0x7C3AED,  # Purple brand color
        timestamp=datetime.utcnow()
    )
    
    # Add description (truncate if too long)
    if 'description' in market and market['description']:
        description = market['description']
        if len(description) > 200:
            description = description[:197] + "..."
        embed.description = description
    
    # Current odds field
    yes_price = float(market['outcomePrices'][0]) * 100
    no_price = float(market['outcomePrices'][1]) * 100
    embed.add_field(
        name="📊 Current Odds",
        value=f"**Yes**: {yes_price:.1f}%\n**No**: {no_price:.1f}%",
        inline=True
    )
    
    # Volume field
    try:
        volume = float(market['volume'])
        embed.add_field(
            name="💰 Volume",
            value=f"${volume:,.0f}",
            inline=True
        )
    except (ValueError, KeyError):
        embed.add_field(
            name="💰 Volume",
            value="N/A",
            inline=True
        )
    
    # Close date field
    try:
        close_date = format_date(market['endDate'])
        embed.add_field(
            name="📅 Closes",
            value=close_date,
            inline=True
        )
    except (ValueError, KeyError):
        embed.add_field(
            name="📅 Closes",
            value="N/A",
            inline=True
        )
    
    # Footer
    embed.set_footer(text="Data from Polymarket")
    
    return embed


def build_multiple_matches_embed(query: str, matches: List[Tuple[Dict, float]]) -> discord.Embed:
    """
    Build an embed showing multiple matching markets.
    
    Args:
        query: Original search query
        matches: List of (market, score) tuples
        
    Returns:
        Discord embed with multiple market options
    """
    # Create embed
    embed = discord.Embed(
        title=f"🔍 Found {len(matches)} markets matching '{query}'",
        description="Here are the closest matches:",
        color=0x7C3AED,
        timestamp=datetime.utcnow()
    )
    
    # Add field for each match
    for i, (market, score) in enumerate(matches, 1):
        # Truncate long questions
        question = market['question']
        if len(question) > 100:
            question = question[:97] + "..."
        
        # Format odds
        try:
            yes_price = float(market['outcomePrices'][0]) * 100
            no_price = float(market['outcomePrices'][1]) * 100
            odds_text = f"**Yes**: {yes_price:.1f}% | **No**: {no_price:.1f}%"
        except (ValueError, KeyError, IndexError):
            odds_text = "Odds unavailable"
        
        # Create field value
        field_value = f"{odds_text}\n*Match: {score:.0f}%*"
        
        # Add field
        embed.add_field(
            name=f"{i}. {question}",
            value=field_value,
            inline=False
        )
    
    # Footer with tip
    embed.set_footer(text="Click the market title to view on Polymarket")
    
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
