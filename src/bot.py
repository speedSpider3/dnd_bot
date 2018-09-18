import re
import discord
from discord.ext import commands
import pickle
from item import Item
from random import randint
from log import Logger
# from inventory import Inventory

log = Logger()
inventory = []
prefix = '!'
bot = commands.Bot(command_prefix=prefix)
inv_file = 'inv.bot'

def dm_check(ctx):
    try:
        for role in ctx.message.author.roles:
            if 'dungeon master' == role.name.lower():
                return True
        return False
    except Exception as e:
        log.queue_data(e)
    finally:
        log.write()

@bot.command()
async def checklog():
    message = log.read()
    await bot.say(message)
	
@bot.command(pass_context=True)
async def prefix(ctx, pre):
    """changes the prefix of the bot."""
    try:
        if dm_check(ctx):
            prefix = pre
        else:
            await bot.say('You can not set the prefix of the bot.')
    except Exception as e:
        log.queue_data(e)
    finally:
        log.write()


@bot.command(pass_context=True)
async def additem(ctx, title, desc, sell, buy, amt):
    """addes item to the inventory"""
    if dm_check(ctx):
        pickle.load(inv_file) # loads from file
        inventory.append(Item(title, desc, sell, buy, amt))
        pickle.dump(inventory, inv_file) # dumps datat in file
        await bot.say('added {0} to the inventory.'.format(title))
    else:
        await bot.say('You can not add an item to the inventory.')

@bot.command(pass_context=True)
async def rmitem(ctx, title, amt):
    """removes item(s) from the inventory."""
    if dm_check(ctx):
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
        await bot.say('You can not remove an item from the inventory.')
            

@bot.command(pass_context=True)
async def lsinv(ctx):
    """lists the inventory."""
    string = ''
    for item in inventory:
        string += '''title: {0.title} desc: {0.description}
            sell: {0.sell} buy: {0.buy} amount: {0.amount}\n'''.format(item)
    await bot.say(string)

@bot.command(pass_context=True)
async def roll(ctx, *args):
    arguments = {'sides': 20, 'amount': 1, 'adv/dis': 0, 'mods': [], 'secret': False}
    rolls = []
    total = 0
    for arg in args:

        if 'adv' == arg:
            arguments['adv/dis'] += 1
        elif 'dis' == arg:
            arguments['adv/dis'] -= 1        
        elif '+' in arg or '-' in arg:
            arguments['mods'].append(arg)
        elif 'secret' == arg:
            arguments['secret'] = True
        elif 'd' in arg:
            try:
                d_ind = arg.index('d')
                arguments['amount'] = int(arg[:d_ind])
                arguments['sides'] = int(arg[d_ind+1:])
            except Exception as e:
                log.queue_data(e)
        else:
            log.queue_data(SyntaxError('unknown command: {0}'.format(arg)))

    for _ in range(arguments['amount']):
        if arguments['adv/dis'] > 0:
            temp1 = randint(1,arguments['sides'])
            temp2 = randint(1,arguments['sides'])
            rolls.append(temp1 if temp1 > temp2 else temp2)
        elif arguments['adv/dis'] < 0:
            temp1 = randint(1,arguments['sides'])
            temp2 = randint(1,arguments['sides'])
            rolls.append(temp1 if temp1 < temp2 else temp2)
        else:
            rolls.append(randint(1,arguments['sides']))

    for roll in rolls:
        total += roll

    for mod in mods:
        total += int(mod)

    rolls = str_array(rolls)

    if arguments['secret']:
        log.write()
        message = 'you rolled, {0}'.format(rolls)
        await bot.send_message(ctx.message.author, message)
    else:
        log.write()
        message = '{0.message.author.mention} has rolled {1}'.format(ctx, rolls)
        await bot.say(message)
        
def str_array(arr):
    if len(arr) == 1:
        arr.insert(-1, 'a')
        arr = str(arr).replace(',', '')
    elif len(arr) == 2:
        arr.insert(-1, 'and')
        arr = str(arr).replace(',', '')
    else:
        arr.insert(-1, 'and')
        arr = str(arr)

    arr = arr.strip('[').strip(']').replace('\'', '').replace('and,', 'and')

    return arr

try:
    file = open('secret.bot', 'r')
    token = file.readline()
    file.close()
    token = token.replace('\n','')
    bot.run(token)
except Exception as error:
    print('Something went wrong ¯\_(ツ)_/¯')
    print(error)
    print(error.args)
finally:
    print('End of Bot.')

