from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

class TimeError(ValueError):
    pass

def to_utc(date: str, time: str, tz_name: str) -> datetime:
    naive = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    tz = ZoneInfo(tz_name)

    a = naive.replace(tzinfo=tz, fold=0)
    b = naive.replace(tzinfo=tz, fold=1)
    off_a, off_b = a.utcoffset(), b.utcoffset()

    if off_a != off_b:
        # same local time, two offsets: gap or fold
        utc_a = (a - off_a).replace(tzinfo=timezone.utc)
        back = utc_a.astimezone(tz).replace(tzinfo=None)
        if back != naive:
            raise TimeError("local time does not exist (DST gap). ask user.")
        raise TimeError("local time ambiguous (DST fold). ask user.")

    return (a - off_a).replace(tzinfo=timezone.utc)

# print(to_utc("1995-08-15", "10:30", "Asia/Kolkata"))
# print(to_utc("1943-06-01", "10:30", "Asia/Kolkata"))