import discord
from discord import app_commands
import logging
import os
from dotenv import load_dotenv
import webserver
import random
import re

# ----------------------------------------

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True   

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# ----------------------------------------

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user}")

# ----------------------------------------
# WELCOME DM

async def send_dm(user: discord.User, message: str):
    try:
        await user.send(message)
    except:
        pass

@bot.event
async def on_member_join(member):
    msg = (
        "Welcome to **影 | Vanquished**.\n\n"
        "A social Roblox Blox Fruits community for chill chats and activity.\n\n"
        "Check <#1458860489772634318> for giveaways.\n"
        "Introduce yourself here <#1458860490695508229>\n\n"
        "Stay active. Stay restless."
    )
    await send_dm(member, msg)

# ----------------------------------------
# LOGGING

LOG_CHANNEL_ID = 1458860493228740652

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    guild = message.guild
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    deleter = "unknown"

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
        if entry.target.id == message.author.id:
            deleter = entry.user.mention
            break

    embed = discord.Embed(title="message removed", color=0x7200E6)
    embed.add_field(name="author", value=message.author.mention, inline=False)
    if message.content:
        embed.add_field(name="content", value=message.content[:1000], inline=False)
    embed.add_field(name="removed by", value=deleter, inline=False)
    embed.add_field(name="channel", value=message.channel.mention, inline=False)
    embed.set_footer(text="影 | Vanquished")
    await log_channel.send(embed=embed)

@bot.event
async def on_member_ban(guild, user):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    embed = discord.Embed(
        title="member banned",
        description=f"**user:** {user.mention}",
        color=0xFF3B3B
    )
    embed.set_footer(text="影 | Vanquished")
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
            embed.set_footer(text="影 | Vanquished")
            await log_channel.send(embed=embed)
            return

# ----------------------------------------
# SLASH COMMANDS

@tree.command(name="coinflip", description="flip a coin")
async def coinflip(interaction: discord.Interaction):
    await interaction.response.send_message(f"🪙 {random.choice(['heads','tails'])}")

@tree.command(name="dice", description="roll a dice")
async def dice(interaction: discord.Interaction):
    await interaction.response.send_message(f"🎲 rolled: **{random.randint(1,6)}**")

ANNOUNCE_CHANNEL_ID = 1458860489772634317

@tree.command(name="announce", description="send an announcement")
@app_commands.describe(title="announcement title", message="announcement text")
async def announce(interaction: discord.Interaction, title: str, message: str):

    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("no permission.", ephemeral=True)
        return

    channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)

    embed = discord.Embed(title=title, description=message, color=0x7200E6)
    embed.set_footer(text="影 | Vanquished")

    await channel.send(embed=embed)
    await interaction.response.send_message("announcement sent.", ephemeral=True)

@tree.command(name="serverinfo", description="show server information")
async def serverinfo(interaction: discord.Interaction):

    embed = discord.Embed(
        title="影 | Vanquished — Server Information",
        description=(
            "A social Roblox Blox Fruits community built for chill chats, events, and activity.\n\n"
            "Late nights. Restless minds. Active energy."
        ),
        color=0x7200E6
    )

    embed.add_field(name="📅 Created On", value="11 January 2026", inline=False)
    embed.add_field(name="👑 Owner", value="Pirate Hunter", inline=False)
    embed.add_field(name="🌙 Identity", value="Social • Roblox • Blox Fruits", inline=False)
    embed.add_field(name="🔒 Moderation", value="Active staff & logging enabled", inline=False)

    embed.set_footer(text="影 | Vanquished")
    await interaction.response.send_message(embed=embed)

@tree.command(name="fortune", description="receive a fortune")
async def fortune(interaction: discord.Interaction):

    fortunes = [
        "the night favors your grind",
        "a rare trade approaches",
        "your next raid will succeed",
        "restless energy surrounds you",
        "a surprise event awaits",
        "the shadows guide your path",
        "a powerful ally will appear",
        "fortune follows the persistent",
        "stay active, stay ahead",
        "the tide turns in your favor"
    ]

    await interaction.response.send_message(f"🔮 {random.choice(fortunes)}")

@tree.command(name="stats", description="show server stats")
async def stats(interaction: discord.Interaction):
    guild = interaction.guild
    await interaction.response.send_message(f"👥 members: **{guild.member_count}**")

@tree.command(name="bounty", description="see a user's bounty")
@app_commands.describe(user="user to check")
async def bounty(interaction: discord.Interaction, user: discord.User = None):

    if user is None:
        user = interaction.user

    amount = random.randint(50_000, 5_000_000_000)

    def format_bounty(n):
        parts = []
        if n >= 1_000_000_000:
            parts.append(f"{n//1_000_000_000} billion")
            n %= 1_000_000_000
        if n >= 1_000_000:
            parts.append(f"{n//1_000_000} million")
            n %= 1_000_000
        if n >= 1_000:
            parts.append(f"{n//1_000} thousand")
        return " ".join(parts)

    written = format_bounty(amount)

    embed = discord.Embed(
        title="⚔️ Vanquished Bounty",
        color=0x7200E6
    )

    embed.add_field(name="user", value=user.mention, inline=False)
    embed.add_field(name="bounty", value=f"**{written} beli**", inline=False)
    embed.set_footer(text="影 | Vanquished")

    await interaction.response.send_message(embed=embed)

# ----------------------------------------
# CHAT FILTER

INVITE_REGEX = re.compile(r"(discord\.gg\/|discord\.com\/invite\/)", re.IGNORECASE)

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
            f"{message.author.mention}, invite links are not allowed here."
        )
        return

    bad_words = {
        "fuck","bitch","rape","nigga","nigger","chutiya","madarchod","dumbass",
        "bhosdike","cunt","pussy","dick","porn","sex","cum","molest"
    }

    words = re.findall(r"\b\w+\b", content)

    for w in words:
        if w in bad_words:
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, keep the chat clean."
            )
            return

    await bot.process_application_commands(message)

# ----------------------------------------

webserver.keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
