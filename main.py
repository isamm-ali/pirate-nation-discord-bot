import discord
from discord.ext import commands
from discord import app_commands
import logging
import os
from dotenv import load_dotenv
import webserver
import random
import re
#----------------------------------------------------------------------------

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.members = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)
    #----------------------------------------------------------------------------

@bot.event
async def on_ready():
    print(f"We have logged in as, {bot.user.name}")


@bot.event
async def on_ready():
    await tree.sync()
    print("Slash commands synced.")


async def send_dm(user: discord.User, message: str):
    try:
        await user.send(message)
        return True
    except discord.Forbidden:
        return False  
    except Exception:
        return False


@bot.event
async def on_member_join(member):
    msg = (
        "Heyy, welcome to Pirate Nation! 🏴‍☠️\n\n"
        "check <#1458860489772634318> for current fruit events\n"
        "check <#1458860489772634317> for server updates\n\n"
        "Hope you enjoy your time here!"
    )
    
    await send_dm(member, msg)


LOG_CHANNEL_ID = 1458860493228740652
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    guild = message.guild
    log_channel = bot.get_channel(LOG_CHANNEL_ID)

    deleter = "unknown"

    # Check audit logs to see if a moderator deleted it
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
        if entry.target.id == message.author.id:
            deleter = entry.user.mention
            break

    embed = discord.Embed(
        title="message deleted",
        color=0x8000FF
    )

    embed.add_field(name="author", value=message.author.mention, inline=False)
    embed.add_field(name="deleted by", value=deleter, inline=False)
    embed.add_field(name="channel", value=message.channel.mention, inline=False)

    if message.content:
        embed.add_field(name="content", value=message.content[:1000], inline=False)

    await log_channel.send(embed=embed)


@bot.event
async def on_member_ban(guild, user):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)

    embed = discord.Embed(
        title="member banned",
        description=f"**user:** {user.mention}",
        color=0xFF3B3B
    )

    await log_channel.send(embed=embed)


@bot.event
async def on_member_remove(member):
    guild = member.guild
    log_channel = bot.get_channel(LOG_CHANNEL_ID)

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
        if entry.target.id == member.id:
            embed = discord.Embed(
                title="member kicked",
                description=f"**user:** {member.mention}\n**by:** {entry.user.mention}",
                color=0xFFA500
            )
            await log_channel.send(embed=embed)
            return


@tree.command(name="coinflip", description="flip a coin")
async def coinflip(interaction: discord.Interaction):
    result = random.choice(["heads", "tails"])
    await interaction.response.send_message(f"🪙 {result}")


@tree.command(name="dice", description="roll a 6-sided dice")
async def dice(interaction: discord.Interaction):
    result = random.randint(1, 6)
    await interaction.response.send_message(f"🎲 rolled: **{result}**")


ANNOUNCE_CHANNEL_ID = 1458860489772634317

@tree.command(name="announce", description="send an announcement")
@app_commands.describe(title="announcement title", message="announcement text")
async def announce(interaction: discord.Interaction, title: str, message: str):

    # staff-only check
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("no permission.", ephemeral=True)
        return

    channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)

    embed = discord.Embed(
        title=title,                 
        description=message,          
        color=0x8000FF                
    )

    embed.set_footer(text="Pirate Nation")

    await channel.send(embed=embed)
    await interaction.response.send_message("announcement sent.", ephemeral=True)


@tree.command(name="serverinfo", description="show server information")
async def serverinfo(interaction: discord.Interaction):

    embed = discord.Embed(
        title="Pirate Nation — Server Information",
        description=(
            "Pirate Nation is a Blox Fruits community server created for players who want organized activity, fair trading, and real interaction instead of chaotic spam hubs.\n\n"
            "Built to grow steady, stay active, and keep things simple."
        ),
        color=0x7200E6
    )

    embed.add_field(name="📅 Created On", value="11th January, 2026", inline=False)
    embed.add_field(name="👑 Owner", value="Pirate Hunter", inline=False)
    embed.add_field(name="🏴‍☠️ Server Focus", value="Blox Fruits trading, grinding, and giveaways", inline=False)
    embed.add_field(name="🌍 Community", value="Open to all regions\nEnglish as main language", inline=False)
    embed.add_field(name="🔒 Moderation", value="Active staff\nLogging enabled\nVerification required", inline=False)
    embed.add_field(name="🎯 Goal", value="Build a reliable Blox Fruits hub that stays active long-term", inline=False)

    embed.set_footer(text="Pirate Nation Official Server")

    await interaction.response.send_message(embed=embed)


@tree.command(name="fortune", description="get a pirate fortune")
async def fortune(interaction: discord.Interaction):

    fortunes = [
        "a legendary fruit awaits you soon",
        "a trade in your favor is coming",
        "danger follows your next raid",
        "today is a lucky grind day",
        "a surprise giveaway is near",
        "your next spin will shock the seas",
        "a powerful ally will join your crew",
        "beware of false traders in the shadows",
        "a rare fruit will cross your path",
        "victory waits in your next duel",
        "the seas favor your journey today",
        "a great raid success is close"
    ]

    await interaction.response.send_message(
        f"🔮 {random.choice(fortunes)}"
    )


@tree.command(name="stats", description="show server stats")
async def stats(interaction: discord.Interaction):
    guild = interaction.guild
    await interaction.response.send_message(
        f"👥 members: **{guild.member_count}**"
    )


@tree.command(name="bounty", description="see a pirate's bounty")
@app_commands.describe(user="user to check bounty for")
async def bounty(interaction: discord.Interaction, user: discord.User = None):

    if user is None:
        user = interaction.user

    amount = random.randint(50_000, 5_000_000_000)

    # format number into written form
    def format_bounty(n):
        parts = []

        billions = n // 1_000_000_000
        if billions:
            parts.append(f"{billions} billion")
        n %= 1_000_000_000

        millions = n // 1_000_000
        if millions:
            parts.append(f"{millions} million")
        n %= 1_000_000

        thousands = n // 1_000
        if thousands:
            parts.append(f"{thousands} thousand")

        return " ".join(parts)

    written = format_bounty(amount)

    # bounty tiers
    if amount >= 1_000_000_000:
        emoji = "🐦‍🔥"
        color = 0xFFD700   # gold
        tier = "Emperor Class"
    elif amount >= 500_000_000:
        emoji = "🔥"
        color = 0xFF4500   # orange-red
        tier = "Legendary Pirate"
    elif amount >= 4_000_000_000:
        emoji = "👑"
        color = 0xFF4500   # orange-red
        tier = "Pirate King"
    elif amount >= 100_000_000:
        emoji = "⚔️"
        color = 0x8000FF   # purple
        tier = "Veteran Pirate"
    else:
        emoji = "🏴‍☠️"
        color = 0x0F3D2E   # dark green
        tier = "Rising Pirate"

    embed = discord.Embed(
        title=f"{emoji} Pirate Bounty",
        color=color
    )

    embed.add_field(name="Pirate", value=user.mention, inline=False)
    embed.add_field(name="Bounty", value=f"**{written} beli**", inline=False)
    embed.add_field(name="Tier", value=tier, inline=False)

    embed.set_footer(text="Pirate Nation")

    await interaction.response.send_message(embed=embed)


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.guild_permissions.administrator:
        await bot.process_application_commands(message)
        return

    bad_words = {
        "fuck","bitch","lund","rape","nigger","nigga","harami","lodu","loda",
        "chutiya","madarchod","chut","bhosdike","bsdk","gaandu",
        "lode","cunt","pussy","dick","porn","sex","masturbate",
        "cum","gandu","rapist","molest","randi","rand","behenchod","bhenchod",
        "tatti","tatti ka","gaand","mc","mcchod","kutta","kutte","bitchass","fuckass",
    }

    words = re.findall(r"\b\w+\b", message.content.lower())

    for w in words:
        if w in bad_words:
            await message.delete()
            await message.channel.send(
                f"Hey!{message.author.mention}, please watch your language! ❌"
            )
            return

    await bot.process_application_commands(message)


INVITE_REGEX = re.compile(
    r"(discord\.gg\/|discord\.com\/invite\/)", re.IGNORECASE
)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.guild_permissions.administrator:
        await bot.process_application_commands(message)
        return

    content = message.content.lower()

    if INVITE_REGEX.search(content):
        await message.delete()
        await message.channel.send(
            f"Hey! {message.author.mention}, server invite links are not allowed here. ❌"
        )
        return



    #----------------------------------------------------------------------------


webserver.keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)