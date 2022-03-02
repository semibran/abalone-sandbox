def format_secs(time):
    mins = int(time / 60)
    secs = int(time % 60)
    ms = int(time % 1 * 100)
    return f"{str(mins).rjust(2, '0')}:{str(secs).rjust(2, '0')}'{str(ms).rjust(2, '0')}\""
