import discord
import json

from discord.ext import commands, tasks
from utils import default
from utils import permissions
from utils import wowginfo as wow

from utils.data import Embed

class GuildSync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get('config.json')

        self.sync_guilds_loop_func.start()
        if self.config.track_guild:
            self.update_guild_members_loop_func.start()     

    @commands.command(name='guild')
    @commands.check(permissions.is_admin)
    async def link_guild(self, ctx, region, realm, name):
        realm = realm.replace('~', ' ')
        name = name.replace('~', ' ')

        info = self.guild_info.copy()
        info[ctx.guild.name] = {}
        info[ctx.guild.name]['linked_guild'] = {
            'region': region,
            'realm' : realm,
            'name'  : name
        } 
        info[ctx.guild.name]['channel'] = ctx.message.channel.id
        info[ctx.guild.name]['message'] = 0
        default.save_guild_info(info)

        await self.sync_guilds()

    async def sync_guilds(self):
        self.guild_info = default.load_guild_info()
        for guild_name in list(self.guild_info.keys()):
            guild = discord.utils.find(lambda g: g.name == guild_name, self.bot.guilds)
            if guild is None:
                print(f'Server {guild_name} is in guildinfo.json, but the bot is not a member of that server.')
                continue

            channel = discord.utils.find(lambda c: c.id == self.guild_info[guild_name]['channel'], guild.channels)
            if channel is None:
                print(f'No channel with id {self.guild_info[guild_name]["channel"]} was found. Please link a new channel.')
                continue

            messages = await channel.history().flatten()
            message = discord.utils.find(lambda m: m.id == self.guild_info[guild_name]['message'], messages)

            bosses_string, time_string = '', ''
            info = wow.get_guild_info(self.guild_info[guild_name]['linked_guild']['region'], self.guild_info[guild_name]['linked_guild']['realm'], self.guild_info[guild_name]['linked_guild']['name'])
            sorted(info.items(), key=lambda i: wow.bosses[i[0]])
            
            for k, v in info.items():
                name = k.replace('-', ' ').title()
                time = self.format_date(v)

                if name == 'Wrathion The Black Emperor':
                    name = 'Wrathion, The Black Emperor'
                elif name == 'Shadhar The Insatiable':
                    name = 'Shad\'har The Insatiable'
                elif name == 'Drestagath':
                    name = 'Drest\'agath'
                elif name == 'IlgynothIl\'gynoth, Corruption Reborn':
                    name = ' Corruption Reborn'
                elif name == 'Ra Den The Despoiled':
                    name = 'Ra-den The Despoiled'
                elif name == 'Carapace Of Nzoth':
                    name = 'Carapace Of N\'Zoth'
                elif name == 'Nzoth The Corruptor':
                    name = 'N\'Zoth The Corruptor'

                bosses_string += f'{name}\n'
                time_string += f'{time}\n'

            embed = Embed(bot=self.bot, title=f'Raid Progression For {self.guild_info[guild_name]["linked_guild"]["name"].title()}',
                    description=f'These are the current tier kills from the guild *{self.guild_info[guild_name]["linked_guild"]["name"].title()}*.')

            embed.add_field(name='Bosses',      value=bosses_string, inline=True)
            embed.add_field(name='\u200b',      value='\u200b',      inline=True)
            embed.add_field(name='Time Killed', value=time_string,   inline=True)
                
            if message is not None:
                await message.delete()
           
            sent = await channel.send(embed=embed)
            self.guild_info[guild_name]['message'] = sent.id
            print(f'Updated guild progress in server {guild_name}.')

        default.save_guild_info(self.guild_info)
        
    @tasks.loop(hours=12)
    async def sync_guilds_loop_func(self):
        await self.sync_guilds()

    @sync_guilds_loop_func.before_loop
    async def sync_guilds_loop_func_before_init(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if not isinstance(reaction.message.channel, discord.TextChannel) or reaction.message.id != self.guild_info[reaction.message.channel.guild.name]['message'] or not user.guild_permissions.administrator:
            return

        await self.sync_guilds()
        await reaction.remove(user)
    
    async def update_guild_members(self):
        if not self.config.track_guild:
            return

        self.guild_info = default.load_guild_info()
        for guild_name in list(self.guild_info.keys()):
            guild = discord.utils.find(lambda g: g.name == guild_name, self.bot.guilds)
            if guild is None:
                print(f'Server {guild_name} is in guildinfo.json, but the bot is not a member of that server.')
                continue

            name = self.config.guild_role_name
            role = discord.utils.find(lambda r: r.name == name, guild.roles)
            if role is None:
                print(f'Please add a role with the name {name} for guild members.')
                return

            guild_dict = self.guild_info[guild_name]['linked_guild']
            roster = wow.get_guild_roster(guild_dict['realm'].replace(' ', '-'), guild_dict['name'].replace(' ', '-'))

            savedchars = default.load_savedchars()
            guild_chars = savedchars[guild_name]

            for member in guild.members:
                try:
                    entry = guild_chars[str(member)]
                    if entry['region'] == guild_dict['region'] and entry['realm'] == guild_dict['realm'] and entry['name'].lower().capitalize() in roster:
                        await member.add_roles(role)
                        print(f'Added role {name} to {str(member)} ({entry["name"].lower().capitalize()} {entry["region"].upper()}-{entry["realm"].title()}).')
                except Exception as e:
                    continue
            

    @commands.command(name='updatemembers')
    @commands.check(permissions.is_admin)
    async def update_guild_member_cmd(self):
        await self.update_guild_members()

    @tasks.loop(minutes=30)
    async def update_guild_members_loop_func(self):
        await self.update_guild_members()

    @update_guild_members_loop_func.before_loop
    async def update_guild_members_loop_func_before_init(self):
        await self.bot.wait_until_ready()

    def format_date(self, date_string):
        if date_string is None: return 'Not Killed'

        split = date_string.split('T')

        date_split = split[0].split ('-')
        date = f'{date_split[1]}/{date_split[2]}/{date_split[0]}'

        time = split[1].split('.')[0]
        return f'**{time}** {date}'

def setup(bot):
    bot.add_cog(GuildSync(bot))





