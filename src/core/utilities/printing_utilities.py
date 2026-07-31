import sys


def clear_line() -> None:
    sys.stdout.write("\033[F")   # Cursor up one line
    sys.stdout.write("\033[K")   # Clear line
    sys.stdout.flush()
