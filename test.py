from datetime import datetime
def now():
    return datetime.now()

print(now().strftime('%Y%m%d%H%M'))  # Print current date and time in the format YYYY-MM-DD HH:MM:SS
