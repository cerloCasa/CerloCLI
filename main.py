from cli import CLI, Option, Color

if __name__ == '__main__':
    cli = CLI('CLI Test', color=Color.BLUE)
    cli.set_exit_message('Uscita pulita')

    name = cli.ask('Come ti chiami?')
    cli.print(f'Ciao, {name}!')

    lang = cli.choose('Linguaggio preferito?', [
        Option('Python', 'py'),
        Option('TypeScript', 'ts'),
        Option('Rust', 'rs'),
        Option('Go', 'go'),
    ])
    cli.success(f'Ottima scelta: {lang}')

    ok = cli.confirm('Vuoi uscire?', default=False)
    cli.print('Arrivederci!' if ok else 'Continuiamo allora.')
