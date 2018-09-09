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
        await bot.say('added {0} to the inventory.'.format(title))
    else:
        await bot.say('You can not add an item to the inventory.')

@bot.command(pass_context=True)
async def rmitem(ctx, title, amt):
    """removes item(s) from the inventory."""
    if dm_check():
        pickle.load(inv_file)
        for x in range(len(inventory)):
            if title == inventory[x].title:
                for y in range(amt):
                    inventory[x].amount -= 1
                    if inventory[x].amount < 1:
                        del inventory[x]
                        break
        pickle.dump(inventory, inv_file)
        await bot.say('Removed {0} {1}(s) from the inventory.'.format(amt, title))
    else:
        await bot.say('You can not remove an item to the inventory.')
            

@bot.command(pass_context=True)
async def lsinv(ctx):
    """lists the inventory."""
    string = ''
    for item in inventory:
        string += '''title: {0.title} desc: {0.description}
            sell: {0.sell} buy: {0.buy} amount: {0.amount}\n'''.format(item)
    await bot.say(string)

@bot.command(pass_context=True)
async def roll(ctx, mod=0, sides=20, adv=""):
    """roll a dice of designated sides."""
    roll = 0
    if adv == "":
        roll = randint(1,sides)
    elif adv == "adv" or adv == "advantage":
        one = randint(1,sides)
        two = randint(1,sides)
        if one > two:
            roll = one
        else:
            roll = two
    elif adv == "dis" or adv == "disadvantage":
        one = randint(1,sides)
        two = randint(1,sides)
        if one < two:
            roll = one
        else:
            roll = two
    else:
        await bot.say('Invalid argument! Try "adv" or "dis"')

    result = roll + mod
    min_total = "total"

    if result < 1:
        result = 1
        min_total = "minimum"

    if mod == 0:
        mod = "no modifier"
    elif mod > 0:
        mod = f'+{mod}'

    if roll == sides:
        await bot.say(f'{ctx.message.author.mention} crit with {mod} for a {min_total} of {result}!')
    elif roll == 1:
        await bot.say(f'{ctx.message.author.mention} rolled a nat 1 with {mod} for a {min_total} of {result}')
    else:
        await bot.say(f'{ctx.message.author.mention} rolled {roll} with {mod} for a {min_total} of {result}.')

   


try:
    file = open('secret.bot', 'r')
    token = file.readline()
    file.close()
    client = discord.Client()
    bot.run('NDg4MjUzMjI1OTQyNjQ2Nzg0.DnZhGA.VqbRVyrGigGxbFjUtG_KqgfORBQ')
except Exception as error:
    print('Something went wrong ¯\_(ツ)_/¯')
    print(error)
    print(error.args)
finally:
    print('End of Bot.')

