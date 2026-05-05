from enum import Enum


class Color(str, Enum):
    """Codici colore ANSI per terminale.

    Ogni membro è una stringa, quindi si può concatenare direttamente::

        print(Color.BLUE + "testo" + Color.DEFAULT)
        print(Color.BOLD + Color.RED + "errore!" + Color.DEFAULT)
    """

    # Reset
    DEFAULT = '\033[0m'

    # Stili
    BOLD      = '\033[1m'
    DIM       = '\033[2m'
    UNDERLINE = '\033[4m'

    # Colori standard
    BLACK   = '\033[30m'
    RED     = '\033[31m'
    GREEN   = '\033[32m'
    YELLOW  = '\033[33m'
    BLUE    = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN    = '\033[36m'
    WHITE   = '\033[37m'

    # Colori brillanti
    BRIGHT_BLACK   = '\033[90m'
    BRIGHT_RED     = '\033[91m'
    BRIGHT_GREEN   = '\033[92m'
    BRIGHT_YELLOW  = '\033[93m'
    BRIGHT_BLUE    = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN    = '\033[96m'
    BRIGHT_WHITE   = '\033[97m'
