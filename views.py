from classes import *
import discord

class WaitingRoomView(discord.ui.View):
    requesting_member: Member
    room: Room

    @discord.ui.button(label="Accept!")
    async def accept_request(self, interaction, button):
        await interaction.response.send_message('accepted')
        await self.room.add_to_allowed_members(self.requesting_member)
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
