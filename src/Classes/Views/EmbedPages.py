import discord
from typing import List



class EmbedPageView(discord.ui.View):
    def __init__(self, pages: List[discord.Embed], timeout=None, nodelete=False):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.current_page = 0
        self.page_count = len(pages)

        self.page_counter.label = f"1/{self.page_count}"
        self.update_buttons()

        if nodelete:
            self.remove_item(self.close)


    async def show_page(self, page_num, interaction):
        self.current_page = page_num
        embed = self.pages[page_num]
        self.page_counter.label = f"{page_num + 1}/{self.page_count}"
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)


    def update_buttons(self):
        self.to_start.disabled = self.previous_page.disabled = self.current_page == 0
        self.next_page.disabled = self.to_end.disabled = self.current_page == self.page_count - 1
        self.page_counter.disabled = self.page_count == 1


    @discord.ui.button(emoji="⏪", style=discord.ButtonStyle.primary)
    async def to_start(self, interaction, button):
        await self.show_page(0, interaction)


    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction, button):
        if self.current_page > 0:
            await self.show_page(self.current_page - 1, interaction)


    @discord.ui.button(label="Placeholder", style=discord.ButtonStyle.secondary)
    async def page_counter(self, interaction, button):
        modal = GotoPageModal(interaction.message, self)
        modal.text_input.placeholder = f"Input a number from 1 - {self.page_count}"
        await interaction.response.send_modal(modal)


    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction, button):
        if self.current_page < self.page_count - 1:
            await self.show_page(self.current_page + 1, interaction)


    @discord.ui.button(emoji="⏩", style=discord.ButtonStyle.primary)
    async def to_end(self, interaction, button):
        await self.show_page(self.page_count - 1, interaction)


    @discord.ui.button(label="Close", style=discord.ButtonStyle.red, row=2)
    async def close(self, interaction, button):
        await interaction.response.defer()
        self.stop()
        await interaction.message.delete()



class GotoPageModal(discord.ui.Modal):
    text_input = discord.ui.TextInput(label="Page Number", style=discord.TextStyle.short)


    def __init__(self, message: discord.Message, view: EmbedPageView):
        super().__init__(timeout=None, title="Go to Page")
        self.message = message
        self.view = view


    async def on_submit(self, interaction: discord.Interaction):
        page_num = int(self.text_input.value) - 1
        if 0 <= page_num < self.view.page_count:
            await self.view.show_page(page_num, interaction)
        else:
            valid_range = f"Valid page range: 1-{self.view.page_count}"
            await interaction.response.send_message(f"Invalid page number. {valid_range}", ephemeral=True)
