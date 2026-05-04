import sys
from typing import Any, Callable

# Abilita sequenze ANSI su Windows (richiesto su cmd.exe, no-op su Windows Terminal)
if sys.platform == 'win32':
    import ctypes
    try:
        _k32 = ctypes.windll.kernel32
        _k32.SetConsoleMode(_k32.GetStdHandle(-11), 7)
    except Exception: pass


def _read_key() -> str:
    """Legge un singolo tasto senza attendere Enter. Ritorna 'UP', 'DOWN', 'ENTER' o il char."""
    if sys.platform == 'win32':
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ('\xe0', '\x00'):
            ch2 = msvcrt.getwch()
            return {'H': 'UP', 'P': 'DOWN', 'K': 'LEFT', 'M': 'RIGHT'}.get(ch2, '')
        if ch == '\r':
            return 'ENTER'
        if ch == '\x03':
            raise KeyboardInterrupt
        return ch
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    return {'A': 'UP', 'B': 'DOWN', 'C': 'RIGHT', 'D': 'LEFT'}.get(ch3, '')
            if ch in ('\r', '\n'):
                return 'ENTER'
            if ch == '\x03':
                raise KeyboardInterrupt
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


class Option:
    def __init__(self, label: str, value: Any = None):
        self.label = label
        self.value = value if value is not None else label

    def __repr__(self):
        return self.label


class CLI:
    def __init__(self, input=None, output=None):
        self._input = input or sys.stdin
        self._output = output or sys.stdout

    def _is_tty(self) -> bool:
        return hasattr(self._output, 'isatty') and self._output.isatty()

    # --- output ---

    def print(self, text: str = ''):
        self._output.write(str(text) + '\n')
        self._output.flush()

    # --- input ---

    def ask(self, prompt: str, validator: Callable[[str], bool] = None, error: str = 'Input non valido.') -> str:
        """Chiede testo libero. Se fornito un validator, ripete finché non è valido."""
        while True:
            self._output.write(prompt + ' ')
            self._output.flush()
            value = self._input.readline().rstrip('\n')
            if validator is None or validator(value):
                return value
            self.print(f'  {error}')

    def confirm(self, prompt: str, default: bool = True) -> bool:
        """Chiede sì/no. Ritorna bool."""
        options = [
            Option('Yes', True),
            Option('No', False)
        ] if default else [
            Option('No', False),
            Option('Yes', False),
        ]
        return self.choose(prompt, options).value

    def choose(self, prompt: str, options: list[Option]) -> Option:
        """
        Mostra un menu navigabile con le frecce ↑↓. Invio conferma la scelta.
        Se l'output non è un TTY cade automaticamente sul fallback numerico.
        """
        if not options:
            raise ValueError('La lista di opzioni non può essere vuota.')

        if not self._is_tty():
            return self._choose_numeric(prompt, options)

        selected = 0

        def render(first: bool = False):
            if not first:
                # Torna su di N righe per ridisegnare il menu in-place
                self._output.write(f'\033[{len(options)}A')
            for i, opt in enumerate(options):
                if i == selected:
                    line = f'\r\033[2K  \033[1;7m {opt.label} \033[0m\n'
                else:
                    line = f'\r\033[2K    {opt.label}\n'
                self._output.write(line)
            self._output.flush()

        self._output.write('\033[?25l')  # nasconde il cursore durante la navigazione
        try:
            self.print(prompt)
            render(first=True)
            while True:
                key = _read_key()
                if key == 'UP':
                    selected = (selected - 1) % len(options)
                    render()
                elif key == 'DOWN':
                    selected = (selected + 1) % len(options)
                    render()
                elif key == 'ENTER':
                    return options[selected]
        finally:
            self._output.write('\033[?25h')  # ripristina il cursore
            self._output.flush()

    def _choose_numeric(self, prompt: str, options: list[Option]) -> Option:
        """Fallback testabile: selezione tramite numero."""
        self.print(prompt)
        for i, opt in enumerate(options, 1):
            self.print(f'  {i}. {opt.label}')
        while True:
            self._output.write(f'Scelta [1-{len(options)}]: ')
            self._output.flush()
            raw = self._input.readline().rstrip('\n').strip()
            if raw.isdigit():
                idx = int(raw) - 1
                if 0 <= idx < len(options):
                    return options[idx]
            self.print(f'  Inserisci un numero tra 1 e {len(options)}.')
