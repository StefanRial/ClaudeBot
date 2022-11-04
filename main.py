import discord
import openai
from discord import app_commands

GUILD = discord.Object(id=YOUR_DISCORD_SERVER_ID_HERE)


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

openai.organization = "YOUR_OPENAI_ORGANIZATION_ID_HERE"
openai.api_key = "YOUR_OPENAI_API_KEY_HERE"
openai.Model.list()


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.tree.command()
@app_commands.describe(prompt="Description of the image that Claude should generate")
async def claude(interaction: discord.Interaction, prompt: str):
    mention = interaction.user.mention
    await interaction.response.defer()

    size = "1024x1024"
    if prompt.find("256x256") != -1:
        prompt = prompt.replace("256x256", "")
        size = "256x256"
    if prompt.find("512x512") != -1:
        prompt = prompt.replace("512x512", "")
        size = "512x512"
    if prompt.find("1024x1024") != -1:
        prompt = prompt.replace("1024x1024", "")
        size = "1024x1024"

    await interaction.followup.send(content=f"{mention} Processing your image of {prompt}...")

    response = openai.Image.create(prompt=prompt, n=1, size=size)
    image_url = response["data"][0]["url"]

    embed = discord.Embed(title=prompt)
    embed.set_image(url=image_url)

    await interaction.edit_original_response(content=f"{mention} Here is your result", embed=embed)

client.run("YOUR_DISCORD_BOT_API_KEY_HERE")
