import datetime as dt


def yyyymmdd_from_timestamp(ts):
    return int(ts.strftime("%Y%m%d"))


def now(yyyymmdd: bool = True, offset_days: int = 0):
    now = dt.datetime.now() + dt.timedelta(days=offset_days)
    if yyyymmdd:
        now = yyyymmdd_from_timestamp(now)
    return now
