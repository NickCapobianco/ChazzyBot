import discord, random, asyncio, logging, time, aiohttp, base64, json
from discord.ext import commands, tasks
from itertools import cycle

bot = commands.Bot(command_prefix=['.', '~'], description="ChazzyBot: Your friendly neighborhood Chazzy")


file = open("data/streamers.txt", 'r')
data = file.readlines()
name = []
url = []
for i in data:
    listing = i.split(',')
    name.append(listing[0])
    temp = listing[1].split('\n')
    url.append(temp[0])

file.close()

status = cycle(name)
streams = cycle(url)

#####################################################################################
#                                  EVENTS
#####################################################################################

# Lets user know when the bot is ready
@bot.event
async def on_ready():
    change_status.start()
    print(f"\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n")


# Sends new members information about our discord
@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name='Peeps')
    await member.add_roles(role)
    await member.create_dm()
    descriptionFile = open("data/serverDescription.txt")
    serverDescription = descriptionFile.read()
    descriptionFile.close()
    await member.send(serverDescription.format(member.name))


#####################################################################################
#                                  COMMANDS
#####################################################################################

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        """-ChazzyBot will join the command author's voice channel"""
        try:
            channel = ctx.author.voice.channel
            if ctx.voice_client is not None:
                await ctx.voice_client.move_to(channel)
        except AttributeError:
            await ctx.send("```Error: Could not connect.```")
            return
        return
        await ctx.author.voice.channel.connect()

    @commands.command(name='gtfo', aliases=['exit', 'ex', 'leave'])
    async def gtfo(self, ctx):
        """-ChazzyBot will leave its current voice channel"""
        if ctx.voice_client is None:
            await ctx.send("```Error: ChazzyBot is not currently in a voice channel.```")
            return
        elif ctx.voice_client.is_playing() and ctx.voice_client is not None:
            await ctx.voice_client.disconnect()
            return
        else:
            try:
                await ctx.voice_client.disconnect()
            except AttributeError:
                await ctx.send("```Error: Could not disconnect.```")
                return

    @commands.command(name='chazzy', aliases=['ch', 'chz', 'c'])
    async def chazzy(self, ctx, *, query=None):
        """-Chazzy soundboard"""
        if query == 'laugh' or query == '1':
            query = "soundboard/chazzy/laugh.mp3"
        if query == 'suck' or query == '2':
            query = "soundboard/chazzy/suck.mp3"
        if query == 'itsme' or query == '3':
            query = "soundboard/chazzy/itsme.mp3"
        if query == 'indahouse' or query == 'idh' or query == '4':
            query = "soundboard/chazzy/indahouse.mp3"
        if query == 'fullsquadonme' or query == 'fsom' or query == '5':
            query = "soundboard/chazzy/fsom.mp3"

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query),volume=0.5)
        if ctx.voice_client is not None:
            try:
                ctx.voice_client.play(source)
            except AttributeError:
                await ctx.send("```Error: Not connected to a voice channel```")
                return

    @commands.command(name='meme', aliases=['me', 'mem'])
    async def meme(self, ctx, *, query=None):
        """-Meme soundboard"""
        if query == 'dumbass' or query == '1':
            query = "soundboard/meme/dumbass.mp3"
        if query == 'omg' or query == '4':
            query = "soundboard/meme/omg.mp3"
        if query == 'piss' or query == '7':
            query = "soundboard/meme/piss.mp3"
        if query == 'douche' or query == 'douchebag' or query == '8':
            query = "soundboard/meme/douche.mp3"
        if query == 'finalcountdown' or query == 'fcd' or query == '9':
            query = "soundboard/meme/fcd.mp3"

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query),volume=0.5)
        ctx.voice_client.play(source)

    @commands.command(name='volume', aliases=['vol', 'v'])
    async def volume(self, ctx, volume: int):
        """-Changes the music player's volume"""
        if ctx.voice_client is None:
            return await ctx.send("```Not connected to a voice channel.```")
        ctx.voice_client.source.volume = volume / 100
        return await ctx.send("```The player's volume has been changed to {}%.```".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """-Stops the audio player"""
        ctx.voice_client.stop()
        await ctx.send("```The audio player has been stopped.```")

    @commands.command()
    async def pause(self, ctx):
        """-Pauses the audio player"""
        ctx.voice_client.pause()
        await ctx.send("```The audio player has been paused.```")

    # @commands.command()
    # async def resume(self, ctx):
    #     """-Pauses the audio player"""
    #     if ctx.voice_client.is_paused():
    #         await ctx.voice_client.play()
    #         await ctx.send("```The audio player has resumed.```")
    #     else:
    #         raise commands.CommandError("```The audio player cannot be paused at this time.```")
    #         return

    @meme.before_invoke
    @chazzy.before_invoke
    @join.before_invoke
    @gtfo.before_invoke
    @stop.before_invoke
    @pause.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


class Text(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx):
        """-Returns ChazzyBot's ping in milliseconds"""
        await ctx.send(f"```Ping: {round(bot.latency * 1000)}ms```")

    @commands.command(name='purge', aliases=['pur'])
    async def delete_bot_messages(self, ctx):
        """-Purges the current text channel of ChazzyBot's messages"""

        def is_me(message):
            return message.author == bot.user and not message.pinned

        try:
            await ctx.channel.purge(limit=int(1000), check=is_me)
        except AttributeError:
            return

    @commands.command(name='delete', aliases=['del'])
    async def delete(self, ctx, amount=1):
        """-Clears a number of the user's messages from the channel"""

        def is_me(message):
            return message.author == ctx.author and not message.pinned

        try:
            await ctx.channel.purge(limit=int(amount) + 1, check=is_me)
        except AttributeError:
            return

    @commands.command(name='test')
    async def test(self, ctx):
        """-Tests to see if the bot is working"""
        try:
            await ctx.send("```Commands are working.```")
        except AttributeError:
            await ctx.send("```Error: Commands are currently broken.```")
            return

    @commands.command(name='roll')
    async def roll(self, ctx):
        """-Rolls a die (1-6)"""
        num = random.randint(1, 6)
        await ctx.send(f"```{ctx.author.name} rolled a: {str(num)}```")

    @commands.command(name='rps')
    async def rock_paper_scissors(self, ctx):
        """-Randomly chooses between rock, paper, and scissors"""
        choices = ['rock', 'paper', 'scissors']
        result = random.choice(choices)
        await ctx.send(f"```{ctx.author.name} used {result}```")

    # Secret command to delete all messages in chat
    @commands.command(name='clear', hidden=True)
    @commands.is_owner()
    async def delete_all_channel_messages(self, ctx, amount=None):
        try:
            if amount is None:
                await ctx.channel.purge(limit=None, check=lambda message: not message.pinned)
            else:
                await ctx.channel.purge(limit=int(amount) + 1, check=lambda message: not message.pinned)
        except AttributeError:
            await ctx.send("```You are not the discord owner and therefore cannot use this command.```")
            return

    @commands.command(name='aliases')
    async def aliases(self, ctx):
        """-Lists alternative methods of calling standard commands"""
        aliasesFile = open("data/aliases.txt", 'r')
        aliasData = aliasesFile.read()
        aliasesFile.close()
        await ctx.send(f'```{aliasData}```')

    @commands.command(name='count')
    async def count_members(self, ctx):
        """-Returns the number of total members on this server (excluding bots)"""
        memberCount = ctx.guild.member_count
        memberList = ctx.guild.members
        botCount = 0
        for discord.user in memberList:
            if discord.user.bot:
                botCount += 1
        await ctx.send(f"```There are {memberCount - botCount} members on this server.```")


#####################################################################################
#                                  LOOPS
#####################################################################################

# Loops bot status every 5 minutes and streams twitch user links
@tasks.loop(seconds=300)
async def change_status():
    await bot.change_presence(activity=discord.Streaming(name=next(status), url=next(streams)))


# @tasks.loop(seconds=5)
# async def check_voice_status(ctx):
#     if not ctx.voice_client.is_playing():
#         await ctx.voice_client.disconnect()
#         raise commands.commandError("Successfully disconnected from voice.")

#####################################################################################
#                               MISCELLANEOUS
#####################################################################################

@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


#####################################################################################


file = open("data/config.txt", 'r')
data = file.read()
file.close()

bot.add_cog(Music(bot))
bot.add_cog(Text(bot))
bot.run(data)
