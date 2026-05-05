from cli import CLI, Option

if __name__ == '__main__':
    cli = CLI(exit_message='Programma interrotto. Arrivederci!')

    name = cli.ask('Come ti chiami?')
    cli.print(f'Ciao, {name}!')

    lang = cli.choose('Linguaggio preferito?', [
        Option('Python', 'py'),
        Option('TypeScript', 'ts'),
        Option('Rust', 'rs'),
        Option('Go', 'go'),
    ])
    cli.print(f'Ottima scelta: {lang}')

    ok = cli.confirm('Vuoi uscire?', default=False)
    cli.print('Arrivederci!' if ok else 'Continuiamo allora.')
