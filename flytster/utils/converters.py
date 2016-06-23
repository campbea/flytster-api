from datetime import datetime


def utc_string_to_datetime(utc_string):
    """
    utc_string has to be in format: xxxx-xx-xxTxx:xx-xx:xx
    """
    string = ''.join(utc_string.rsplit(':', 1))
    return datetime.strptime(string, '%Y-%m-%dT%H:%M%z')
