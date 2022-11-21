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

config_file = "config.ini"
config = ConfigParser(interpolation=None)
config.read(config_file)

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


claude_intents = discord.Intents.default()
claude_intents.messages = True
claude_intents.message_content = True
client = Client(intents=claude_intents)

openai.organization = OPENAI_ORG
openai.api_key = OPENAI_API_KEY
openai.Model.list()


class Buttons(discord.ui.View):
    def __init__(self, prompt: str, path: str, size: str):
        super().__init__()
        self.prompt = prompt
        self.path = path
        self.size = size

    @discord.ui.button(label='Variation', style=discord.ButtonStyle.primary)
    async def variation(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"Creating a variation of {self.prompt}...", ephemeral=True)
        response = openai.Image.create_variation(image=open(self.path, "rb"), n=1, size=self.size)
        await send_result(interaction, self.prompt, response, self.size)
        self.stop()

    @discord.ui.button(label='Redo', style=discord.ButtonStyle.grey)
    async def redo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"Redoing {self.prompt}...", ephemeral=True)
        response = openai.Image.create(prompt=self.prompt, n=1, size=self.size)
        await send_result(interaction, self.prompt, response, self.size)
        self.stop()

    @discord.ui.button(label='Delete', style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        self.stop()


async def send_result(interaction: discord.Interaction, prompt: str, response, size: str):
    mention = interaction.user.mention
    channel = interaction.channel
    image_url = response["data"][0]["url"]
    image_name = download_image(image_url)
    image_path = f"{FILE_PATH}{image_name}"

    file = discord.File(image_path, filename=image_name)
    embed = discord.Embed(title=prompt)
    embed.set_image(url=f"attachment://{image_name}")

    await channel.send(file=file, content=f"{mention} Here is your result", embed=embed,
                       view=Buttons(prompt=prompt, path=image_path, size=size))
    await interaction.delete_original_response()


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
    await interaction.response.defer(ephemeral=True)

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

    await interaction.followup.send(content=f"Processing your image of {prompt}...", ephemeral=True)

    response = openai.Image.create(prompt=prompt, n=1, size=size)
    await send_result(interaction, prompt, response, size)

client.run(DISCORD_API_KEY)
