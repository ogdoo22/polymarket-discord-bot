"""
Polymarket API client with caching support.

This module handles all interactions with the Polymarket Gamma API,
including fetching market data and caching responses to reduce API calls.
"""

import aiohttp
import asyncio
import time
import os
from typing import List, Dict, Optional


class PolymarketClient:
    """Client for interacting with Polymarket Gamma API."""
    
    def __init__(self):
        """Initialize the Polymarket API client with configuration from environment."""
        self.base_url = os.getenv('POLYMARKET_API_BASE', 'https://gamma-api.polymarket.com')
        self.timeout = int(os.getenv('API_TIMEOUT_SECONDS', '30'))
        self.retry_attempts = int(os.getenv('REQUEST_RETRY_ATTEMPTS', '3'))
        
        # Cache structure
        self.cache = {
            'data': None,
            'timestamp': 0,
            'ttl': int(os.getenv('CACHE_TTL_SECONDS', '300'))
        }
    
    def _is_cache_valid(self) -> bool:
        """
        Check if the cached data is still valid.
        
        Returns:
            True if cache exists and hasn't expired, False otherwise
        """
        if self.cache['data'] is None:
            return False
        
        current_time = time.time()
        age = current_time - self.cache['timestamp']
        return age < self.cache['ttl']
    
    def _update_cache(self, data: List[Dict]) -> None:
        """
        Update the cache with new market data.
        
        Args:
            data: List of market dictionaries to cache
        """
        self.cache['data'] = data
        self.cache['timestamp'] = time.time()
    
    async def get_markets(self) -> List[Dict]:
        """
        Fetch active markets from Polymarket API with caching.
        
        Returns:
            List of market dictionaries
            
        Raises:
            Exception: If API request fails after retries
        """
        # Return cached data if valid
        if self._is_cache_valid():
            print("Using cached market data")
            return self.cache['data']
        
        # Fetch fresh data with retries
        for attempt in range(self.retry_attempts):
            try:
                print(f"Fetching markets from Polymarket API (attempt {attempt + 1}/{self.retry_attempts})")
                markets = await self._fetch_markets()
                
                # Update cache on success
                self._update_cache(markets)
                print(f"Successfully fetched {len(markets)} markets")
                return markets
                
            except asyncio.TimeoutError:
                if attempt == self.retry_attempts - 1:
                    raise Exception("Request timed out after multiple attempts. Please try again later.")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
            except aiohttp.ClientResponseError as e:
                if e.status == 429:  # Rate limit
                    retry_after = int(e.headers.get('Retry-After', 60))
                    raise Exception(f"Rate limit reached. Please wait {retry_after} seconds before trying again.")
                elif e.status >= 500:
                    if attempt == self.retry_attempts - 1:
                        raise Exception("Polymarket API is currently unavailable. Please try again later.")
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise Exception(f"API error: {e.status} - {e.message}")
                    
            except aiohttp.ClientError as e:
                if attempt == self.retry_attempts - 1:
                    raise Exception(f"Network error: {str(e)}")
                await asyncio.sleep(2 ** attempt)
        
        # Should never reach here, but just in case
        raise Exception("Failed to fetch markets after all retry attempts")
    
    async def _fetch_markets(self) -> List[Dict]:
        """
        Internal method to fetch markets from the API.

        Returns:
            List of market dictionaries

        Raises:
            Various aiohttp exceptions
        """
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            url = f"{self.base_url}/markets"
            params = {
                'closed': 'false',
                'limit': '100'
            }

            async with session.get(url, params=params) as response:
                response.raise_for_status()

                raw_text = await response.text()
                with open("polymarket_raw_response.json", "w", encoding="utf-8") as f:
                    f.write(raw_text)
                print("DEBUG: Raw response saved to polymarket_raw_response.json")


                try:
                    data = await response.json()
                except Exception:
                    raise Exception("Received invalid JSON data from Polymarket API")

                # Validate response structure
                if not isinstance(data, dict) or 'data' not in data:
                    raise Exception("Unexpected response format from Polymarket API")

                markets = data.get('data', [])

                # Filter out markets without required fields
                valid_markets = []
                for market in markets:
                    if self._is_valid_market(market):
                        valid_markets.append(market)

                return valid_markets

    
    @staticmethod
    def _is_valid_market(market: Dict) -> bool:
        """
        Validate that a market has core required fields.
        
        Accepts markets with any variation of field names to handle
        different API response structures.
        
        Args:
            market: Market dictionary to validate

        Returns:
            True if market has essential data, False otherwise
        """
        # Check if market is a dictionary
        if not isinstance(market, dict):
            return False
        
        # Check for question/title field (core requirement)
        has_question = any(key in market for key in ['question', 'title', 'name', 'text'])
        
        # Check for at least one price/odds field
        has_prices = any(key in market for key in ['outcomePrices', 'prices', 'odds', 'outcomes'])
        
        # Market is valid if it has both a question and price data
        return has_question and has_prices

