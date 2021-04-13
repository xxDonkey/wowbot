import discord
import json

from discord.ext import commands
from discord.utils import find
from utils import default
from utils import permissions
from utils import rolemanager as rm

from utils.data import Embed
from utils import wowchinfo as wow
 
class WoWInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get('config.json')

    """ Links the specified character to the discord account in the server the command was typed in. """
    @commands.command(name='link')
    @commands.check(permissions.link_channel)
    async def link(self, ctx, region, realm, name):
        savedchars = default.load_savedchars()
        name_key = ctx.message.guild.name.replace(' ', '')
        try:
            if savedchars[name_key] is not None:
                pass
        except KeyError:
            savedchars[name_key] = {}

        savedchars[name_key][str(ctx.author)] = {
            'region': region,
            'realm' : realm,
            'name'  : name
        }
        default.save_savedchars(savedchars)

        await self.update_roles(ctx, region, realm, name)

    """ Updates the authors roles based on the currently linked character. """
    @commands.command(name='roleupdate')
    @commands.check(permissions.update_channel)
    async def roleupdate(self, ctx):
        savedchars = default.load_savedchars()
        if not str(ctx.author) in list(savedchars[ctx.message.guild.name].keys()):
            await ctx.channel.send(f'Please link a character before calling `{self.config.prefix}roleupdate`.')
            return

        info = savedchars[ctx.message.guild.name][str(ctx.author)]
        await self.update_roles(ctx, info['region'], info['realm'], info['name'], link=False)

    """ The function called by both link and roleupdate to update the user's roles. """
    async def update_roles(self, ctx, region, realm, name, link=True):
        data = wow.get_character_data(
            region  = region,
            realm   = realm,
            name    = name,
        )

        if data == None:
            await ctx.channel.send(f'{ctx.author.mention}, the specified character could not be found. Please try again.')
            return

        msg = ctx.message
        got_mythic_plus_role, got_raid_progress_role = False, False
        
        score = data['mythic_plus_score']
        score_floored = default.floor_to_nearest(score, 100)
        mythic_plus_role_name = None
        
        if score_floored > 2000:
            got_mythic_plus_role = True
            if score_floored >= 4000:
                mythic_plus_role_name = '4.0k+ Raider IO'
            else:
                score_string = f'{score_floored}'
                mythic_plus_role_name = f'{score_string[0]}.{score_string[1]}k Raider IO'

        raid_progression_role_name = None
        role_names = [r.name for r in self.config.raid_progression_roles]
        if data['raid_progression'] in role_names:
            raid_progression_role_name = data['raid_progression']
            got_raid_progress_role = True

        if self.config.change_names:
            await ctx.author.edit(nick=name.lower().capitalize())

        await rm.clear_roles(msg.author)

        added_roles = []

        if self.config.track_armor_type:
            role = await rm.add_role(msg.guild, msg.author, data['armor_type'])
            if role:
                added_roles.append(role.name)

        if self.config.track_class:
            role = await rm.add_role(msg.guild, msg.author, data['class'])
            if role:
                added_roles.append(role.name)

        if self.config.track_mythic_plus:
            role = await rm.add_role(msg.guild, msg.author, mythic_plus_role_name)
            if role:
                added_roles.append(role.name)

        if self.config.track_raid_progression:
            role = await rm.add_role(msg.guild, msg.author, raid_progression_role_name)
            if role:
                added_roles.append(role.name)

        if self.config.track_linked:
            role = await rm.add_role(msg.guild, msg.author, self.config.linked_role.name)
            if role:
                added_roles.append(role.name)

        if len(added_roles) > 0:
            print(f'Gave user {msg.author} roles ' + ', '.join(added_roles))

        await rm.clear_guild_roles(msg.guild)
        await rm.update_guild_role_positions(msg.guild)

        if link:
            embed = Embed(bot=self.bot, title='Your character has been linked!', 
                description=f'{msg.author.mention}, you have linked your account to {name.capitalize()} ({realm.capitalize()}-{region.upper()}).\nYour Raider IO statistics will now be shown as ranks on the server.\nPlease wait another minute before relinking your account.')

            embed.add_field(name=f'Mythic Plus Score {":white_check_mark:" if got_mythic_plus_role else ":negative_squared_cross_mark:"}', value=score, inline=True)
            embed.add_field(name=f'Raid Progression {":white_check_mark:" if got_raid_progress_role else ":negative_squared_cross_mark:"}', value=data['raid_progression'], inline=True)

            await msg.channel.send(embed=embed)
            print(f'Linked {msg.author} to {name.capitalize()} ({region.upper()}-{realm.capitalize()}).')
        else:
            await msg.channel.send(f'Your roles have been updated, {msg.author.mention}.')
            print(f'Updated roles for {msg.author} : {name.capitalize()} ({realm.capitalize()}-{region.upper()}).')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        savedchars = default.default.load_savedchars()
        savedchars[guild.name.replace(' ', '')] = {}
        default.save_savedchars(savedchars)


def setup(bot):
    bot.add_cog(WoWInfo(bot))