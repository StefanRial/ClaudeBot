"""
This is a discord bot for generating images using OpenAI's DALL-E

Author: Stefan Rial
YouTube: https://youtube.com/@StefanRial
GitHub: https://https://github.com/StefanRial/ClaudeBot
E-Mail: mail.stefanrial@gmail.com
"""

import discord
import openai
import urllib.request
import os
from datetime import datetime
from configparser import ConfigParser
from discord import app_commands

file = "config.ini"
config = ConfigParser(interpolation=None)
config.read(file)

SERVER_ID = config["discord"]["server_id"]
DISCORD_API_KEY = config["discord"][str("api_key")]
OPENAI_ORG = config["openai"][str("organization")]
OPENAI_API_KEY = config["openai"][str("api_key")]

FILE_PATH = config["settings"][str("file_path")]
FILE_NAME_FORMAT = config["settings"][str("file_name_format")]

SIZE_LARGE = "1024x1024"
SIZE_MEDIUM = "512x512"
SIZE_SMALL = "256x256"
SIZE_DEFAULT = config["settings"][str("default_size")]

GUILD = discord.Object(id=SERVER_ID)

if not os.path.isdir(FILE_PATH):
    os.mkdir(FILE_PATH)

class Client(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=GUILD)
        await self.tree.sync(guild=GUILD)


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = Client(intents=intents)

openai.organization = OPENAI_ORG
openai.api_key = OPENAI_API_KEY
openai.Model.list()


def download_image(url: str):
    file_name = f"{datetime.now().strftime(FILE_NAME_FORMAT)}.jpg"
    full_path = f"{FILE_PATH}{file_name}"
    urllib.request.urlretrieve(url, full_path)
    return file_name


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.tree.command()
@app_commands.describe(prompt="Description of the image that Claude should generate")
async def claude(interaction: discord.Interaction, prompt: str):
    mention = interaction.user.mention
    channel = interaction.channel
    await interaction.response.defer()

    size = SIZE_DEFAULT
    if prompt.find(SIZE_SMALL) != -1:
        prompt = prompt.replace(SIZE_SMALL, "")
        size = SIZE_SMALL
    if prompt.find(SIZE_MEDIUM) != -1:
        prompt = prompt.replace(SIZE_MEDIUM, "")
        size = SIZE_MEDIUM
    if prompt.find(SIZE_LARGE) != -1:
        prompt = prompt.replace(SIZE_LARGE, "")
        size = SIZE_LARGE

    await interaction.followup.send(content=f"{mention} Processing your image of {prompt}...")

    response = openai.Image.create(prompt=prompt, n=1, size=size)
    image_url = response["data"][0]["url"]
    image_name = download_image(image_url)
    image_path = f"{FILE_PATH}{image_name}"

    file = discord.File(image_path, filename=image_name)
    embed = discord.Embed(title=prompt)
    embed.set_image(url=f"attachment://{image_name}")

    await channel.send(file=file, content=f"{mention} Here is your result", embed=embed)
    await interaction.delete_original_response()


client.run(DISCORD_API_KEY)
