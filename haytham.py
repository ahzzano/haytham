
import discord
from discord import Member, VoiceState, Embed
from discord.ext import commands

from classes import Room, GuildSetup

import asyncio

import json
import os

# settings stuff
DEFAULT_SETTINGS = {'token': '', 'generators': []}
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

def main():
    client.run(SETTINGS['token'])

def save_settings():
    print(SETTINGS)
    with open('settings.json', 'w') as outfile:
        outfile.write(json.dumps(SETTINGS))


@client.event
async def on_ready():
    print('Adding Guilds')
    for guild in SETTINGS['generators']:
        g = client.get_guild(guild['guild'])
        vc = g.get_channel(guild['vc'])

        guilds.append(GuildSetup(vc, g, vc.category))

    print('READY')

class WaitingRoomView(discord.ui.View):
    requesting_member: Member
    room: Room

    @discord.ui.button(label="Accept!")
    async def accept_request(self, interaction, button):
        await interaction.response.send_message('accepted')
        await self.requesting_member.move_to(self.room.main_vc)
        self.stop()

    @discord.ui.button(label="Reject")
    async def reject_request(self, interaction, button):
        await interaction.response.send_message('rejected')
        await self.requesting_member.move_to(None)
        self.stop()

    def __init__(self, requesting_member: Member, room: Room):
        super(WaitingRoomView, self).__init__()

        self.requesting_member = requesting_member
        self.room = room

# refactor this later
@client.event
async def on_voice_state_update(member, before, after):
    event_guild = member.guild
    
    generator = [g for g in guilds if g.guild == event_guild][-1].generator # a server must only have 1 generator
    active_rooms = [r for r in rooms if r.guild == event_guild]
    waiting_rooms = [r.waiting_room for r in active_rooms]
    
    if generator == None:
        print("error")
        return
    
    if before.channel == None and after.channel == generator:
        print('joined a generator vc')
        
        r = Room(member, guilds[0])
        await r.create_channels(guilds[0])

        rooms.append(r)

    if after.channel == None:
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

        embed = Embed(title="A user wants to join!")
        embed.set_thumbnail(url=avatar)

        # buttons and view

        view = WaitingRoomView(member, room)

        await room.no_mics.send(embed=embed, view=view)

    return

@client.command(name="setup")
async def setup(ctx):
    await ctx.send(f'Setting up the stuff')

    guild = ctx.guild

    generator_category = await guild.create_category('Private Chat')
    generator_vc = await guild.create_voice_channel('Click here to create VC', category=generator_category)
    
    SETTINGS['generators'].append({'vc': generator_vc.id, 'guild': generator_vc.guild.id})

    save_settings()

    guilds.append(GuildSetup(generator_vc, generator_vc.guild, generator_vc.category))

if __name__ == '__main__':
    main()
