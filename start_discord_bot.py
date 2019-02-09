import discord
import asyncio
import logging

from cigarCrawler.settings import MONGO_URI
from cigarCrawler.settings import DISCORD_TOKEN

from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)


class MongoDB(object):

    collection_name = 'cigar_items'

    def __init__(self, mongo_uri, mongo_db):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[mongo_db]

    def getDB(self):
        db = self.db[self.collection_name]

        return db

    def getCigarAmountsPerPage(self):
        cigars = self.db[self.collection_name].aggregate([
            {
                '$group': {
                    '_id': {'$toLower': '$website'},
                    'count': {'$sum': 1}
                }
            },
            {'$group': {
                '_id': None,
                'counts': {
                    '$push': {'k': '$_id', 'v': '$count'}
                }
            }},
            {
                '$replaceRoot': {
                    'newRoot': {'$arrayToObject': '$counts'}
                }
            }
        ])

        return cigars


class MyClient(discord.Client):

    mongoDb = MongoDB(MONGO_URI, 'cigars')

    async def on_ready(self):
        logging.info('Logged in as')
        logging.info(self.user.name)
        logging.info(self.user.id)
        logging.info('------')

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content.startswith('!test'):
            counter = 0
            tmp = await message.channel.send('Calculating messages...')
            async for msg in message.channel.history(limit=100):
                if msg.author == message.author:
                    counter += 1

            await tmp.edit(content='You have {} messages.'.format(counter))

        elif message.content.startswith('!sleep'):
            with message.channel.typing():
                await asyncio.sleep(5.0)
                await message.channel.send('Done sleeping.')

        elif message.content.startswith('!search'):
            try:
                search_text = message.content.split('!search')[1].strip()
                with message.channel.typing():
                    logging.info("Searching for [" + search_text + "]")
                    embed = discord.Embed(
                        title='Search result for [' + search_text + ']', footer="There are x result", color=0x00aa00, author="NuTeeE")

                    savedCigars = []
                    for cigar in list(self.mongoDb.getDB().aggregate(
                        [
                            {'$match': {'$text': {'$search': search_text}}},
                            {'$addFields': {'score': {'$meta': 'textScore'}}},
                            {'$match': {'score': {'$gt': 50*len(search_text.split(' '))}}},
                            # {'$match': {'website': {'$eq': 'DanPipe'}}},
                            {'$sort': {'score': -1, 'pricePerStick': 1}},
                            {'$limit': 15}
                        ]
                    )):
                        if cigar['amount'] is 1:
                            field_string = 'Price / Stick: [{0:,.0f} €] [{1:,.0f} Ft]\nURL: [{5}]\nSearch Score: [{6:.5f}]'
                        else:
                            field_string = 'Price / Stick: [{0:,.0f} €] [{1:,.0f} Ft]\nAmount: [{2}]\nActual price: [{3:,.0f} €] [{4:,.0f} Ft]\nURL: [{5}]\nSearch score: [{6:.5f}]'

                        updated = False
                        for savedCigar in savedCigars:
                            if cigar['name'] == savedCigar['name']:
                                updated = True
                                if float(cigar['pricePerStick']) < float(savedCigar['pricePerStick']):
                                    savedCigars.append(cigar)
                                    embed.set_field_at(index=savedCigars.index(savedCigar), name=cigar['name'], value=field_string.format(
                                        cigar['pricePerStick'], cigar['pricePerStickHuf'], cigar['amount'], cigar['price'], cigar['amount'] * cigar['pricePerStickHuf'], cigar['url'], cigar['score']))

                        if not updated:
                            savedCigars.append(cigar)
                            embed.add_field(name=cigar['name'], value=field_string.format(
                                cigar['pricePerStick'], cigar['pricePerStickHuf'], cigar['amount'], cigar['price'], cigar['amount'] * cigar['pricePerStickHuf'], cigar['url'], cigar['score']))

                        # logging.info(embed.fields)

                    await message.channel.send(embed=embed)
            except Exception as e:
                logging.error(e)


client = MyClient()
client.run(DISCORD_TOKEN)
