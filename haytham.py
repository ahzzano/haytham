
import discord
from discord import Member, VoiceState
from discord.ext import commands

from classes import Room, GuildSetup

import asyncio

import json
import os

# settings stuff
DEFAULT_SETTINGS = {'token': '', 'generator_id': 0, 'generator_category': 0, 'guild_hosted': 0}
SETTINGS = DEFAULT_SETTINGS

if os.path.exists('settings.json'):
    with open('settings.json', 'r') as settings_file:
        SETTINGS = json.load(settings_file)

else:
    with open('settings.json', 'w') as outfile:
        outfile.write(json.dumps(DEFAULT_SETTINGS))

    print('please re-run this program')
    exit()

rooms = []
guilds = []

intents = discord.Intents.default()
intents.message_content=True

client = commands.Bot(command_prefix=['h'], intents=intents)

def get_generator_vc(): 
    return client.get_channel(SETTINGS['generator_id'])

def get_category_channel():
    return client.get_channel(SETTINGS['generator_category'])

def did_join_generator(before, after):
    generator_vc = get_generator_vc()
    return before.channel == None and after.channel == generator_vc

def main():
    client.run(SETTINGS['token'])

def save_settings():
    print(SETTINGS)
    with open('settings.json', 'rw') as outfile:
        outfile.write(json.dumps(SETTINGS))


@client.event
async def on_ready():
    vc = get_generator_vc()

    guilds.append(GuildSetup(vc, vc.guild, vc.category))
    print('ready')

# refactor this later
@client.event
async def on_voice_state_update(member, before, after):
    generator_vc = get_generator_vc()

    generator_category = generator_vc.category 
    
    if generator_vc == None:
        print("error")
        return
    
    if did_join_generator(before, after):
        print('joined a generator vc')
        
        r = Room(member, guilds[0])
        await r.create_vc(guilds[0])

        #private_vc = await generator_vc.guild.create_voice_channel(f'{member.name}\'s Room ', category = generator_category)
        #await member.move_to(private_vc)

        rooms.append(r)

    if after.channel == None:
        await asyncio.sleep(2.5)
            
        print('left vc')
        matches = [room for room in rooms if before.channel == room.main_vc]
        
        for room in matches:
            await room.remove_vc()

            rooms.remove(room)

        print('left room')

    return


@client.command(name="setup")
async def setup(ctx):
    await ctx.send(f'Setting up the stuff')
    guild = ctx.guild

    generator_category = await guild.create_category('Private Chat')
    generator_vc = await guild.create_voice_channel('Click here to create VC', category=generator_category)
    
    SETTINGS['guild_hosted'] = guild.id 
    SETTINGS['generator_category'] = generator_category.id 
    SETTINGS['generator_id'] = generator_vc.id 

    save_settings()
    print(ctx)


if __name__ == '__main__':
    main()
