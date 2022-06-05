import datetime
import calendar


def get_last_of_month(date):
    return datetime.date(date.year, date.month, calendar.monthrange(date.year, date.month)[-1])

def get_first_of_month(date):
    return datetime.date(date.year, date.month, 1)
