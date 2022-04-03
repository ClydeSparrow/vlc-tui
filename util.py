import os


SEEK_STEP = 5


def ms_to_hms(ms):
    seconds = ms / 1000
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)

def truncate(string, max_length):
    if len(string) > max_length:
        return string[:max_length] + "…"
    return string

def list_files(path):
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]