from datetime import date


def zero_pad(to_pad, length, padder="0"):
    padded_value = padder * (length - len(str(to_pad))) + str(to_pad)
    return padded_value


def zero_pad_date(year, month, day):
    year_str = zero_pad(year, 4)
    month_str = zero_pad(month, 2)
    day_str = zero_pad(day, 2)
    return f"{year_str}-{month_str}-{day_str}"


def get_today_date():
    """
    Get today's date
    """
    out = date.today()
    return out


def get_tomorrow_date():
    """
    Get tomorrow's date
    """
    out = get_today_date()
    out = out.replace(day=out.day + 1)
    return out


def get_yesterday_date():
    """
    Get yesterday's date
    """
    out = get_today_date()
    out = out.replace(day=out.day - 1)
    return out


def today_date_str():
    """
    Get today's date as string
    """
    out = str(get_today_date())
    return out


def split_csv_line(line):
    """
    Split line from text file into list
    """
    split_line = line.split(",")
    split_line = [entry.strip() for entry in split_line]
    return split_line


def confidence_from_prediction(prediction):
    """
    Get confidence from prediction
    """
    if prediction >= 0.5:
        confidence = prediction
    else:
        confidence = 1 - prediction
    return confidence
