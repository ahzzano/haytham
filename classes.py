from dataclasses import dataclass

from discord import Member, VoiceState, VoiceChannel, TextChannel, Guild, CategoryChannel, PermissionOverwrite

import asyncio

@dataclass(init=True)
class GuildSetup:
    generator: VoiceChannel
    guild: Guild 
    generator_category: CategoryChannel

@dataclass()
class Room:
    owner: Member
    allowed_members: list[Member]
    main_vc: VoiceChannel
    waiting_room: VoiceChannel
    no_mics: TextChannel
    guild: Guild
    active: True

    async def delete(self):
        await self.main_vc.delete()

    def __init__(self, owner:Member, gs: GuildSetup):
        self.owner = owner 
        self.guild = gs.guild
        self.allowed_members = []

    async def create_channels(self, gs: GuildSetup):
        # main_vc_permissions = PermissionOverwrite(connect=False)
        # no_mics_permissions = Permissions()
        #
        # wr_vc_permissions = Permissions(connect=True)

        main_vc_overwrites = {
            gs.guild.default_role: PermissionOverwrite(connect=False),
            self.owner: PermissionOverwrite(connect=True)
        }

        wr_vc_overwrites = {
            gs.guild.default_role: PermissionOverwrite(connect=True)
        }

        no_mics_overwrites = {
            gs.guild.default_role: PermissionOverwrite(view_channel=False),
            self.owner: PermissionOverwrite(connect=True, view_channel=True)
        }

        vc = await gs.guild.create_voice_channel(f'{self.owner.name}\'s Room', category=gs.generator_category, overwrites=main_vc_overwrites)
        channel = await gs.guild.create_text_channel(f'{self.owner.name}\'s Room (no-mics)', category=gs.generator_category, position=vc.position-1, overwrites=no_mics_overwrites)
        waiting_room = await gs.guild.create_voice_channel(f'{self.owner.name}\'s Room (waiting room)', category=gs.generator_category, position=vc.position+1, overwrites=wr_vc_overwrites)

        self.main_vc = vc
        self.no_mics = channel
        self.waiting_room = waiting_room

        await self.owner.move_to(vc)
        self.allowed_members.append(self.owner)

    async def remove_channels(self):
        self.active = False

        await self.main_vc.delete()
        await self.no_mics.delete()
        await self.waiting_room.delete()

    async def add_to_allowed_members(self, member: Member):
        self.allowed_members.append(member) 
        


    
