"""
Polymarket Discord Bot - Main Entry Point

A Discord bot that allows users to search and display Polymarket prediction
market data using natural language queries with fuzzy string matching.
"""

import discord
from discord.ext import commands
import os
import sys
from dotenv import load_dotenv

from api_client import PolymarketClient
from fuzzy_matcher import find_matching_markets
from embed_builder import (
    build_single_market_embed,
    build_multiple_matches_embed,
    build_no_matches_embed
)

# Load environment variables
load_dotenv()

# Validate required environment variables
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not DISCORD_BOT_TOKEN:
    print("ERROR: DISCORD_BOT_TOKEN not found in environment variables")
    print("Please create a .env file with your Discord bot token")
    sys.exit(1)

# Bot configuration
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')

# Set up Discord intents
intents = discord.Intents.default()
intents.message_content = True  # Required for prefix commands
intents.guilds = True

# Initialize bot
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# Initialize Polymarket API client
polymarket_client = PolymarketClient()


@bot.event
async def on_ready():
    """Called when the bot successfully connects to Discord."""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} server(s)')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} slash command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')


@bot.hybrid_command(
    name="market",
    description="Search for Polymarket prediction markets"
)
@commands.cooldown(1, 5, commands.BucketType.user)
async def market(ctx: commands.Context, *, query: str):
    """
    Search for Polymarket markets and display results.
    
    This command uses fuzzy string matching to find relevant markets
    even when the query doesn't exactly match market titles.
    
    Args:
        ctx: Discord context object
        query: User's search query (natural language)
        
    Example:
        !market Bitcoin 200k 2027
        /market Trump election 2028
    """
    # Input validation
    if not query or not query.strip():
        await ctx.send(
            "⚠️ Please provide a search query.\n"
            f"**Usage**: `{COMMAND_PREFIX}market <search query>`\n"
            f"**Example**: `{COMMAND_PREFIX}market Bitcoin hitting 200k`"
        )
        return
    
    if len(query.strip()) < 3:
        await ctx.send(
            "⚠️ Please provide at least 3 characters to search.\n"
            f"**Example**: `{COMMAND_PREFIX}market Bitcoin`"
        )
        return
    
    # Log the search query
    print(f"\n[SEARCH] User: {ctx.author.name} | Query: '{query}'")
    
    # Show typing indicator while processing
    async with ctx.typing():
        try:
            # Fetch markets (cached or fresh from API)
            markets = await polymarket_client.get_markets()
            print(f"[SEARCH] Fetched {len(markets)} markets from API")
            
            if not markets:
                await ctx.send(
                    "⚠️ No active markets available at the moment. "
                    "Please try again later."
                )
                return
            
            # Find matching markets using fuzzy matching
            matches = find_matching_markets(query, markets)
            
            # Log match results
            print(f"[SEARCH] Found {len(matches)} matches")
            if matches:
                for i, (market, score) in enumerate(matches[:3], 1):
                    print(f"[SEARCH]   {i}. {market['question'][:60]}... (score: {score:.1f})")
            
            # Build appropriate embed based on results
            if not matches:
                # No matches found
                embed = build_no_matches_embed(query)
                print("[SEARCH] Sending 'no matches' embed")
            elif len(matches) == 1 or matches[0][1] > 85:
                # Single market (high confidence >85% or only one result)
                embed = build_single_market_embed(matches[0][0])
                print(f"[SEARCH] Sending single market embed (score: {matches[0][1]:.1f})")
            else:
                # Multiple matches (2-5 results with scores 60-85)
                embed = build_multiple_matches_embed(query, matches)
                print(f"[SEARCH] Sending multiple matches embed ({len(matches)} markets)")
            
            # Send embed
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            # Bot doesn't have permission to send embeds
            await ctx.send(
                "❌ I don't have permission to send embeds in this channel. "
                "Please check my permissions and try again."
            )
            
        except Exception as e:
            # General error handler
            error_message = str(e)
            print(f"[ERROR] Error in market command: {e}")
            import traceback
            traceback.print_exc()
            
            # Send user-friendly error message
            await ctx.send(
                f"❌ An error occurred: {error_message}\n"
                "Please try again in a moment."
            )


@market.error
async def market_error(ctx: commands.Context, error: commands.CommandError):
    """
    Error handler for the market command.
    
    Handles cooldowns and other command-specific errors.
    """
    if isinstance(error, commands.CommandOnCooldown):
        # Cooldown error - user is using command too frequently
        await ctx.send(
            f"⏱️ Please wait **{error.retry_after:.1f} seconds** before using this command again."
        )
    elif isinstance(error, commands.MissingRequiredArgument):
        # Missing query argument
        await ctx.send(
            f"⚠️ Please provide a search query.\n"
            f"**Usage**: `{COMMAND_PREFIX}market <search query>`\n"
            f"**Example**: `{COMMAND_PREFIX}market Bitcoin hitting 200k`"
        )
    else:
        # Unknown error
        print(f"[ERROR] Unhandled error in market command: {error}")
        await ctx.send(
            "❌ An unexpected error occurred. Please try again later."
        )


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    """
    Global error handler for all commands.
    
    This catches errors that aren't handled by command-specific error handlers.
    """
    # Ignore errors that are already handled
    if hasattr(ctx.command, 'on_error'):
        return
    
    # Log the error
    print(f"[ERROR] Command error: {error}")
    
    # Don't send error messages for command not found
    if isinstance(error, commands.CommandNotFound):
        return


@bot.command(name="help_market", hidden=True)
async def help_market(ctx: commands.Context):
    """
    Display detailed help information for the market command.
    """
    embed = discord.Embed(
        title="📚 Polymarket Bot Help",
        description="Search for Polymarket prediction markets using natural language queries.",
        color=0x7C3AED
    )
    
    embed.add_field(
        name="🔧 Command",
        value=f"`{COMMAND_PREFIX}market <query>` or `/market <query>`",
        inline=False
    )
    
    embed.add_field(
        name="📝 Examples",
        value=(
            f"`{COMMAND_PREFIX}market Trump Department Education`\n"
            f"`{COMMAND_PREFIX}market Bitcoin 2025`\n"
            f"`{COMMAND_PREFIX}market Fed rate hike`\n"
            f"`{COMMAND_PREFIX}market Ukraine NATO`\n"
            f"`{COMMAND_PREFIX}market recession 2025`"
        ),
        inline=False
    )
    
    embed.add_field(
        name="💡 Search Tips",
        value=(
            "• Use natural language - the bot handles typos and variations\n"
            "• Be specific but not overly detailed\n"
            "• Search for key terms from the market title\n"
            "• High-volume markets are easier to find\n"
            "• Popular topics: politics, crypto, economy, geopolitics"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⚠️ Coverage Limitation",
        value=(
            "This bot searches **~500 most popular markets** by trading volume. "
            "Niche or low-volume markets may not appear even if they exist on polymarket.com."
        ),
        inline=False
    )
    
    embed.add_field(
        name="⏱️ Rate Limit",
        value="One command every 5 seconds per user",
        inline=False
    )
    
    embed.set_footer(text="Data from Polymarket API")
    
    await ctx.send(embed=embed)


@bot.command(name="ping", hidden=True)
async def ping(ctx: commands.Context):
    """Check bot latency."""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency: {latency}ms")


@bot.command(name="info", hidden=True)
async def info(ctx: commands.Context):
    """Display bot information."""
    embed = discord.Embed(
        title="🤖 Polymarket Bot",
        description="A Discord bot for searching Polymarket prediction markets",
        color=0x7C3AED
    )
    
    embed.add_field(
        name="📊 Stats",
        value=f"Servers: {len(bot.guilds)}\nLatency: {round(bot.latency * 1000)}ms",
        inline=True
    )
    
    embed.add_field(
        name="🔍 Market Coverage",
        value="Top ~500 markets by volume",
        inline=True
    )
    
    embed.add_field(
        name="ℹ️ Important",
        value=(
            "This bot searches the **most popular markets** from Polymarket's API. "
            "Low-volume or niche markets may not appear in search results even if they exist on polymarket.com. "
            "For best results, search for high-volume topics like politics, crypto, or major events."
        ),
        inline=False
    )
    
    embed.add_field(
        name="🔗 Links",
        value="[Polymarket](https://polymarket.com) • [All Markets](https://polymarket.com/markets)",
        inline=False
    )
    
    embed.set_footer(text=f"Discord.py {discord.__version__}")
    
    await ctx.send(embed=embed)


def main():
    """Main entry point for the bot."""
    print("Starting Polymarket Discord Bot...")
    print(f"Command prefix: {COMMAND_PREFIX}")
    
    try:
        bot.run(DISCORD_BOT_TOKEN)
    except discord.LoginFailure:
        print("\nERROR: Invalid Discord bot token")
        print("Please check your DISCORD_BOT_TOKEN in the .env file")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Failed to start bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()