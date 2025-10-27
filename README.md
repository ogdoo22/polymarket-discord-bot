# Polymarket Discord Bot

A Discord bot that allows users to search and display Polymarket prediction market data directly in Discord servers using natural language queries with intelligent fuzzy matching.

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![Discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 Quick Start

```bash
# Clone and navigate to the repository
git clone <your-repo-url>
cd polymarket-discord-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your Discord bot token

# Run the bot
python bot.py
```

## ✨ Features

- **Natural Language Search**: Search for markets using everyday language
- **Fuzzy Matching**: Finds relevant markets even with typos or approximate queries
- **Hybrid Commands**: Works with both prefix commands (`!market`) and slash commands (`/market`)
- **Beautiful Embeds**: Displays market data in rich, formatted Discord embeds
- **Real-time Odds**: Shows current Yes/No percentages for each market
- **Smart Caching**: Caches API responses for 5 minutes to reduce load and improve speed
- **Error Handling**: Graceful handling of API failures, timeouts, and invalid inputs
- **Rate Limiting**: Per-user cooldowns prevent spam

## 📋 Prerequisites

- **Python 3.8 or higher**
- **Discord Bot Token** (from Discord Developer Portal)
- **Discord Server** for testing

## 🛠️ Installation

### 1. Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Navigate to the "Bot" section in the sidebar
4. Click "Add Bot"
5. Under "Privileged Gateway Intents", enable:
   - **Message Content Intent** (required for prefix commands)
   - **Server Members Intent** (optional)
6. Click "Reset Token" and copy your bot token

### 2. Set Up the Project

```bash
# Clone the repository
git clone <your-repo-url>
cd polymarket-discord-bot

# Create and activate virtual environment
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env
```

Edit `.env` and add your Discord bot token:

```env
DISCORD_BOT_TOKEN=your_actual_bot_token_here
COMMAND_PREFIX=!
POLYMARKET_API_BASE=https://gamma-api.polymarket.com
CACHE_TTL_SECONDS=300
API_TIMEOUT_SECONDS=30
REQUEST_RETRY_ATTEMPTS=3
```

### 4. Invite Bot to Your Server

Generate an invite URL:

1. Go back to the Discord Developer Portal
2. Navigate to "OAuth2" → "URL Generator"
3. Select scopes:
   - `bot`
   - `applications.commands`
4. Select permissions:
   - Send Messages
   - Embed Links
   - Use Slash Commands
   - Read Message History
5. Copy the generated URL and open it in your browser
6. Select your server and authorize the bot

### 5. Run the Bot

```bash
python bot.py
```

You should see:
```
Starting Polymarket Discord Bot...
Command prefix: !
<YourBot>#1234 has connected to Discord!
Bot is in 1 server(s)
Synced 1 slash command(s)
```

## 📖 Usage

### Commands

#### Search for Markets
```
!market <query>
/market <query>
```

Search for Polymarket prediction markets using natural language.

**Examples:**
```
!market Bitcoin hitting 200k by 2027
/market Trump wins 2028 election
!market Ethereum price above 5000
!market NFL Super Bowl winner
```

#### Help Command
```
!help_market
```

Display detailed help information about the market command.

#### Info Command
```
!info
```

Display bot information and statistics.

#### Ping Command
```
!ping
```

Check bot latency/response time.

### Example Interactions

**Single Market (High Confidence)**
```
User: !market Bitcoin 200k 2027
Bot: [Rich embed with market details, current odds, volume, and close date]
```

**Multiple Matches**
```
User: /market Trump election
Bot: [Embed listing 3-5 related markets with odds and match scores]
```

**No Results**
```
User: !market alien invasion 2025
Bot: [Embed with "No markets found" and helpful suggestions]
```

## 🏗️ Project Structure

```
polymarket-discord-bot/
│
├── bot.py                 # Main bot entry point and command handlers
├── api_client.py          # Polymarket API client with caching
├── fuzzy_matcher.py       # RapidFuzz string matching logic
├── embed_builder.py       # Discord embed construction
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

### Module Descriptions

- **bot.py**: Main Discord bot with command handlers, error handling, and user interactions
- **api_client.py**: Handles all Polymarket API interactions with intelligent caching
- **fuzzy_matcher.py**: Uses RapidFuzz to find relevant markets with typo tolerance
- **embed_builder.py**: Creates beautifully formatted Discord embeds for different scenarios

## 🎨 Embed Types

### Single Market Embed
Shown when a high-confidence match is found (score > 85%) or only one result exists.

Features:
- Market question as clickable title
- Current Yes/No odds
- Trading volume
- Market close date
- Market description (truncated)

### Multiple Matches Embed
Shown when 2-5 markets match with confidence scores between 60-85%.

Features:
- List of matching markets
- Current odds for each
- Match quality percentage
- Numbered for easy reference

### No Matches Embed
Shown when no markets score above 60% similarity.

Features:
- Friendly error message
- Search suggestions
- Link to Polymarket search page

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DISCORD_BOT_TOKEN` | *Required* | Your Discord bot token |
| `COMMAND_PREFIX` | `!` | Prefix for text commands |
| `POLYMARKET_API_BASE` | `https://gamma-api.polymarket.com` | Polymarket API URL |
| `CACHE_TTL_SECONDS` | `300` | Cache lifetime (5 minutes) |
| `API_TIMEOUT_SECONDS` | `30` | API request timeout |
| `REQUEST_RETRY_ATTEMPTS` | `3` | Number of retry attempts |

### Bot Permissions

Minimum required permissions:
- **Send Messages**: Post responses
- **Embed Links**: Display rich embeds
- **Use Slash Commands**: Enable `/market` command
- **Read Message History**: Maintain context

**Note**: Do NOT grant Administrator permissions. The bot doesn't need them.

## 🚀 Deployment

### Railway (Recommended)

1. Fork this repository
2. Sign up at [Railway](https://railway.app)
3. Create new project from GitHub repo
4. Add environment variable: `DISCORD_BOT_TOKEN`
5. Deploy automatically

### Heroku

```bash
# Login to Heroku
heroku login

# Create new app
heroku create your-bot-name

# Set environment variables
heroku config:set DISCORD_BOT_TOKEN=your_token_here

# Deploy
git push heroku main
```

### DigitalOcean App Platform

1. Connect your GitHub repository
2. Configure environment variables in the dashboard
3. Deploy with one click

### VPS (Ubuntu/Debian)

```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Clone repository
git clone <your-repo-url>
cd polymarket-discord-bot

# Set up environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure .env file
nano .env

# Run with systemd (persistent)
sudo nano /etc/systemd/system/polymarket-bot.service
```

Example systemd service file:
```ini
[Unit]
Description=Polymarket Discord Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/polymarket-discord-bot
Environment="PATH=/path/to/polymarket-discord-bot/venv/bin"
ExecStart=/path/to/polymarket-discord-bot/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable polymarket-bot
sudo systemctl start polymarket-bot
sudo systemctl status polymarket-bot
```

## 🔧 Troubleshooting

### Bot Doesn't Connect

**Problem**: Bot shows "Invalid token" or doesn't connect

**Solutions**:
- Verify `DISCORD_BOT_TOKEN` in `.env` file
- Check if token was regenerated in Developer Portal
- Ensure `.env` file is in the same directory as `bot.py`
- Confirm no extra spaces around the token

### Commands Don't Work

**Problem**: Bot doesn't respond to `!market` or `/market`

**Solutions**:
- Ensure **Message Content Intent** is enabled in Developer Portal
- Verify bot has "Send Messages" permission in the channel
- Check if slash commands are synced (restart bot)
- Try using the command in a different channel

### API Errors

**Problem**: "Failed to fetch markets" or timeout errors

**Solutions**:
- Check your internet connection
- Verify Polymarket API is accessible: `https://gamma-api.polymarket.com/markets`
- Increase `API_TIMEOUT_SECONDS` in `.env`
- Check if Polymarket API is experiencing downtime

### Poor Matching Results

**Problem**: Bot returns irrelevant markets

**Solutions**:
- Use more specific search terms
- Include key words from the market title
- Try different phrasings of your query
- Check if the market exists on Polymarket.com first

### Cache Issues

**Problem**: Bot shows outdated odds

**Solutions**:
- Wait for cache to expire (default: 5 minutes)
- Restart the bot to clear cache
- Reduce `CACHE_TTL_SECONDS` for more frequent updates

## 🧪 Testing

### Manual Testing Checklist

- [ ] Bot connects successfully
- [ ] `!market` command responds
- [ ] `/market` slash command works
- [ ] API fetches market data
- [ ] Fuzzy matching returns relevant results
- [ ] Single market embed displays correctly
- [ ] Multiple matches embed works
- [ ] No matches message shows with suggestions
- [ ] Clickable links work
- [ ] Cache behavior is correct
- [ ] Cooldown prevents spam
- [ ] Error messages are clear

### Test Queries

Try these queries to test different scenarios:

```
# Should return single market
!market Bitcoin price 200000 December 2027

# Should return multiple matches
!market Trump election

# Should return no matches
!market completely nonexistent market xyz123

# Edge cases
!market BTC  (short query)
!market !@#$%^&*()  (special characters)
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write docstrings for public functions
- Test your changes thoroughly
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [Polymarket](https://polymarket.com) - Prediction markets platform
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [RapidFuzz Documentation](https://github.com/maxbachmann/RapidFuzz)
- [Discord Developer Portal](https://discord.com/developers/applications)

## 💬 Support

Having issues? Here's how to get help:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review closed GitHub issues
3. Open a new issue with details:
   - Python version
   - Error messages
   - Steps to reproduce
   - Expected vs actual behavior

## 🙏 Acknowledgments

- **Polymarket** for providing the public API
- **discord.py** for the excellent Discord library
- **RapidFuzz** for fast fuzzy string matching
- The Discord bot development community

## 📊 Future Enhancements

Planned features for future releases:

- [ ] Interactive button selection for multiple matches
- [ ] Price alerts and notifications
- [ ] Market tracking with live updates
- [ ] Historical price charts
- [ ] Portfolio integration
- [ ] Multi-language support
- [ ] Custom server configurations
- [ ] Leaderboard for most-searched markets

---

**Made with ❤️ for the prediction markets community**

*Disclaimer: This bot is not affiliated with Polymarket. Use at your own risk.*