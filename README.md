# ClaudeBot
Python Discord bot for using OpenAI's image generator DALL-E

## Installation:

### To use this bot, you need 2 things
1. A discord application and bot user
2. An OpenAI account with a set up payment plan

### Open main.py and change the following values:

1. **YOUR_DISCORD_SERVER_ID_HERE**

2. **YOUR_DISCORD_BOT_API_KEY_HERE**

3. **YOUR_OPENAI_ORGANIZATION_ID_HERE**

4. **YOUR_OPENAI_API_KEY_HERE**

Now you can invite your bot to your server. It needs message and editing permissions.
Then run main.py.

## Usage:

- You can use the command /claude [your prompt]
- Claude will generate an image using OpenAI and will return it as an embedded link.
- You can put in 256x256, 512x512 or 1024x1024 anywhere inside your prompt to specify the image's resolution.
- Please see OpenAI's pricing about the cost of generating each image.
