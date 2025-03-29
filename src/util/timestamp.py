from datetime import datetime


def leading_zeros(n: int, digits: int) -> str:
    '''
    :param int n: The number to add leading zeros to
    :param int digits: The total number of digits including leading zeros
    :return str: `n` with enough leading zeros to be at least `digits` long
    '''

    n = str(n)
    return (digits - len(n)) * '0' + n


def timestamp(dt: datetime, *, date=True, time=True) -> str:
    '''
    :param str dt: The `datetime.datetime` to be formatted
    :param bool date: Whether or not to include the date
    :param bool time: Whether or not to include the time
    :return str: The `datetime.datetime` formatted to "YYYYMMDDHHMMSS"
    '''

    return (leading_zeros(dt.year, 4) + leading_zeros(dt.month, 2) +
            leading_zeros(dt.day, 2) if date else
            '') + (leading_zeros(dt.hour, 2) + leading_zeros(dt.minute, 2) +
                   leading_zeros(dt.second, 2) if time else '')


del datetime
