import dateutil.parser


def ordinal(value):
    try:
        value = int(value)
    except ValueError:
        return value

    if value % 100 // 10 != 1:
        if value % 10 == 1:
            ordval = u"%d%s" % (value, "st")
        elif value % 10 == 2:
            ordval = u"%d%s" % (value, "nd")
        elif value % 10 == 3:
            ordval = u"%d%s" % (value, "rd")
        else:
            ordval = u"%d%s" % (value, "th")
    else:
        ordval = u"%d%s" % (value, "th")

    return ordval


def parse_iso8601(s):
    return dateutil.parser.parse(s)


def format_es_date(s):
    dt = parse_iso8601(s)
    day = ordinal(dt.day)
    month = dt.strftime('%b')
    year = dt.year
    return u"%s %s, %s" % (month, day, year)
