import discord

from utils import default

config = default.get('config.json')

def get_roles():
    armor_type_roles = [r.name.replace('_', ' ') for r in config.armor_type_roles]
    class_roles = [r.name.replace('_', ' ') for r in config.class_roles]
    mythic_plus_roles = [r.name for r in config.mythic_plus_roles]
    raid_progression_roles = [r.name for r in config.raid_progression_roles]
    
    roles = armor_type_roles + class_roles + mythic_plus_roles + raid_progression_roles
    roles.append(config.linked_role.name)
    return roles

def get_role_colors():
    armor_type_colors = {r.name.replace('_', ' '): r.color for r in config.armor_type_roles}
    class_colors = {r.name.replace('_', ' '): r.color for r in config.class_roles}
    mythic_plus_colors = {r.name: r.color for r in config.mythic_plus_roles}
    raid_progression_colors = {r.name: r.color for r in config.raid_progression_roles}
    
    colors = {}
    colors.update(armor_type_colors)
    colors.update(class_colors)
    colors.update(mythic_plus_colors)
    colors.update(raid_progression_colors)
    colors[config.linked_role.name] = config.linked_role.color
    return colors

def get_role_positions():
    armor_type_positions = {r.name.replace('_', ' '): r.position for r in config.armor_type_roles}
    class_positions = {r.name.replace('_', ' '): r.position for r in config.class_roles}
    mythic_plus_positions = {r.name: r.position for r in config.mythic_plus_roles}
    raid_progression_positions = {r.name: r.position for r in config.raid_progression_roles}
    
    positions = {}
    positions.update(armor_type_positions)
    positions.update(class_positions)
    positions.update(mythic_plus_positions)
    positions.update(raid_progression_positions)
    positions[config.linked_role.name] = config.linked_role.position
    return positions

async def add_role(guild, member, name):
    if name == None: return
    #print(name)

    COLORS = get_role_colors()
    if name in get_roles():
        role = discord.utils.find(lambda r: r.name == name, guild.roles)
        if role == None: 
            color = COLORS[name]
            role = await guild.create_role(name=name, color=discord.Colour.from_rgb(color[0], color[1], color[2]))

        await member.add_roles(role)

    return role

async def clear_roles(member):
    roles_to_remove = []
    ROLES = get_roles()

    for role in member.roles:
        if role.name in ROLES:
            roles_to_remove.append(role)

    for role in roles_to_remove:
        await member.remove_roles(role)

async def clear_guild_roles(guild):
    for role in guild.roles:
        if role.name in get_roles() and len(role.members) == 0:
            await role.delete()

async def update_guild_role_positions(guild):
    def sort(arr, compare):
        for i in range (len(arr) - 1):
            for j in range(len(arr) - 1 - i):
                if compare(arr[j], arr[j + 1]):
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]

    POSITIONS = get_role_positions()
    def compare(role1, role2):
        return POSITIONS[role1.name] > POSITIONS[role2.name]

    ROLES = get_roles()
    roles_in_guild = [role for role in guild.roles if role.name in ROLES]
    sort(roles_in_guild, compare=compare)

    for i, role in enumerate(roles_in_guild):
        print(i, role.name)
        try:
            await role.edit(position=i + 1)
        except Exception:
            pass