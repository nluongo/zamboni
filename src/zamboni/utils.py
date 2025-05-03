from datetime import date

def get_today_date():
    '''
    Get today's date
    '''
    out = date.today()
    return out

def get_tomorrow_date():
    '''
    Get tomorrow's date
    '''
    out = get_today_date()
    out = out.replace(day=out.day + 1)
    return out

def get_yesterday_date():
    '''
    Get yesterday's date
    '''
    out = get_today_date()
    out = out.replace(day=out.day - 1)
    return out

def today_date_str():
    '''
    Get today's date as string
    '''
    out = str(get_today_date())
    return out
    
def split_csv_line(line):
    '''
    Split line from text file into list
    '''
    split_line = line.split(',')
    split_line = [entry.strip() for entry in split_line]
    return split_line
