
import datetime

import pytz


def nowAsISO():
    now = (datetime.datetime.now(pytz.UTC) +
           datetime.timedelta(hours=3, minutes=1)).date()
    return now.strftime('%Y-%m-%d')