import re
import discord
import os
from discord.ext import commands
import pickle
from item import Item
from random import randint
from character import Character
from log import Logger
# from inventory import Inventory

log = Logger()
bot = commands.Bot(command_prefix='!')
dm_role = 'dungeon master'

@bot.command()
async def checklog():
    message = log.read()
    await bot.say(message)
	
@bot.command(pass_context=True)
async def prefix(ctx, pre):
    """changes the prefix of the bot."""
    try:
        if dm_check(ctx):
            bot = commands.Bot(command_prefix=pre)
        else:
            await bot.say('You can not set the prefix of the bot.')
    except Exception as e:
        log.queue_data(e)
    finally:
        log.write()

@bot.command(pass_context=True)
async def addpartymember(ctx, name, class_name, subclass_name=""):
    file = "party_files/" + ctx.message.channel.server.id + ".bot"
    if dm_check(ctx):
        party = load_party(ctx)
        player = Character(name,class_name,subclass_name)
        for character in party:
            if character.get_name().lower() == name.lower():
                await bot.say(name + " is already in the party!")
                return
        party.append(player)
        dump(file, party)
        await bot.say(player.get_name() + " succesfully added!")
    else:
        await bot.say('You can not add a member to the party.')

@bot.command(pass_context=True)
async def rmpartymember(ctx, character_name):
    if dm_check(ctx):
        party = load_party(ctx)
        deleted = False
        for character in party:
            if character.get_name().lower() == character_name.lower():
                deleted = True
        party = [ character for character in party if character.get_name().lower() != character_name.lower() ]
        if deleted:
            dump(file, party)
            await bot.say("Succesfully removed " + character_name + " from the party!")
        else:
            await bot.say(character_name + " not found.")
    else:
        await bot.say("You can not remove a member from the party.")

@bot.command(pass_context=True)
async def clearparty(ctx):
    if dm_check(ctx):
        file = "party_files/" + ctx.message.channel.server.id + ".bot"
        dump(file, [])
        await bot.say("Cleared the party.")
    else:
        await bot.say("You can not clear the party.")

@bot.command(pass_context=True)
async def lsparty(ctx):
    party = load_party(ctx)
    print_str = ""
    for player in party:
        print_str += "**" + player.to_string() + "**\n"
    if print_str == "":
        await bot.say("Party is empty!")
    else:
        await bot.say(print_str)

@bot.command(pass_context=True)
async def setsubclass(ctx, character_name, subclass):
    if dm_check(ctx):
        file = "party_files/" + ctx.message.channel.server.id + ".bot"
        party = load_party(ctx)
        set_subclass = False
        for character in party:
            if character.get_name().lower() == character_name.lower():
                character.set_subclass(subclass)
                set_subclass = True
        if set_subclass:
            dump(file, party)
            await bot.say("Set subclass succesfully!")
        else:
            await bot.say(character_name + " not found.")
    else:
        await bot.say("You cannot modify characters.")


@bot.command(pass_context=True)
async def additem(ctx, title, desc, sell, buy, amt, inv_name=""):
    """addes item to the inventory"""
    file = get_inv_file(ctx, inv_name)
    if file == "not-allowed":
        await bot.say("You may only modify your own inventory.")
        return

    inventory = load_inv(file)
    inventory.append(Item(title, desc, sell, buy, amt))
    dump(file, inventory)
    await bot.say("Added {0} to the inventory.".format(title))
    # inv_file = ""
    # if dm_check(ctx):
    #     inventory = pickle.load(inv_file) # loads from file
    #     inventory.append(Item(title, desc, sell, buy, amt))
    #     pickle.dump(inventory, inv_file) # dumps datat in file
    #     await bot.say('added {0} to the inventory.'.format(title))
    # else:
    #     await bot.say('You can not add an item to the inventory.')

@bot.command(pass_context=True)
async def rmitem(ctx, title, amt, inv_name=""):
    """removes item(s) from the inventory."""
    file = get_inv_file(ctx, inv_name)
    if file == "not-allowed":
        await bot.say("You may only modify your own inventory.")
        return

    inventory = load_inv(file)

    # if dm_check(ctx):
    #     pickle.load(inv_file)
    #     for x in range(len(inventory)):
    #         if title == inventory[x].title:
    #             for _ in range(amt):
    #                 inventory[x].amount -= 1
    #                 if inventory[x].amount < 1:
    #                     del inventory[x]
    #                     break
    #     pickle.dump(inventory, inv_file)
    #     await bot.say('Removed {0} {1}(s) from the inventory.'.format(amt, title))
    # else:
    #     await bot.say('You can not remove an item from the inventory.')
            

@bot.command(pass_context=True)
async def lsinv(ctx, inv_name=""):
    """lists the inventory."""
    file = get_inv_file(ctx, inv_name, True)
    inventory = load_inv(file)
    string = ''
    for item in inventory:
        string += '''title: {0.title} desc: {0.description}
            sell: {0.sell} buy: {0.buy} amount: {0.amount}\n'''.format(item)
    await bot.say(string)

@bot.command(pass_context=True)
async def roll(ctx, *args):
    """rolls a specified number of dice with a specified number of sides"""
    arguments = {'sides': 20, 'amount': 1, 'adv/dis': 0, 'mods': [], 'secret': False, 'double': False} # Add elven accuracy
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
                else:
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
    elif msgs['rolls'][0] == 1 and arguments['sides'] == 20:
        message = ('rolled a **nat 1**')
    else:
        message = ('rolled {0}').format(msgs['rolls'][0])

    message += ('{0}{1} with {2} for a {3} of **{4}**.').format(
                msgs['adv/dis'],
                msgs['double'],
                msgs['mod'], 
                msgs['min/total'], 
                total)

    log.write()

    if arguments['secret']:
        await bot.send_message(ctx.message.author, 'You {0}'.format(message))
    else:
        await bot.say('{0.message.author.mention} {1}'.format(ctx, message))
        
def dump(file_name, obj):
    create_file(file_name)
    with open(file_name, 'wb') as pickle_file:
        pickle.dump(obj, pickle_file)

def load(file_name):
    create_file(file_name)
    try:
        with open(file_name, 'rb') as pickle_file:
            return pickle.load(pickle_file)
    except EOFError:
        return None

def load_party(ctx):
    file = "party_files/" + ctx.message.channel.server.id + ".bot"
    party = load(file)
    if party == None:
        return []
    else:
        return party

def load_inv(inv_file):
    inv = load(inv_file)
    if inv == None:
        return []
    else:
        return inv

def get_inv_file(ctx, inv_name, allow_party=False):
    if not inv_name == "":
        if not dm_check(ctx):
            return "not-allowed"
        else:
            if inv_name.lower() == "party":
                inv_name = "party"
            else:
                inv_name = inv_name[2:-1]
    elif inv_name == "":
        inv_name = ctx.message.author.id

    return "inv_files/" + ctx.message.channel.server.id + "/" + inv_name + ".inv"

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

    return arr.strip('[').strip(']').replace('\'', '').replace('and,', 'and')

def create_file(to_create):
    if not os.path.exists(to_create[:to_create.rfind('/') + 1]):
        os.makedirs(to_create[:to_create.rfind('/') + 1])
    try:
        open(to_create, 'r')
    except IOError:
        open(to_create, 'w')

def dm_check(ctx):
    try:
        for role in ctx.message.author.roles:
            if dm_role.lower() == role.name.lower():
                return True
        return False
    except Exception as e:
        log.queue_data(e)
    finally:
        log.write()

try:
    file = open('secret.bot', 'r')
    token = file.readline()
    file.close()
    token = token.replace('\n','')
    bot.run(token)
except Exception as error:
    print('Something went wrong ¯\\_(ツ)_/¯')
    print(error)
    print(error.args)
finally:
    print('End of Bot.')

