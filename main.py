import time

from cli import CLI, Option, Color

if __name__ == '__main__':
    cli = CLI('CLI Test', color=Color.BLUE)
    cli.set_exit_message('Uscita pulita')

    name = cli.ask_password('Come ti chiami?')
    cli.print(f'Ciao, {name}!')

    lang = cli.choose('Linguaggio preferito?', [
        Option('PY', 'Python'),
        Option('TS', 'Typescript'),
        Option('RU', 'Rust'),
        Option('GO'),
    ])
    cli.success(f'Ottima scelta: {lang}')

    ok = cli.confirm('Ti è piaciuto questo test?')
    cli.start_spinner('Caricamento in corso...')
    time.sleep(2)
    cli.stop_spinner()
    cli.print('Grazie!' if ok else 'Grazie lo stesso!')
