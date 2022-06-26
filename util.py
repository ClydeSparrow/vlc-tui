import subprocess

SEEK_STEP = 5
TRIGGER_WAS_PLAYED = 60 * 2 + 30    # Update media to mark played when less than 2m30s left
SUPPORTED_EXTS = [
    '.mp4',
]


def ms_to_hms(ms):
    seconds = ms / 1_000
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


def truncate(string, max_length):
    if len(string) > max_length:
        return string[:max_length] + "…"
    return string


def get_media_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             check=True)
    return float(result.stdout) * 1_000
