import threading

_FRAMES = ('⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠣', '⠏')


class _Spinner:
    def __init__(self, message: str, output):
        self._message = message
        self._output = output
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._output.write('\033[?25l')  # nasconde il cursore
        self._output.flush()
        self._thread.start()

    def stop(self):
        self._stop.set()
        self._thread.join()
        self._output.write('\r\033[2K')  # cancella la riga
        self._output.write('\033[?25h')  # ripristina il cursore
        self._output.flush()

    def _run(self):
        i = 0
        while not self._stop.wait(0.08):
            frame = _FRAMES[i % len(_FRAMES)]
            self._output.write(f'\r{frame} {self._message}')
            self._output.flush()
            i += 1
