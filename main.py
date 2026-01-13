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



@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user}")



async def send_dm(user: discord.User, message: str):
    try:
        await user.send(message)
    except:
        pass

@bot.event
async def on_member_join(member):
    msg = (
        "Heyy, welcome to Pirate Nation! 🏴‍☠️\n\n"
        "Check <#1458860489772634318> for current fruit events\n"
        "Check <#1458860489772634317> for server updates\n\n"
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

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
        if entry.target.id == message.author.id:
            deleter = entry.user.mention
            break

    embed = discord.Embed(title="message deleted", color=0x8000FF)
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

    embed = discord.Embed(title=title, description=message, color=0x8000FF)
    embed.set_footer(text="Pirate Nation")

    await channel.send(embed=embed)
    await interaction.response.send_message("announcement sent.", ephemeral=True)

@tree.command(name="serverinfo", description="show server information")
async def serverinfo(interaction: discord.Interaction):

    embed = discord.Embed(
        title="Pirate Nation — Server Information",
        description=(
            "Pirate Nation is a Blox Fruits community server created for players who want organized activity, fair trading, and real interaction.\n\n"
            "Built to grow steady, stay active, and keep things simple."
        ),
        color=0x7200E6
    )

    embed.add_field(name="📅 Created On", value="11 January 2026", inline=False)
    embed.add_field(name="👑 Owner", value="Pirate Hunter", inline=False)
    embed.add_field(name="🏴‍☠️ Focus", value="Blox Fruits trading, grinding, giveaways", inline=False)
    embed.add_field(name="🔒 Moderation", value="Active staff & logging enabled", inline=False)

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
        "victory waits in your next battle",
        "the seas favor your journey today"
    ]

    await interaction.response.send_message(f"🔮 {random.choice(fortunes)}")

@tree.command(name="stats", description="show server stats")
async def stats(interaction: discord.Interaction):
    guild = interaction.guild
    await interaction.response.send_message(f"👥 members: **{guild.member_count}**")

@tree.command(name="bounty", description="see a pirate's bounty")
@app_commands.describe(user="user to check bounty for")
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

    if amount >= 4_000_000_000:
        tier, emoji, color = "Pirate King", "👑", 0xFFD700
    elif amount >= 1_000_000_000:
        tier, emoji, color = "Emperor Class", "🐦‍🔥", 0xFF4500
    elif amount >= 500_000_000:
        tier, emoji, color = "Legendary Pirate", "🔥", 0xFF4500
    elif amount >= 100_000_000:
        tier, emoji, color = "Veteran Pirate", "⚔️", 0x8000FF
    else:
        tier, emoji, color = "Rising Pirate", "🏴‍☠️", 0x0F3D2E

    embed = discord.Embed(title=f"{emoji} Pirate Bounty", color=color)
    embed.add_field(name="Pirate", value=user.mention, inline=False)
    embed.add_field(name="Bounty", value=f"**{written} beli**", inline=False)
    embed.add_field(name="Tier", value=tier, inline=False)

    embed.set_footer(text="Pirate Nation")
    await interaction.response.send_message(embed=embed)



INVITE_REGEX = re.compile(r"(discord\.gg\/|discord\.com\/invite\/)", re.IGNORECASE)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Skip admins
    if message.author.guild_permissions.administrator:
        await bot.process_application_commands(message)
        return

    content = message.content.lower()

    # Invite filter
    if INVITE_REGEX.search(content):
        await message.delete()
        await message.channel.send(
            f"Hey {message.author.mention}, server invite links are not allowed here. ❌"
        )
        return

    # Bad word filter
    bad_words = {
        "fuck","bitch","lund","rape","nigga","nigger","harami","loda","lodu",
        "chutiya","madarchod","chut","bhosdike","bsdk","gaandu","lode",
        "cunt","pussy","dick","porn","sex","masturbate","cum","rapist",
        "molest","randi","rand","behenchod","tatti","gaand","mc","kutta"
    }

    words = re.findall(r"\b\w+\b", content)

    for w in words:
        if w in bad_words:
            await message.delete()
            await message.channel.send(
                f"Hey {message.author.mention}, please watch your language! ❌"
            )
            return

    await bot.process_application_commands(message)



webserver.keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
