import datetime
import random
import pytz
from db.base import DB


async def getProblemset():
    now = (datetime.datetime.now(pytz.UTC) +
           datetime.timedelta(hours=3, minutes=1)).date()
    nowDate = now.strftime('%Y-%m-%d')
    nowDay = now.strftime('%A')
    queries = await DB.queryrule.find_many(where={
        'AND': [
            {'OR': [{'startDate': None}, {'startDate': {'lte': nowDate}}]},
            {'OR': [{'endDate': None}, {'endDate': {'gte': nowDate}}]},
            {f'on{nowDay}': True},
            {'probability': {'gte': random.random()}}
        ]
    },
        order={
        'queryRuleRank'
    })
    return queries
