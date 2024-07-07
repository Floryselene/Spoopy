import re
from datetime import timedelta



def convert_duration_to_seconds(duration):
    total_seconds = 0

    components = re.findall(r"(\d+)([ywdDhHmMsS])", duration)

    for value, unit in components:
        value = int(value)

        if unit.lower() == "y":
            total_seconds += int(value * 365 * 86400)  # 1 year = 365 days
        elif unit.lower() == "w":
            total_seconds += value * 7 * 86400  # 1 week = 7 days
        elif unit.lower() == "d":
            total_seconds += value * 86400  # 1 day = 86400 seconds
        elif unit.lower() == "h":
            total_seconds += value * 3600  # 1 hour = 3600 seconds
        elif unit.lower() == "m":
            total_seconds += value * 60  # 1 minute = 60 seconds
        elif unit.lower() == "s":
            total_seconds += value  # seconds

    time = timedelta(seconds=total_seconds)

    # Extract the readable time portion without hours, minutes, and seconds
    days = time.days
    hours, remainder = divmod(time.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days > 0:
        readable_time = f"{days} day{'s' if days != 1 else ''}"
    elif hours > 0:
        readable_time = f"{hours} hour{'s' if hours != 1 else ''}"
    elif minutes > 0:
        readable_time = f"{minutes} minute{'s' if minutes != 1 else ''}"
    else:
        readable_time = f"{seconds} second{'s' if seconds != 1 else ''}"

    return (readable_time, total_seconds)
