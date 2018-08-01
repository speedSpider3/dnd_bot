import discord
#import asyncio

bot = discord.Client()


try:
    file = open('secret.bot', 'r')
    token = file.readline()
    file.close()
    bot.run(token)
except Exception:
    print('Something went wrong ¯\_(ツ)_/¯')
finally:
    print('End of Bot.')

