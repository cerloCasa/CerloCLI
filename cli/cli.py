import sys
from typing import Any, Callable

from .colors import Color
from .banner import banner
from ._spinner import _Spinner

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
    def __init__(self, value: Any, label: str = None):
        self.value = value
        self.label = label if label is not None else value

    def __repr__(self) -> str:
        return self.label

    def get(self) -> Any:
        return self.value


class CLI:
    def __init__(self, name: str = None, color: Color = Color.DEFAULT, input=None, output=None):
        """Inizializza l'interfaccia CLI.

        Args:
            name: Nome dell'applicazione. Se fornito, stampa un banner ASCII all'avvio.
            color: Colore del banner. Se non fornito, stampa il banner del colore di default.
            input: Stream di input (default: sys.stdin).
            output: Stream di output (default: sys.stdout).
        """
        self._input = input or sys.stdin
        self._output = output or sys.stdout
        self._exit_message = ''
        if name is not None: self.print(color + banner(name) + Color.DEFAULT)

    def set_exit_message(self, message: str):
        """Imposta il messaggio mostrato all'uscita (Ctrl+C o exit).

        Args:
            message: Testo da stampare prima di terminare il processo.
        """
        self._exit_message = message or ''

    def _exit(self):
        self.print(f'\n{self._exit_message}')
        sys.exit(0)

    def _is_tty(self) -> bool:
        return hasattr(self._output, 'isatty') and self._output.isatty()

    # --- output ---

    def print(self, text: str = ''):
        """Stampa una riga sullo stream di output.

        Args:
            text: Testo da stampare. Se omesso stampa una riga vuota.
        """
        self._output.write(str(text) + '\n')
        self._output.flush()

    def success(self, text: str = ''):
        """Stampa un messaggio di successo in verde.

        Args:
            text: Testo del messaggio.
        """
        self.print(Color.GREEN + text + Color.DEFAULT)

    def warn(self, text: str = ''):
        """Stampa un avviso in giallo.

        Args:
            text: Testo dell'avviso.
        """
        self.print(Color.YELLOW + text + Color.DEFAULT)

    def error(self, text: str = ''):
        """Stampa un errore in rosso.

        Args:
            text: Testo dell'errore.
        """
        self.print(Color.RED + text + Color.DEFAULT)

    def start_spinner(self, message: str = ''):
        """Avvia uno spinner animato in background.

        Lo spinner gira finché non viene chiamato ``stop_spinner()``.
        Durante l'animazione il cursore è nascosto; la riga viene pulita allo stop.

        Args:
            message: Testo mostrato accanto all'animazione.
        """
        self._spinner = _Spinner(message, self._output)
        self._spinner.start()

    def stop_spinner(self):
        """Ferma lo spinner avviato da ``start_spinner()`` e pulisce la riga."""
        if getattr(self, '_spinner', None):
            self._spinner.stop()
            self._spinner = None

    # --- input ---

    def ask(self, prompt: str, validator: Callable[[str], bool] = None, error: str = 'Input non valido.') -> str:
        """Chiede testo libero all'utente.

        Se viene fornito un ``validator``, il prompt viene ripetuto finché
        la funzione non ritorna ``True`` per il valore inserito.
        Ctrl+C termina il processo con il messaggio di uscita configurato.

        Args:
            prompt: Testo mostrato prima del cursore di input.
            validator: Funzione opzionale ``(str) -> bool`` per validare l'input.
            error: Messaggio mostrato quando la validazione fallisce.

        Returns:
            La stringa inserita dall'utente, senza newline finale.
        """
        try:
            while True:
                self._output.write(prompt + ' ')
                self._output.flush()
                value = self._input.readline().rstrip('\n')
                if validator is None or validator(value):
                    return value
                self.print(f'  {error}')
        except KeyboardInterrupt:
            self._exit()

    def ask_password(self, prompt: str) -> str:
        """Chiede una password mostrando asterischi al posto dei caratteri.

        Ogni carattere digitato viene sostituito da ``*`` sullo schermo.
        Il backspace rimuove l'ultimo carattere. Ctrl+C termina il processo.

        Args:
            prompt: Testo mostrato prima del cursore di input.

        Returns:
            La password inserita dall'utente in chiaro.
        """
        try:
            self._output.write(prompt + ' ')
            self._output.flush()
            buf = []

            if sys.platform == 'win32':
                import msvcrt
                while True:
                    ch = msvcrt.getwch()
                    if ch in ('\r', '\n'):
                        self._output.write('\n')
                        self._output.flush()
                        return ''.join(buf)
                    if ch == '\x03':
                        raise KeyboardInterrupt
                    if ch in ('\x08', '\x7f'):
                        if buf:
                            buf.pop()
                            self._output.write('\b \b')
                            self._output.flush()
                    elif ch >= ' ':
                        buf.append(ch)
                        self._output.write('*')
                        self._output.flush()
            else:
                import tty
                import termios
                fd = sys.stdin.fileno()
                old = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    while True:
                        ch = sys.stdin.read(1)
                        if ch in ('\r', '\n'):
                            self._output.write('\n')
                            self._output.flush()
                            return ''.join(buf)
                        if ch == '\x03':
                            raise KeyboardInterrupt
                        if ch in ('\x08', '\x7f'):
                            if buf:
                                buf.pop()
                                self._output.write('\b \b')
                                self._output.flush()
                        elif ch >= ' ':
                            buf.append(ch)
                            self._output.write('*')
                            self._output.flush()
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except KeyboardInterrupt:
            self._exit()

    def confirm(self, prompt: str, default: bool = True) -> bool:
        """Chiede conferma sì/no tramite menu interattivo.

        Presenta due opzioni (Yes / No) navigabili con le frecce.
        L'opzione predefinita viene mostrata per prima.

        Args:
            prompt: Domanda da mostrare all'utente.
            default: Se ``True`` (default) Yes appare prima; se ``False`` appare No.

        Returns:
            ``True`` se l'utente sceglie Yes, ``False`` se sceglie No.
        """
        options = [
            Option('Yes', True),
            Option('No', False)
        ] if default else [
            Option('No', False),
            Option('Yes', False),
        ]
        return self.choose(prompt, options).value

    def choose(self, prompt: str, options: list[Option]) -> Option:
        """Mostra un menu interattivo navigabile con le frecce ↑↓.

        Il menu viene ridisegnato in-place ad ogni pressione di tasto.
        Premere Invio conferma la voce evidenziata. Ctrl+C termina il processo.
        Se l'output non è un TTY (pipe, file, test) ricade automaticamente
        sul fallback numerico ``_choose_numeric``.

        Args:
            prompt: Titolo/domanda mostrata sopra il menu.
            options: Lista di ``Option`` tra cui scegliere (non vuota).

        Returns:
            L'``Option`` selezionata dall'utente.

        Raises:
            ValueError: Se ``options`` è una lista vuota.
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
        except KeyboardInterrupt:
            self._exit()
        finally:
            self._output.write('\033[?25h')  # ripristina il cursore
            self._output.flush()

    def _choose_numeric(self, prompt: str, options: list[Option]) -> Option:
        """Fallback testabile: selezione tramite numero."""
        try:
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
                self.warn(f'Inserisci un numero tra 1 e {len(options)}.')
        except KeyboardInterrupt:
            self._exit()
