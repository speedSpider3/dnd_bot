import re
import discord
from discord.ext import commands
import pickle
from item import Item
from random import randint
from log import Logger
from inventory import Inventory

log = Logger()
inventory = []
prefix = '!'
bot = commands.Bot(command_prefix=prefix)
inv_file = 'inv.bot'

@bot.command()
def checklog():
    message = log.read()
    await bot.say(message)

def dm_check(ctx):
    try:
        return True if 'dungeon master' in ctx.message.author.role.name.lower() else False
    except Exception as e:
        log.queue_data(e)
    finally:
        log.write()

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
async def roll(ctx, *args):
    arguments = {'sides': [], 'amount': [], 'adv/dis': 0, 'mod': 0, 'secret': False, 'excpt': []}
    sides = []
    for arg in args:

        if 'adv' == arg:
            arguments['adv/dis'] += 1
        elif 'dis' == arg:
            arguments['adv/dis'] -= 1        
        elif '+' in arg or '-' in arg:
            arguments['mod'] += int(arg)
        elif 'secret' == arg:
            arguments['secret'] = True
        elif 'd' in arg:
            for x in range(0,len(arg) - 1):
                if arg[x] == 'd':
                    try:
                        if arg[:x] == '':
                            arguments['amount'].append(1) # sets amount to 1 
                            arguments['sides'].append(int(arg[x+1:])) # gets dice size
                        else:
                            arguments['amount'].append(int(arg[:x])) # gets numbers before the d
                            arguments['sides'].append(int(arg[x+1:])) # gets numbers after the d
                    except Exception as e:
                        log.queue_data(e)
                        arguments['excpt'].append(str(e))
        else:
            log.queue_data(SyntaxError('unknown command: {0}'.format(arg)))
            arguments['excpt'].append(str(SyntaxError('unknown command: {0}'.format(arg))))

    if arguments['sides'] == []:
        arguments['sides'].append(20)
        arguments['amount'].append(1)

    for rolls in range(0, len(arguments['sides'])):
        for j in range(0,arguments['amount'][rolls]):
            if arguments['adv/dis'] > 0: # roll adv
                temp1 = randint(1,arguments['sides'][rolls]) + arguments['mod']
                temp2 = randint(1,arguments['sides'][rolls]) + arguments['mod']
                sides.append(temp1 if temp1 > temp2 else temp2)
            elif arguments['adv/dis'] < 0: # roll dis
                temp1 = randint(1,arguments['sides'][rolls]) + arguments['mod']
                temp2 = randint(1,arguments['sides'][rolls]) + arguments['mod']
                sides.append(temp1 if temp1 < temp2 else temp2)
            else: # roll no adv
                sides.append(randint(1,arguments['sides'][rolls]) + arguments['mod'])

    sides.insert(-1, 'and')
    sides = str(sides).strip('[').strip(']').replace('\'', '').replace('and,', 'and')

    if arguments['secret']:
        log.write()
        message = 'you rolled, {0}'.format(sides)
        await bot.send_message(ctx.message.author, message)
    else:
        log.write()
        message = '{0.message.author.mention} has rolled {1}'.format(ctx, sides)
        await bot.say(message)
        
'''
@bot.command(pass_context=True)
async def roll_legacy(ctx, *args):
    """roll a dice of designated sides."""
    sides = 20
    numDice = 1
    mod_msg = ""
    mods = []
    adv = ""
    rolls = []
    adv_msg = ""
    force_crit = 0
    double = False
    double_msg = ""
    secret = False

    for arg in args:
        if re.match(r"^(([1-9]*)d[^io])", arg):
            if arg.startswith('d'):
                sides = int(arg[1:])
            else:
                i = arg.index('d')
                numDice = int(arg[0:i])
                sides = int(arg[i + 1:])
        elif '+' in arg or '-' in arg:
            mods.append(str(arg))
        elif 'adv' in arg or 'dis' in arg:
            adv = arg
        elif arg == 'force crit':
            force_crit = 1
        elif arg == 'force fail':
            force_crit = -1
        elif arg == 'double':
            double = True
            double_msg = ", doubled,"
        elif arg == 'secret':
            secret = True
        else:
            print('Invalid argument discarded')

    for _ in range(numDice):
        roll = 0
        if adv == "":
            roll = randint(1,sides)
        elif adv == "adv" or adv == "advantage":
            roll = roll_with_adv(sides)
            adv_msg = " with advantage"
        elif adv == "dis" or adv == "disadvantage":
            roll = roll_with_adv(sides, dis=True)
            adv_msg = " with disadvantage"
        else:
            await bot.say('Invalid argument! Try "adv" or "dis"')

        if force_crit > 0:
            roll = sides
        elif force_crit < 0:
            roll = 1
        rolls.append(roll)

    if numDice == 1:
        result = rolls[0]
        if double:
            result *= 2
        
        for mod in mods:
            result += int(mod)
    else:
        result = 0
        for roll in rolls:
            result += roll
        if double:
            result *= 2
        for mod in mods:
            result += int(mod)

    min_total = "total"

    if result < 1:
        result = 1
        min_total = "minimum"

    if len(mods) == 0:
        mod_msg = "no modifiers"
    elif len(mods) == 1:
        mod_msg = mods[0]
    else:
        mod_msg = printable_array(mods)

    message = ''

    if numDice > 1:
        message = (f'rolled {numDice} d{sides}s and got {printable_array(rolls)}{adv_msg}{double_msg} with {mod_msg} for a {min_total} of **{result}**.')
    elif rolls[0] == sides and sides == 20:
        message = (f'**crit**{adv_msg} on a d{sides}{double_msg} with {mod_msg} for a {min_total} of **{result}**!')
    elif rolls[0] == 1 and sides == 20:
        message = (f'rolled a **nat 1**{adv_msg} on a d{sides}{double_msg} with {mod_msg} for a {min_total} of **{result}**.')
    else:
        message = (f'rolled {rolls[0]}{adv_msg} on a d{sides}{double_msg} with {mod_msg} for a {min_total} of **{result}**.')

    if secret:
        await bot.send_message(ctx.message.author, f'You {message}')
    else:
        await bot.say(f'{ctx.message.author.mention} {message}')
   
def roll_with_adv(sides, dis=False):
    result = 0
    rollOne = randint(1,sides)
    rollTwo = randint(1,sides)

    if not dis:
        result = rollOne if rollOne > rollTwo else rollTwo
    if dis:
        result = rollOne if rollOne < rollTwo else rollTwo

    return result
        
def printable_array(arr):
    result = ""

    for i in range(len(arr)):
        if i < (len(arr) - 2):
            result += f'{arr[i]}'
            result += ', '
        elif i == (len(arr) - 2):
            result += f'{arr[i]}'
        else:
            result += f' and {arr[i]}'

    return result
'''

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
