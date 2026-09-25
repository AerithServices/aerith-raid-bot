import discord
import re

from src.utils.db import (
    get_user_presets,
    save_user_preset,
    delete_user_preset
)

from src.utils.helpers import Aerith_INVITE, success_embed

class PresetManagementView(discord.ui.LayoutView):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    container1 = discord.ui.Container(
        discord.ui.TextDisplay(content="## preset management"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.Section(
            discord.ui.TextDisplay(content="make a new preset >"),
            accessory=discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="create",
                custom_id="create_preset",
            ),
        ),
        discord.ui.Section(
            discord.ui.TextDisplay(content="list out your presets >"),
            accessory=discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="list",
                custom_id="list_preset",
            ),
        ),
        discord.ui.Section(
            discord.ui.TextDisplay(content="delete a preset >"),
            accessory=discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="delete",
                custom_id="delete_preset",
            ),
        ),
    )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        cid = interaction.data.get("custom_id")
        uid = str(interaction.user.id)

        if cid == "create_preset":
            presets = await get_user_presets(uid)
            if len(presets) >= 5:
                await interaction.response.send_message("You can only have up to 5 presets!", ephemeral=True)
                return False

            class CreatePresetModal(discord.ui.Modal, title="Create Preset"):
                title_input = discord.ui.TextInput(label="Preset Title", placeholder="Enter title...")
                content_input = discord.ui.TextInput(label="Preset Content", style=discord.TextStyle.paragraph, placeholder="Enter content...")

                async def on_submit(self2, modal_interaction: discord.Interaction):
                    text = self2.content_input.value
                    if "discord.gg/" in text.lower():
                        text = re.sub(r'(?:https?://)?discord\.gg/\S+', Aerith_INVITE, text)

                    await save_user_preset(uid, self2.title_input.value, text)
                    await modal_interaction.response.send_message(f"Preset `{self2.title_input.value}` saved!", ephemeral=True)

            await interaction.response.send_modal(CreatePresetModal())
            return False

        if cid == "list_preset":
            presets = await get_user_presets(uid)
            if not presets:
                await interaction.response.send_message("You have no presets.", ephemeral=True)
                return False

            sections = [
                discord.ui.TextDisplay(content="## your presets"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small)
            ]
            preset_map = {}
            for p in presets:
                t, c, u = p['title'], p['content'], p.get('uses', 0)
                preset_map[f"view_{t}"] = c
                sections.append(
                    discord.ui.Section(
                        discord.ui.TextDisplay(content=f"{t} - {u} uses"),
                        accessory=discord.ui.Button(
                            style=discord.ButtonStyle.secondary,
                            label="view contents",
                            custom_id=f"view_{t}",
                        ),
                    )
                )

            class DynamicListView(discord.ui.LayoutView):
                container1 = discord.ui.Container(*sections)
                async def interaction_check(self, it: discord.Interaction) -> bool:
                    cid = it.data.get("custom_id")
                    if cid and cid.startswith("view_"):
                        content = preset_map.get(cid, "Not found")
                        await it.response.send_message(f"Content for preset:\n```\n{content}\n```", ephemeral=True)
                        return False
                    return True

            await interaction.response.send_message(view=DynamicListView(), ephemeral=True)
            return False

        if cid == "delete_preset":
            presets = await get_user_presets(uid)
            if not presets:
                await interaction.response.send_message("You have no presets to delete.", ephemeral=True)
                return False

            del_sections = [
                discord.ui.TextDisplay(content="## delete presets"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small)
            ]
            for p in presets:
                del_sections.append(
                    discord.ui.Section(
                        discord.ui.TextDisplay(content=f"{p['title']}"),
                        accessory=discord.ui.Button(
                            style=discord.ButtonStyle.danger,
                            label="delete",
                            custom_id=f"del_{p['title']}",
                        ),
                    )
                )

            class DynamicDeleteView(discord.ui.LayoutView):
                container1 = discord.ui.Container(*del_sections)
                async def interaction_check(self, it: discord.Interaction) -> bool:
                    cid = it.data.get("custom_id")
                    if cid and cid.startswith("del_"):
                        title = cid.replace("del_", "")

                        class ConfirmDelete(discord.ui.View):
                            def __init__(self2, user_id, t):
                                super().__init__(timeout=30)
                                self2.user_id = user_id
                                self2.t = t

                            @discord.ui.button(label="Confirm Delete", style=discord.ButtonStyle.danger)
                            async def confirm(self2, it2: discord.Interaction, button: discord.ui.Button):
                                await delete_user_preset(self2.user_id, self2.t)
                                await it2.response.edit_message(content=f"Deleted preset `{self2.t}`", view=None)

                            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
                            async def cancel(self2, it2: discord.Interaction, button: discord.ui.Button):
                                await it2.response.edit_message(content="Cancelled.", view=None)

                        await it.response.send_message(f"Are you sure you want to delete `{title}`?", view=ConfirmDelete(uid, title), ephemeral=True)
                        return False
                    return True

            await interaction.response.send_message(view=DynamicDeleteView(), ephemeral=True)
            return False

        return True
