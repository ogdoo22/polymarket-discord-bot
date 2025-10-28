# Testing Checklist for Polymarket Discord Bot

## ⚠️ Important: API Limitations

**The Polymarket Gamma API only returns the top ~500 markets by volume/popularity.** This means:
- ✅ High-volume markets (Bitcoin, Trump, major events) will be found
- ❌ Low-volume or niche markets may not appear in the API
- ❌ Markets visible on polymarket.com might not be in the API

**This is a limitation of the public API, not our bot.**

## Quick Test Commands

Use these commands with **markets that exist in the API** to verify the bot works:

### ✅ Basic Functionality Tests (Using Real Available Markets)

```
!market Trump Department Education
Expected: Single market embed - "Will Trump end Department of Education in 2025?"

!market Fed rate hike 2025
Expected: Single market - "Fed rate hike in 2025?"

!market Bitcoin
Expected: Multiple crypto-related markets

!market recession 2025
Expected: "US recession in 2025?" market

!market Tether
Expected: Tether-related markets (insolvent, depeg, etc.)

!market Ukraine NATO
Expected: "Ukraine joins NATO in 2025?" market

!market alien invasion
Expected: "No Markets Found" embed with suggestions
```

### ✅ Input Validation Tests

```
!market ab
Expected: Error message "Please provide at least 3 characters"

!market
Expected: Error message with usage example

!market    
Expected: Error handling for empty query
```

### ✅ Edge Case Tests

```
!market When will Trump end the Department of Education in 2025?
Expected: High confidence match

!market govt shutdown end
Expected: Matches despite abbreviation "govt"

!market SHUTDOWN END
Expected: Case-insensitive matching works

!market shutdown? when?
Expected: Handles punctuation gracefully
```

## What to Look For

### In Discord

1. **Response Time**
   - First request: 2-5 seconds (API call)
   - Subsequent requests: <2 seconds (cached)

2. **Embed Formatting**
   - ✅ Title is clickable (links to Polymarket)
   - ✅ Odds display as percentages
   - ✅ Volume formatted with commas ($838,592)
   - ✅ Date is human-readable
   - ✅ Footer shows "Data from Polymarket"

3. **Multiple Matches Display**
   - ✅ Shows match percentage for each result
   - ✅ Truncates long questions with "..."
   - ✅ Lists 2-5 markets maximum

4. **Error Messages**
   - ✅ User-friendly (not technical stack traces)
   - ✅ Provide helpful suggestions
   - ✅ Include example usage

### In Bot Console

Look for these log messages:

```
[SEARCH] User: YourUsername | Query: 'Trump end Department of Education'
[SEARCH] Fetched 100 markets from API
[SEARCH] Found 1 matches
[SEARCH]   1. Will Trump end Department of Education in 2025?... (score: 95.8)
[SEARCH] Sending single market embed (score: 95.8)
```

**Good signs:**
- ✅ User and query logged
- ✅ Market count shown
- ✅ Match scores displayed
- ✅ Decision logic visible

**Red flags:**
- ❌ No [SEARCH] logs appearing
- ❌ 0 markets fetched
- ❌ Python exceptions/tracebacks
- ❌ "No matches" for obvious queries

## Regression Tests

After making changes, ensure these previously-working queries still work:

| Query | Expected Behavior |
|-------|-------------------|
| `Trump Department Education` | High score match (>85%) |
| `Bitcoin 200k` | Crypto-related market |
| `shutdown 2025` | Multiple shutdown markets |
| `election` | Multiple election markets |
| `climate change` | Related markets if available |

## Performance Benchmarks

### Cache Testing

1. **First Query:**
   ```
   !market Bitcoin 200k
   ```
   - Expected: 3-5 seconds
   - Log: "Fetched 100 markets from API"

2. **Repeated Query (within 5 minutes):**
   ```
   !market Bitcoin 200k
   ```
   - Expected: <1 second
   - Log: Should use cached data (no "Fetched" message)

3. **After 5+ Minutes:**
   ```
   !market Bitcoin 200k
   ```
   - Expected: 3-5 seconds
   - Log: "Fetched 100 markets from API" (cache refreshed)

### Concurrent Users

Have 2-3 people run commands simultaneously:
```
User A: !market Trump
User B: !market shutdown
User C: !market Bitcoin
```

- ✅ All should receive responses
- ✅ No errors or crashes
- ✅ Responses accurate for each query

## Fuzzy Matching Quality Test

Test various query styles to ensure matching works:

### Exact Phrases
```
!market Trump end Department of Education
Expected: Very high score (>90%)
```

### Keywords Only
```
!market Trump education
Expected: Reasonable match (>70%)
```

### Question Format
```
!market When will shutdown end
Expected: Matches question-style markets
```

### Abbreviations
```
!market govt shutdown
Expected: Matches "government shutdown"
```

### Typos (Should Still Work Reasonably)
```
!market Trupm educaton
Expected: Still finds relevant markets (>60% score)
```

## Debug Commands

If something isn't working:

1. **Check bot status:**
   ```
   Look for bot's online/green status in Discord
   ```

2. **Check console output:**
   ```
   Look for connection message: "Bot connected as: pmbot#1234"
   Check for error messages or exceptions
   ```

3. **Test API directly:**
   ```python
   # Run in Python console
   import asyncio
   from api_client import PolymarketClient
   
   async def test():
       client = PolymarketClient()
       markets = await client.get_markets()
       print(f"Fetched {len(markets)} markets")
   
   asyncio.run(test())
   ```

4. **Test fuzzy matching:**
   ```bash
   python test_matching.py
   ```

## Success Criteria

Bot is working correctly if:

- ✅ Responds to both `!market` and `/market` commands
- ✅ Returns relevant results 80%+ of the time
- ✅ Handles errors gracefully (no crashes)
- ✅ Response time <3 seconds
- ✅ Embeds format correctly
- ✅ Links are clickable
- ✅ Cache reduces API calls
- ✅ Cooldowns prevent spam
- ✅ Works in multiple servers

## Bug Reporting Template

If you find an issue, report it with:

```
Query: <exact command used>
Expected: <what should happen>
Actual: <what happened>
Console Log: <any error messages>
Screenshot: <Discord output>
```

Example:
```
Query: !market When will the government shutdown end
Expected: Match for "When will next government shutdown end?"
Actual: "No Markets Found"
Console Log: [SEARCH] Found 0 matches
Screenshot: [attach image]
```