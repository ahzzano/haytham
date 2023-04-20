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
    active: True

    async def delete(self):
        await self.main_vc.delete()

    def __init__(self, owner:Member, gs: GuildSetup):
        self.owner = owner 

        #main_loop = asyncio.get_running_loop()

        #main_loop.create_task(self.create_vc(owner, gs))

    async def create_vc(self, gs: GuildSetup):
        vc = await gs.guild.create_voice_channel(f'{self.owner.name}\'s Room', category=gs.generator_category)

        self.main_vc = vc

        await self.owner.move_to(vc)

    async def remove_vc(self):
        self.active = False
        await self.main_vc.delete()


    
