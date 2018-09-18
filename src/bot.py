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
    arguments = {'sides': 20, 'amount': 1, 'adv/dis': 0, 'mods': [], 'secret': False, 'double': False}
    msgs = {'rolls': [], 'double': '', 'adv/dis': '', 'min/total': 'total', 'mod': 'no modifiers'}
    for arg in args:

        if arg.endswith('d1'):
            await bot.say('Hysterical.')
            return
        elif 'adv' == arg:
            arguments['adv/dis'] += 1
        elif 'dis' == arg:
            arguments['adv/dis'] -= 1        
        elif '+' in arg or '-' in arg:
            arguments['mods'].append(arg)
        elif 'secret' == arg:
            arguments['secret'] = True
        elif 'double' == arg:
            arguments['double'] = True
            msgs['double'] = ', doubled,'
        elif 'd' in arg:
            try:
                if arg.startswith('d'):
                    arguments['sides'] = int(arg[1:])
                    print(arguments['sides'])
                else:
                    d_ind = arg.index('d')
                    arguments['amount'] = int(arg[:d_ind])
                    arguments['sides'] = int(arg[d_ind+1:])
                    print(arguments['sides'])
            except Exception as e:
                log.queue_data(e)
        else:
            log.queue_data(SyntaxError('unknown command: {0}'.format(arg)))

    for _ in range(arguments['amount']):
        if arguments['adv/dis'] > 0:
            temp1 = randint(1,arguments['sides'])
            temp2 = randint(1,arguments['sides'])
            msgs['rolls'].append(temp1 if temp1 > temp2 else temp2)
            msgs['adv/dis'] = ' with advantage'
        elif arguments['adv/dis'] < 0:
            temp1 = randint(1,arguments['sides'])
            temp2 = randint(1,arguments['sides'])
            msgs['rolls'].append(temp1 if temp1 < temp2 else temp2)
            msgs['adv/dis'] = ' with disadvantage'
        else:
            msgs['rolls'].append(randint(1,arguments['sides']))

    total = 0
    for roll in msgs['rolls']:
        total += roll
    if arguments['double']:
        total *= 2
    for mod in arguments['mods']:
        total += int(mod)

    if total < 1:
        total = 1
        msgs['min/total'] = 'minimum'

    if len(arguments['mods']) > 0:
        msgs['mod'] = str_array(arguments['mods'])

    message = ''
    if arguments['amount'] > 1:
        message = ('rolled {0} d{1}s and got {2}').format(
                    arguments['amount'], 
                    arguments['sides'], 
                    str_array(msgs['rolls']))
    elif msgs['rolls'][0] == 20:
        message = ('**crit**')
    elif msgs['rolls'][0] == 1 and sides == 20:
        message = ('rolled a **nat 1**')
    else:
        message = ('rolled {0}').format(msgs['rolls'][0])

    message += ('{0}{1} with {2} for a {3} of **{4}**.').format(
                msgs['adv/dis'],
                msgs['double'],
                msgs['mod'], 
                msgs['min/total'], 
                total)

    if arguments['secret']:
        log.write()
        await bot.send_message(ctx.message.author, 'You {0}'.format(message))
    else:
        log.write()
        await bot.say('{0.message.author.mention} {1}'.format(ctx, message))
        
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

