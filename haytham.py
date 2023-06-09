
import discord
from discord import Embed, Guild
from discord.ext import commands

from classes import Room, GuildSetup
from views import WaitingRoomView
from config import Config

import json
import os
import datetime

# settings stuff
DEFAULT_DATA = {'generators': []}
SETTINGS = DEFAULT_DATA

if os.path.exists('data.json'):
    with open('data.json', 'r') as settings_file:
        SETTINGS = json.load(settings_file)

else:
    with open('data.json', 'w') as outfile:
        outfile.write(json.dumps(DEFAULT_DATA))

rooms: list[Room] = []
guilds: list[GuildSetup] = []

intents = discord.Intents.default()
intents.message_content=True

client = commands.Bot(command_prefix=['h'], intents=intents)

def main(config: Config):
    client.run(config.get_token())

def save_settings():
    print(SETTINGS)
    with open('data.json', 'w') as outfile:
        outfile.write(json.dumps(SETTINGS))


@client.event
async def on_ready():
    print('Adding Guilds')
    for guild in SETTINGS['generators']:
        g: Guild | None = client.get_guild(guild['guild'])

        if g is None:
            print('Error: Guild does not exist')
            continue

        print(f'Adding Guild: {g.name}')

        vc = g.get_channel(guild['vc'])

        guilds.append(GuildSetup(vc, g, vc.category))

    print('Loaded')

# refactor this later
@client.event
async def on_voice_state_update(member, before, after):
    event_guild = member.guild
    
    generator = [g for g in guilds if g.guild == event_guild][-1].generator # a server must only have 1 generator
    active_rooms = [r for r in rooms if r.guild == event_guild]
    waiting_rooms = [r.waiting_room for r in active_rooms]
    main_rooms = [r.main_vc for r in active_rooms]
    
    if generator == None:
        print("error")
        return
    
    if before.channel == None and after.channel == generator:
        print('joined a generator vc')

        g = [gs for gs in guilds if gs.guild == member.guild]
        
        r = Room(member, g[-1])
        await r.create_channels(g[-1])

        rooms.append(r)

    if after.channel != None:
        r = [r for r in active_rooms if r.main_vc == after.channel]

        if len(r) >= 1:
            if not member in r[-1].allowed_members:
                await member.move_to(None)

    if before.channel in main_rooms or after.channel == None:
        # await asyncio.sleep(2.5)
        matches = [room for room in rooms if before.channel == room.main_vc and len(room.main_vc.members) <= 0]
        
        for room in matches:
            await room.remove_channels()
            rooms.remove(room)

        print('deleted room')

    if after.channel in waiting_rooms:
        room = [r for r in active_rooms if r.waiting_room == after.channel][-1]
        print(f'joining {room.main_vc.name}')

        # send embed
        
        avatar = member.display_avatar.url

        embed = Embed(title=f"A user wants to join!", timestamp=datetime.datetime.now(), description=f'User: \"{member.name}\" wants to join your private room')
        embed.set_thumbnail(url=avatar)

        # buttons and view

        view = WaitingRoomView(member, room)

        message = await room.no_mics.send(embed=embed, view=view)
        

    return

@client.command(name="setup")
async def setup(ctx):
    await ctx.send(f'Setting up the stuff')

    guild = ctx.guild

    generator_category = await guild.create_category('Private Chat')
    generator_vc = await guild.create_voice_channel('Click here to create VC', category=generator_category)
    
    SETTINGS['generators'].append({'vc': generator_vc.id, 'guild': generator_vc.guild.id})

    save_settings()

    gs = GuildSetup(generator_vc, generator_vc.guild, generator_vc.category)

    guilds.append(gs)

if __name__ == '__main__':
    c = Config.load_config('settings.yaml')
    print(c.configuration)

    main(c)
