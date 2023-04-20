from dataclasses import dataclass

from discord import Member, VoiceState, VoiceChannel, TextChannel, Guild, CategoryChannel

import asyncio

@dataclass(init=True)
class GuildSetup:
    generator: VoiceChannel
    guild: Guild 
    generator_category: CategoryChannel

@dataclass()
class Room:
    owner: Member
    main_vc: VoiceChannel
    no_mics: TextChannel
    guild: Guild
    active: True

    async def delete(self):
        await self.main_vc.delete()

    def __init__(self, owner:Member, gs: GuildSetup):
        self.owner = owner 
        self.guild = gs.guild

    async def create_channels(self, gs: GuildSetup):
        vc = await gs.guild.create_voice_channel(f'{self.owner.name}\'s Room', category=gs.generator_category)

        channel = await gs.guild.create_text_channel(f'{self.owner.name}\'s Room (no-mics)', category=gs.generator_category, position=vc.position-1)

        self.main_vc = vc
        self.no_mics = channel

        await self.owner.move_to(vc)

    async def remove_channels(self):
        self.active = False
        await self.main_vc.delete()
        await self.no_mics.delete()
        


    
