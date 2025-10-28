# Polymarket Bot - Common Issues & Fixes

## Quick Start Testing

### Run Tests
```bash
# 1. Run diagnostic checker first
python diagnostic_checker.py

# 2. Run comprehensive test suite
python test_suite.py

# 3. If all tests pass, start the bot
python bot.py
```

---

## Issue 1: Bot Won't Connect to Discord

### Symptoms
- Bot script runs but shows no "connected" message
- Immediate exit or timeout error
- "Invalid token" or authentication errors

### Fixes

**Fix 1.1: Check Token**
```python
# In .env file
DISCORD_BOT_TOKEN=your_actual_token_here  # No quotes, no spaces

# Verify token is loaded
import os
from dotenv import load_dotenv
load_dotenv()
print(os.getenv('DISCORD_BOT_TOKEN'))  # Should print your token
```

**Fix 1.2: Enable Required Intents**
1. Go to Discord Developer Portal
2. Navigate to your application → Bot section
3. Scroll to "Privileged Gateway Intents"
4. Enable:
   - ✅ Message Content Intent (REQUIRED)
   - ✅ Server Members Intent (optional)
5. Save changes

**Fix 1.3: Verify Bot Code Has Intents**
```python
# In bot.py - add these lines
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True  # Critical for prefix commands
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)
```

---

## Issue 2: Commands Not Responding

### Symptoms
- Bot is online but doesn't respond to !market or /market
- No errors shown in console
- Bot can be mentioned but commands fail

### Fixes

**Fix 2.1: Sync Slash Commands**
```python
# In bot.py - add to on_ready event
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')
```

**Fix 2.2: Check Command Registration**
```python
# Ensure hybrid command is used
@bot.hybrid_command(name="market", description="Search Polymarket markets")
async def market(ctx, *, query: str):
    # Command code here
```

**Fix 2.3: Verify Bot Permissions**
In Discord server:
- Bot needs "Send Messages" permission
- Bot needs "Embed Links" permission
- Bot needs "Use Application Commands" permission

**Fix 2.4: Check Command Prefix**
```python
# Make sure prefix matches .env file
COMMAND_PREFIX=!

# In bot.py
bot = commands.Bot(command_prefix=os.getenv('COMMAND_PREFIX', '!'), intents=intents)
```

---

## Issue 3: API Calls Failing

### Symptoms
- "Request timed out" errors
- "Failed to fetch markets" messages
- Empty market data returned

### Fixes

**Fix 3.1: Verify API Endpoint**
```python
# In .env file
POLYMARKET_API_BASE=https://gamma-api.polymarket.com

# Test endpoint manually
import aiohttp
import asyncio

async def test_api():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://gamma-api.polymarket.com/markets?closed=false&limit=10') as resp:
            print(f"Status: {resp.status}")
            data = await resp.json()
            print(f"Markets: {len(data.get('data', []))}")

asyncio.run(test_api())
```

**Fix 3.2: Increase Timeout**
```python
# In api_client.py
async with session.get(
    url,
    timeout=aiohttp.ClientTimeout(total=60)  # Increase from 30 to 60
) as response:
```

**Fix 3.3: Add Retry Logic**
```python
# In api_client.py - add retry with exponential backoff
import asyncio

async def fetch_with_retry(session, url, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                response.raise_for_status()
                return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            await asyncio.sleep(wait_time)
```

**Fix 3.4: Handle Rate Limiting**
```python
# In api_client.py
if response.status == 429:
    retry_after = int(response.headers.get('Retry-After', 60))
    print(f"Rate limited. Waiting {retry_after} seconds...")
    await asyncio.sleep(retry_after)
    # Retry the request
```

---

## Issue 4: Fuzzy Matching Returns Poor Results

### Symptoms
- Obvious matches not found
- Too many irrelevant results
- Searches only work with exact text

### Fixes

**Fix 4.1: Lower Threshold**
```python
# In fuzzy_matcher.py - change score_cutoff
matches = process.extract(
    query,
    market_questions.keys(),
    scorer=fuzz.token_set_ratio,
    limit=5,
    score_cutoff=50  # Lower from 60 to 50 for more lenient matching
)
```

**Fix 4.2: Try Different Scorer**
```python
# Test different scoring methods
from rapidfuzz import fuzz

# Option 1: token_sort_ratio (handles word order)
scorer=fuzz.token_sort_ratio

# Option 2: partial_ratio (finds substring matches)
scorer=fuzz.partial_ratio

# Option 3: WRatio (weighted combination)
scorer=fuzz.WRatio
```

**Fix 4.3: Preprocess Query**
```python
# In fuzzy_matcher.py - add preprocessing
def preprocess_text(text: str) -> str:
    """Clean and normalize text for matching"""
    import re
    # Lowercase
    text = text.lower()
    # Remove special characters
    text = re.sub(r'[^\w\s]', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def find_matching_markets(query: str, markets: List[Dict]) -> List[Tuple[Dict, float]]:
    query = preprocess_text(query)
    # ... rest of function
```

**Fix 4.4: Increase Result Limit**
```python
# In fuzzy_matcher.py - get more results
matches = process.extract(
    query,
    market_questions.keys(),
    scorer=fuzz.token_set_ratio,
    limit=10,  # Increase from 5 to 10
    score_cutoff=45
)
```

---

## Issue 5: Embeds Not Displaying Correctly

### Symptoms
- Plain text instead of rich embeds
- Missing fields or broken formatting
- "Missing permissions" errors

### Fixes

**Fix 5.1: Check Bot Permissions**
```
Bot needs "Embed Links" permission in the server/channel
```

**Fix 5.2: Validate Embed Structure**
```python
# In embed_builder.py - add validation
def build_single_market_embed(market: Dict) -> discord.Embed:
    # Ensure required fields exist
    question = market.get('question', 'Unknown Market')
    slug = market.get('slug', '')
    
    # Truncate long text
    if len(question) > 256:
        question = question[:253] + "..."
    
    embed = discord.Embed(
        title=question,
        url=f"https://polymarket.com/market/{slug}" if slug else None,
        color=0x7C3AED
    )
    
    return embed
```

**Fix 5.3: Handle Missing Data**
```python
# In embed_builder.py - add defaults
def format_odds(outcome_prices):
    """Safely format odds with fallback"""
    try:
        if not outcome_prices or len(outcome_prices) < 2:
            return "Yes: N/A | No: N/A"
        
        yes_pct = float(outcome_prices[0]) * 100
        no_pct = float(outcome_prices[1]) * 100
        return f"Yes: {yes_pct:.1f}% | No: {no_pct:.1f}%"
    except (ValueError, TypeError, IndexError):
        return "Odds unavailable"
```

**Fix 5.4: Test Embed Limits**
```python
# Discord embed limits:
# - Title: 256 characters
# - Description: 4096 characters
# - Fields: 25 max
# - Field name: 256 characters
# - Field value: 1024 characters
# - Footer: 2048 characters
# - Total: 6000 characters

def truncate_text(text: str, max_length: int) -> str:
    """Safely truncate text"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
```

---

## Issue 6: Cache Not Working

### Symptoms
- Every request hits the API (slow responses)
- No improvement in response time
- Cache timestamp not updating

### Fixes

**Fix 6.1: Verify Cache Implementation**
```python
# In api_client.py - complete cache implementation
import time

class PolymarketClient:
    def __init__(self):
        self.cache = {
            'data': None,
            'timestamp': 0,
            'ttl': 300  # 5 minutes
        }
    
    async def get_markets(self):
        current_time = time.time()
        
        # Check if cache is valid
        if (self.cache['data'] is not None and 
            (current_time - self.cache['timestamp']) < self.cache['ttl']):
            print("Using cached data")  # Debug message
            return self.cache['data']
        
        # Fetch fresh data
        print("Fetching fresh data from API")  # Debug message
        markets = await self._fetch_from_api()
        
        # Update cache
        self.cache['data'] = markets
        self.cache['timestamp'] = current_time
        
        return markets
```

**Fix 6.2: Test Cache Behavior**
```python
# Test script
import asyncio
from api_client import PolymarketClient

async def test_cache():
    client = PolymarketClient()
    
    print("First call (should fetch from API):")
    markets1 = await client.get_markets()
    print(f"Got {len(markets1)} markets\n")
    
    print("Second call (should use cache):")
    markets2 = await client.get_markets()
    print(f"Got {len(markets2)} markets\n")
    
    print("Cache is same data:", markets1 is markets2)

asyncio.run(test_cache())
```

---

## Issue 7: Memory or Performance Issues

### Symptoms
- Bot becomes slow over time
- High memory usage
- Crashes after running for a while

### Fixes

**Fix 7.1: Clear Old Cache Entries**
```python
# In api_client.py - add cache size limit
def cleanup_cache(self):
    """Clear cache if it's too old or too large"""
    import sys
    
    if self.cache['data']:
        size = sys.getsizeof(self.cache['data'])
        if size > 10_000_000:  # 10MB limit
            print("Cache too large, clearing...")
            self.cache['data'] = None
            self.cache['timestamp'] = 0
```

**Fix 7.2: Use Weak References for Large Objects**
```python
# For very large data structures
import weakref

# Instead of storing direct reference
self.cache['data'] = weakref.ref(markets)

# When retrieving
cached_data = self.cache['data']()
if cached_data is not None:
    return cached_data
```

**Fix 7.3: Add Resource Cleanup**
```python
# In bot.py - cleanup on shutdown
@bot.event
async def on_disconnect():
    print("Bot disconnected, cleaning up...")
    # Clear caches
    polymarket_client.cache['data'] = None
```

---

## Issue 8: Error Messages Not Helpful

### Symptoms
- Generic "An error occurred" messages
- No information about what went wrong
- Difficult to debug issues

### Fixes

**Fix 8.1: Add Detailed Error Logging**
```python
# In bot.py - improve error handling
import traceback

@bot.hybrid_command(name="market")
async def market(ctx, *, query: str):
    try:
        # Command logic
        pass
    except Exception as e:
        # Log full error for debugging
        print(f"Error in market command:")
        print(traceback.format_exc())
        
        # Send user-friendly message
        error_msg = str(e) if str(e) else "Unknown error occurred"
        await ctx.send(f"❌ Error: {error_msg}\nPlease try again or contact support.")
```

**Fix 8.2: Add Specific Error Handlers**
```python
# In api_client.py - specific exceptions
class PolymarketAPIError(Exception):
    pass

class PolymarketTimeoutError(PolymarketAPIError):
    pass

class PolymarketRateLimitError(PolymarketAPIError):
    pass

# Use in code
if response.status == 429:
    raise PolymarketRateLimitError("Rate limit exceeded")
```

---

## Testing Checklist

### Pre-Deployment Tests
- [ ] Run `python diagnostic_checker.py` - all checks pass
- [ ] Run `python test_suite.py` - all tests pass
- [ ] Bot connects to Discord (see "Connected!" message)
- [ ] `!market bitcoin` returns results
- [ ] `/market ethereum` returns results
- [ ] Embeds display with proper formatting
- [ ] Links in embeds are clickable
- [ ] Error handling works (try `!market ab`)
- [ ] Cooldown prevents spam (try command rapidly)
- [ ] Cache works (second query is faster)
- [ ] Bot works in multiple servers

### Performance Tests
- [ ] Response time < 3 seconds (first query)
- [ ] Response time < 1 second (cached query)
- [ ] Bot handles 10+ concurrent users
- [ ] No memory leaks after 100+ commands
- [ ] Graceful handling of API timeout

### Edge Case Tests
- [ ] Very long query (200+ characters)
- [ ] Special characters (!@#$%^&*)
- [ ] Empty query
- [ ] Query with only spaces
- [ ] Unicode characters (emojis, non-English)
- [ ] Simultaneous requests from multiple channels

---

## Quick Fixes Summary

| Issue | Quick Fix |
|-------|-----------|
| Bot won't connect | Check token in .env, enable message_content intent |
| Commands not working | Add bot.tree.sync(), verify hybrid_command decorator |
| API timeout | Increase timeout, add retry logic |
| Poor fuzzy matching | Lower threshold to 50, try different scorer |
| Embeds not showing | Check "Embed Links" permission |
| Cache not working | Add timestamp validation, test with debug prints |
| Slow performance | Implement proper caching, cleanup old data |
| Unhelpful errors | Add detailed logging with traceback |

---

## Getting Help

### Debug Mode
Add to bot.py for verbose logging:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
```

### Test Individual Components
```python
# Test API client
python -c "import asyncio; from api_client import PolymarketClient; asyncio.run(PolymarketClient().get_markets())"

# Test fuzzy matcher
python -c "from fuzzy_matcher import find_matching_markets; print(find_matching_markets('bitcoin', [{'question': 'Bitcoin price'}]))"
```

### Check Dependencies
```bash
pip list | grep -E "discord|aiohttp|rapidfuzz|dotenv"
python --version  # Should be 3.8+
```

---

## Resources

- Discord.py Documentation: https://discordpy.readthedocs.io/
- Polymarket API: https://gamma-api.polymarket.com/
- RapidFuzz Docs: https://maxbachmann.github.io/RapidFuzz/
- Discord Developer Portal: https://discord.com/developers/applications

---

## Need More Help?

1. Run `python diagnostic_checker.py` and share output
2. Run `python test_suite.py` and note which tests fail
3. Check console logs for error messages
4. Verify all environment variables are set
5. Ensure Discord bot has proper permissions

Most issues are resolved by:
- Enabling message_content intent
- Adding bot.tree.sync() to on_ready
- Using aiohttp instead of requests
- Proper error handling in all async functions