import hashlib
import locale


# template filter functions
def md5_filter(value):
    return hashlib.md5(str(value).encode()).hexdigest()


def slice3_filter(value):
    return value[:3]


def date_MdY(date):
    return date.strftime("%b %d, %Y")


def date_month(date):
    return date.month


def date_year(date):
    return date.year


def date_day(date):
    return date.day


def format_currency(value):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    return locale.currency(value, grouping=True, symbol=False)


def format_date(date):
    return date.strftime("%d/%m")
