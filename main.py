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

    city = cli.search('Da quale città vieni?', [
        Option('MI', 'Milano'), Option('RM', 'Roma'), Option('NA', 'Napoli'),
        Option('TO', 'Torino'), Option('BO', 'Bologna'), Option('FI', 'Firenze'),
        Option('VE', 'Venezia'), Option('GE', 'Genova'), Option('PA', 'Palermo'),
        Option('BA', 'Bari'), Option('CT', 'Catania'), Option('TR', 'Trento'),
    ], visible=4)
    cli.print(f'Città: {city}')

    ok = cli.confirm('Ti è piaciuto questo test?')
    cli.start_spinner('Caricamento in corso...')
    time.sleep(2)
    cli.stop_spinner()
    cli.print('Grazie!' if ok else 'Grazie lo stesso!')
