# Polymarket Discord Bot - Manual Testing Guide

## Pre-Testing Setup

### 1. Environment Check
```bash
# Verify Python version
python --version  # Should be 3.8 or higher

# Verify all dependencies installed
pip list | grep discord
pip list | grep aiohttp
pip list | grep rapidfuzz
pip list | grep dotenv

# Check environment variables
cat .env  # Verify DISCORD_BOT_TOKEN is set
```

### 2. Run Automated Tests First
```bash
# Run diagnostic checker
python diagnostic_checker.py

# Run implementation validator
python implementation_validator.py

# Run comprehensive test suite
python test_suite.py
```

**Only proceed with manual testing if all automated tests pass.**

---

## Phase 1: Bot Connection Testing

### Test 1.1: Bot Startup
**Objective**: Verify bot connects to Discord

**Steps**:
1. Run: `python bot.py`
2. Wait for connection message

**Expected Output**:
```
<BotName> has connected to Discord!
Synced X command(s)
```

**Pass Criteria**:
- ✅ Bot shows "connected" message within 10 seconds
- ✅ No error messages in console
- ✅ Bot appears online in Discord server

**Fail Indicators**:
- ❌ "Invalid token" error → Check .env file
- ❌ Timeout → Check internet connection
- ❌ Permission error → Enable message_content intent

---

### Test 1.2: Bot Visibility
**Objective**: Confirm bot is visible and responsive

**Steps**:
1. Open Discord server where bot is added
2. Check member list for bot
3. Mention the bot: `@BotName`

**Expected Output**:
- Bot appears in member list with green "online" status
- Bot doesn't respond to mention (expected behavior)

**Pass Criteria**:
- ✅ Bot is visible in server
- ✅ Bot status is "online" (green dot)

---

## Phase 2: Command Testing

### Test 2.1: Basic Prefix Command
**Objective**: Test !market command with simple query

**Command**: `!market Bitcoin`

**Expected Output**:
- Bot shows "typing" indicator
- Response within 3-5 seconds
- Discord embed with market information

**Embed Should Contain**:
- ✅ Title with market question
- ✅ Clickable URL to Polymarket
- ✅ Current odds (Yes/No percentages)
- ✅ Volume (formatted as currency)
- ✅ Close date
- ✅ Purple color (0x7C3AED)
- ✅ Footer: "Data from Polymarket"

**Screenshot Checklist**:
- [ ] Embed displays correctly
- [ ] URL is clickable
- [ ] Percentages add up to ~100%
- [ ] Date is readable format

---

### Test 2.2: Slash Command
**Objective**: Test /market command

**Command**: `/market Ethereum`

**Steps**:
1. Type `/market` - autocomplete should appear
2. Select the market command
3. Enter query: `Ethereum`
4. Press Enter

**Expected Output**:
- Same format as prefix command
- Response time similar to !market

**Pass Criteria**:
- ✅ Slash command appears in autocomplete
- ✅ Command executes successfully
- ✅ Embed format identical to prefix command

---

### Test 2.3: Multiple Matches
**Objective**: Test query returning multiple results

**Command**: `!market election`

**Expected Output**:
- Embed title: "🔍 Found X markets matching 'election'"
- List of 2-5 markets
- Each market shows:
  - Question (truncated to 100 chars)
  - Odds (Yes/No percentages)
  - Match score percentage

**Pass Criteria**:
- ✅ Shows 2-5 matches
- ✅ Matches sorted by score (highest first)
- ✅ All scores ≥ 60%
- ✅ Footer suggests using !market for details

---

### Test 2.4: No Matches
**Objective**: Test query with no results

**Command**: `!market xyzabc123impossible`

**Expected Output**:
- Red embed (color 0xEF4444)
- Title: "❌ No Markets Found"
- Description with query text
- Suggestions for improving search

**Pass Criteria**:
- ✅ Red colored embed
- ✅ Helpful error message
- ✅ Search suggestions included
- ✅ Link to Polymarket search page

---

### Test 2.5: Input Validation
**Objective**: Test input validation rules

**Test Cases**:

| Command | Expected Result |
|---------|----------------|
| `!market` | "Usage: !market <search query>" |
| `!market ab` | "Please provide at least 3 characters" |
| `!market   ` | "Usage message" (empty after trim) |
| `!market !!!` | Valid search (special chars allowed) |

**Pass Criteria**:
- ✅ All validation errors show helpful messages
- ✅ No crashes or unhandled exceptions

---

## Phase 3: Fuzzy Matching Quality

### Test 3.1: Exact Match
**Command**: `!market Will Bitcoin hit $200k by 2027?`
(Use actual market question from Polymarket)

**Expected Output**:
- Single market embed
- Match score > 90%
- Correct market displayed

---

### Test 3.2: Partial Match
**Command**: `!market Bitcoin 200k`

**Expected Output**:
- Single market or multiple matches
- Includes Bitcoin-related markets
- Top match relevant to query

---

### Test 3.3: Typos
**Command**: `!market Bitcon price`

**Expected Output**:
- Still finds Bitcoin markets
- Fuzzy matching handles typo

---

### Test 3.4: Word Order
**Command**: `!market 2027 Bitcoin`

**Expected Output**:
- Same results as "Bitcoin 2027"
- Token set ratio handles word order

---

### Test 3.5: Case Insensitivity
**Commands**:
- `!market BITCOIN`
- `!market bitcoin`
- `!market BiTcOiN`

**Expected Output**:
- All return same results
- Case doesn't affect matching

---

## Phase 4: Performance Testing

### Test 4.1: Response Time (First Query)
**Command**: `!market Ethereum`

**Measurement**:
- Time from command sent to embed received
- Use Discord timestamp or stopwatch

**Pass Criteria**:
- ✅ Response within 5 seconds
- ⚠️  3-5 seconds is acceptable
- ❌ > 5 seconds needs investigation

---

### Test 4.2: Response Time (Cached)
**Commands**:
1. `!market Bitcoin`
2. Wait 2 seconds
3. `!market Ethereum`

**Expected**:
- Second query faster than first
- Response within 1-2 seconds

**Pass Criteria**:
- ✅ Cached response ≤ 2 seconds
- ✅ Noticeably faster than first query

---

### Test 4.3: Concurrent Users
**Setup**: Have 3 people run commands simultaneously

**Commands** (at same time):
- User 1: `!market Bitcoin`
- User 2: `!market Trump`
- User 3: `!market Ethereum`

**Expected Output**:
- All users get responses
- No crashes or errors
- Response times similar to single user

**Pass Criteria**:
- ✅ All commands succeed
- ✅ No timeout errors
- ✅ Bot remains responsive

---

### Test 4.4: Cooldown
**Commands** (rapid fire):
1. `!market Bitcoin`
2. Immediately: `!market Ethereum`

**Expected Output**:
- First command succeeds
- Second command shows cooldown message
- "Please wait X seconds before using this command again"

**Pass Criteria**:
- ✅ Cooldown activates (5 seconds)
- ✅ Cooldown message is friendly
- ✅ User can retry after cooldown expires

---

## Phase 5: Error Handling

### Test 5.1: API Timeout
**Setup**: Temporarily modify api_client.py timeout to 1 second

**Command**: `!market Bitcoin`

**Expected Output**:
- "⏱️ Request timed out. Please try again."
- No crash or stack trace visible to user

**Pass Criteria**:
- ✅ Graceful error message
- ✅ Bot remains responsive
- ✅ User can retry

---

### Test 5.2: Network Error
**Setup**: Disconnect from internet briefly

**Command**: `!market Bitcoin`

**Expected Output**:
- Error message about connection
- Bot recovers after reconnection

**Pass Criteria**:
- ✅ Doesn't crash
- ✅ Error message helpful
- ✅ Bot reconnects automatically

---

### Test 5.3: Invalid Market Data
**Note**: Hard to test manually, but validate error handling exists in code

**Check Code For**:
- Try-except around JSON parsing
- Validation of required fields
- Default values for missing data

---

## Phase 6: Edge Cases

### Test 6.1: Long Query
**Command**: `!market [200 character string]`

**Expected Output**:
- Query processed normally
- Results based on relevant keywords
- No truncation errors

---

### Test 6.2: Special Characters
**Commands**:
- `!market Bitcoin & Ethereum`
- `!market Trump (2028)`
- `!market $200k price?`

**Expected Output**:
- Commands process successfully
- Special characters handled gracefully

---

### Test 6.3: Unicode Characters
**Commands**:
- `!market Bitcoin 🚀`
- `!market élection`

**Expected Output**:
- Unicode characters handled
- No encoding errors

---

### Test 6.4: Multiple Channels
**Setup**: Bot in multiple text channels

**Steps**:
1. Send command in Channel #1
2. Simultaneously send command in Channel #2

**Expected Output**:
- Both channels receive responses
- Responses don't mix between channels
- Bot handles concurrent requests

---

## Phase 7: Embed Formatting

### Test 7.1: Link Functionality
**Steps**:
1. Run: `!market Bitcoin`
2. Click the embed title (should be a link)

**Expected Output**:
- Link opens Polymarket market page
- URL format: `https://polymarket.com/market/{slug}`
- Page loads correctly

**Pass Criteria**:
- ✅ Link is clickable
- ✅ Opens correct market page
- ✅ No 404 errors

---

### Test 7.2: Embed Limits
**Test**: Find market with very long description

**Expected Output**:
- Description truncated to ~200 characters
- Ends with "..."
- No overflow or formatting issues

---

### Test 7.3: Mobile Display
**Steps**:
1. Open Discord on mobile device
2. Run: `!market Bitcoin`

**Expected Output**:
- Embed displays correctly on mobile
- All fields readable
- Links still clickable

---

## Phase 8: Multi-Server Testing

### Test 8.1: Different Servers
**Setup**: Add bot to 2+ servers

**Steps**:
1. Run command in Server A
2. Run command in Server B

**Expected Output**:
- Commands work in both servers
- No interference between servers
- Cooldowns are per-user, not global

---

### Test 8.2: Permissions Variation
**Setup**: Test in channels with different permissions

**Channels to Test**:
- Channel where bot has all permissions
- Channel where bot can only send messages
- Channel where bot cannot embed links

**Expected Results**:
- Bot works in channels with proper permissions
- Graceful error in restricted channels

---

## Phase 9: Long-Running Stability

### Test 9.1: Extended Runtime
**Duration**: 30+ minutes

**Steps**:
1. Start bot
2. Run commands periodically (every 2-3 minutes)
3. Monitor console for errors
4. Check memory usage

**Pass Criteria**:
- ✅ Bot stays online entire duration
- ✅ No memory leaks (stable RAM usage)
- ✅ Response time doesn't degrade
- ✅ Cache continues working

---

### Test 9.2: Cache Expiration
**Steps**:
1. Run: `!market Bitcoin` (cache populated)
2. Wait 6+ minutes (cache TTL is 5 minutes)
3. Run: `!market Bitcoin` again

**Expected Output**:
- First query shows "Fetching fresh data" log
- Second query shows "Using cached data" log
- After 6 minutes, fetches fresh data again

---

## Testing Results Template

### Summary Table

| Test Category | Tests Passed | Tests Failed | Notes |
|---------------|--------------|--------------|-------|
| Bot Connection | X/2 | | |
| Commands | X/5 | | |
| Fuzzy Matching | X/5 | | |
| Performance | X/4 | | |
| Error Handling | X/3 | | |
| Edge Cases | X/4 | | |
| Embed Formatting | X/3 | | |
| Multi-Server | X/2 | | |
| Stability | X/2 | | |
| **TOTAL** | **X/30** | | |

---

## Acceptance Criteria

### Must Pass (Critical)
- ✅ Bot connects to Discord
- ✅ !market and /market commands work
- ✅ API successfully fetches data
- ✅ Fuzzy matching returns relevant results
- ✅ Embeds display correctly with all fields
- ✅ Links are clickable
- ✅ Error messages are helpful
- ✅ No crashes or unhandled exceptions

### Should Pass (Important)
- ✅ Response time < 3 seconds (first query)
- ✅ Response time < 1 second (cached)
- ✅ Cooldown prevents spam
- ✅ Handles 3+ concurrent users
- ✅ Cache works correctly
- ✅ Works across multiple servers

### Nice to Have (Optional)
- Mobile display optimized
- Unicode character support
- Very long queries handled
- Extended runtime stable (hours)

---

## Troubleshooting During Testing

### Bot Not Responding
1. Check console for errors
2. Verify bot is online (green status)
3. Check bot has permission to send messages
4. Try re-syncing commands: `!sync` (if implemented)

### Slow Response Times
1. Check internet connection
2. Verify cache is working (check logs)
3. Test Polymarket API directly
4. Check server load

### Embeds Not Showing
1. Verify "Embed Links" permission
2. Check if embed is valid (not too large)
3. Test in different channel
4. Check bot role permissions

### Incorrect Results
1. Test fuzzy matching with simpler queries
2. Verify API returns expected data
3. Check market question extraction
4. Adjust matching threshold if needed

---

## Post-Testing Actions

### If All Tests Pass ✅
1. Document any minor issues found
2. Take screenshots of working features
3. Write deployment notes
4. Prepare for production deployment

### If Tests Fail ❌
1. Document specific failures
2. Note error messages
3. Check relevant logs
4. Reference "Common Issues & Fixes" guide
5. Fix issues and re-test

---

## Final Checklist Before Deployment

- [ ] All automated tests pass
- [ ] All critical manual tests pass
- [ ] Bot has been tested for 30+ minutes without issues
- [ ] Multiple users have tested successfully
- [ ] Error handling verified
- [ ] Performance acceptable (< 3 second responses)
- [ ] Documentation complete
- [ ] Environment variables secured
- [ ] .env not committed to git
- [ ] Bot token regenerated if exposed
- [ ] Invite link tested
- [ ] Bot added to production server
- [ ] Monitoring/logging enabled

---

## Testing Notes

**Date**: ___________
**Tester**: ___________
**Version**: ___________

**Environment**:
- Python Version: ___________
- discord.py Version: ___________
- Server Count: ___________

**Issues Found**:
1. ___________
2. ___________
3. ___________

**Overall Assessment**:
- [ ] Ready for deployment
- [ ] Needs minor fixes
- [ ] Needs major fixes
- [ ] Not ready

**Additional Comments**:
___________
___________
___________