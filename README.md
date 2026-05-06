# CerloCLI

Toolkit leggero per costruire applicazioni CLI interattive in Python.
Zero dipendenze esterne, compatibile con Windows, macOS e Linux.

## Funzionalità

- Menu navigabile con le frecce ↑↓
- Ricerca interattiva con filtro in tempo reale
- Prompt testo con validazione
- Input password con asterischi
- Conferma sì/no interattiva
- Spinner animato per operazioni in background
- Output semantico colorato (success, warn, error)
- Banner ASCII colorato all'avvio
- Gestione pulita di Ctrl+C con messaggio personalizzabile

## Installazione

```bash
pip install git+https://github.com/cerloCasa/CerloCLI.git
```

## Utilizzo

```python
from cli import CLI, Option, Color

cli = CLI('MiaApp', color=Color.CYAN)
cli.set_exit_message('A presto!')

# Input testo con validazione opzionale
nome = cli.ask('Come ti chiami?', validator=lambda s: len(s) > 0, error='Il nome non può essere vuoto.')

# Input password mascherato con asterischi
pwd = cli.ask_password('Password:')

# Menu interattivo
lingua = cli.choose('Linguaggio preferito?', [
    Option('py', 'Python'),
    Option('ts', 'TypeScript'),
    Option('rs', 'Rust'),
])

# Ricerca interattiva tra molte opzioni
città = cli.search('Da quale città vieni?', [
    Option('MI', 'Milano'),
    Option('RM', 'Roma'),
    Option('NA', 'Napoli'),
    # ...altre opzioni...
], visible=4)

# Conferma sì/no
ok = cli.confirm('Vuoi continuare?', default=True)

# Spinner per operazioni lunghe
cli.start_spinner('Caricamento...')
# ... operazione lunga ...
cli.stop_spinner()

# Output semantico
cli.success('Operazione completata.')
cli.warn('Configurazione mancante.')
cli.error('Connessione fallita.')

# Output colorato libero
cli.print(Color.BLUE + 'testo blu' + Color.DEFAULT)
```

## API

### `CLI(name, color, input, output)`

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `name` | `str` | `None` | Nome dell'app — stampa un banner ASCII all'avvio |
| `color` | `Color` | `Color.DEFAULT` | Colore del banner |
| `input` | stream | `sys.stdin` | Stream di input |
| `output` | stream | `sys.stdout` | Stream di output |

### Metodi

| Metodo | Descrizione |
|--------|-------------|
| `print(text)` | Stampa una riga sullo stream di output |
| `success(text)` | Stampa in verde |
| `warn(text)` | Stampa in giallo |
| `error(text)` | Stampa in rosso |
| `ask(prompt, validator, error)` | Chiede testo libero, con validazione opzionale |
| `ask_password(prompt)` | Chiede una password mostrando asterischi |
| `confirm(prompt, default)` | Menu sì/no, ritorna `bool` |
| `choose(prompt, options)` | Menu a frecce, ritorna l'`Option` selezionata |
| `search(prompt, options, visible)` | Ricerca con filtro live, ritorna l'`Option` selezionata |
| `start_spinner(message)` | Avvia uno spinner animato in background |
| `stop_spinner()` | Ferma lo spinner e pulisce la riga |
| `set_exit_message(message)` | Imposta il messaggio mostrato all'uscita |

### `Option(value, label=None)`

Voce di un menu. `value` è il dato restituito da `choose()`; `label` è il testo mostrato all'utente (se omessa coincide con `value`). Usa `.get()` per accedere al valore.

### `Color`

Enum `str` con codici ANSI. Concatenabile direttamente con le stringhe:

```python
Color.BOLD + Color.RED + 'errore' + Color.DEFAULT
```

| Gruppo | Membri |
|--------|--------|
| Reset | `DEFAULT` |
| Stili | `BOLD`, `DIM`, `UNDERLINE` |
| Colori | `BLACK`, `RED`, `GREEN`, `YELLOW`, `BLUE`, `MAGENTA`, `CYAN`, `WHITE` |
| Brillanti | `BRIGHT_RED`, `BRIGHT_GREEN`, `BRIGHT_YELLOW`, `BRIGHT_BLUE`, `BRIGHT_MAGENTA`, `BRIGHT_CYAN`, `BRIGHT_WHITE` |
