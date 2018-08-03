import discord
from discord.ext import commands
import pickle
from item import Item
from random import randint
#import asyncio

inventory = []
prefix = '!'
bot = commands.Bot(command_prefix=prefix)
inv_file = 'inv.bot'

def dm_check(ctx):
    return True if 'dungeon master' in ctx.message.author.role.name.lower() else False


@bot.command(pass_context=True)
async def prefix(ctx, pre):
    """changes the prefix of the bot."""
    if dm_check():
        prefix = pre
    else:
        await bot.say('You can not set the prefix of the bot.')

@bot.command(pass_context=True)
async def additem(ctx, title, desc, sell, buy, amt):
    """addes item to the inventory"""
    if dm_check():
        pickle.load(inv_file) # loads from file
        inventory.append(Item(title, desc, sell, buy, amt))
        pickle.dump(inventory, inv_file) # dumps datat in file
    else:
        await bot.say('You can not add an item to the inventory')

@bot.command(pass_context=True)
async def rmitem(ctx, title, amt):
    """removes item(s) from the inventory."""
    pass

@bot.command(pass_context=True)
async def lsinv(ctx):
    """lists the inventory."""
    pass

@bot.command(pass_context=True)
async def roll(ctx, sides):
    """roll a dice of designated sides."""
    await bot.say('{0.message.author}, rolled a {1} out of {2}.'.format(ctx, randint(1,sides), sides))


try:
    file = open('secret.bot', 'r')
    token = file.readline()
    file.close()
    bot.run(token)
except Exception:
    print('Something went wrong ¯\_(ツ)_/¯')
finally:
    print('End of Bot.')

