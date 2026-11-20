# Pandas project: prenotazioni alberghiere (PMS + CRM)

Progetto del corso *Pandas & Data Manipulation* (Master in AI & Entrepreneurship, Albert School).

Si parte da due file sulle stesse prenotazioni di due hotel, salvati da due sistemi diversi:
- **PMS** (`hotel_reservations_pms.xlsx`), il gestionale dell'hotel;
- **CRM** (`hotel_bookings_crm.csv`).

Pipeline: **Load → Clean di ogni file → Merge → Describe → Analyse**. Il codice deve girare dall'inizio alla fine sui file grezzi, e ogni passo dice cosa fa, perché e quante righe ci sono prima e dopo. Il testo completo della consegna è in `Project/ProjectPresentation.pdf`.

## Struttura

```
.gitignore
requirements.txt
Project/
  ProjectPresentation.pdf          consegna del progetto
  data/
    hotel_reservations_pms.xlsx    PMS grezzo (foglio "bookings"; il foglio "info" è il dizionario delle colonne)
    hotel_bookings_crm.csv         CRM grezzo (separatore ";", virgola decimale)
  cleaning/
    pms_cleaning.ipynb             Fase A del PMS: Load, Assess, Clean
    (notebook del CRM)             Fase A del CRM
```

I dati grezzi in `data/` non si modificano mai: ogni notebook li legge e lavora su una copia.

## Come si esegue

```
python -m venv .venv
.venv\Scripts\activate           # su Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Poi si apre il notebook e si fa **Run All**. I notebook in `Project/cleaning/` leggono i dati con percorsi relativi alla propria cartella, ad esempio `pd.read_excel("../data/hotel_reservations_pms.xlsx", sheet_name="bookings")`.

## Fasi

- **Fase A.** Ogni file si pulisce da solo:
  - PMS: Jacopo, `pms_cleaning.ipynb`.
  - CRM: il compagno di gruppo.
- **Fase B.** Merge dei due file sul codice di prenotazione (`booking_id` nel PMS, `BookingRef` nel CRM), poi controlli di coerenza, Describe e Analyse.

## Regole della pulizia (valgono per entrambi i file)

1. **Prima si misura, poi si decide.** Ogni decisione è preceduta da una cella VERIFICA con i numeri su cui si basa.
2. **Un valore diventa NaN solo se è impossibile già da solo.** Il recupero di un valore dall'altro file si fa nella Fase B, dopo il merge.
3. **Prima di cambiare un valore si crea una colonna flag** (booleana) che segna le righe toccate, così si distinguono i dati originali da quelli modificati o stimati.
4. **Nessun dato inventato.** Un riempimento non provato si chiama STIMA, e la sua riga è segnata dal flag.
5. **Si usano solo funzioni di pandas viste a lezione.**

## Risultato della Fase A del PMS

Il notebook parte da 24.480 righe e arriva a 24.250 righe × 27 colonne:
- tolte 150 copie esatte;
- unite 80 prenotazioni che avevano due versioni: vince la più recente, come conferma il CRM.

Flag creati:

| Flag | Righe | Significato |
|---|---|---|
| `meal_ricodificato` | 236 | `Undefined` ricodificato in `SC` (nessun pasto, come dice l'articolo originale del dataset) |
| `adr_anomalo` | 71 | adr negativo o sopra 1000: messo a NaN, da ricalcolare dal CRM nella Fase B |
| `adr_zero` | 377 | adr = 0, confermato anche dal CRM; da escludere nelle analisi sui prezzi |
| `week_nights_mancante` | 35 | `stays_in_week_nights` = -1, un codice per "non noto": messo a NaN |
| `zero_notti` | 147 | soggiorni di 0 notti, tenuti |
| `senza_ospiti` | 31 | 0 adulti, 0 bambini, 0 neonati, tenuti |
| `children_missing` | 809 | children mancante riempito con 0 (STIMA) |

NaN rimasti: adr 191, `stays_in_week_nights` 35, meal 483.

Le cose da fare nella Fase B sono nell'ultima cella di `pms_cleaning.ipynb`, "Note per la Fase B". In sintesi:
- controllare che le colonne in comune tra i due file tornino;
- ricalcolare adr da `total_price / notti`;
- ricostruire le notti feriali;
- confrontare gli adulti oltre 10 con `n_adults` del CRM.

## Come si collabora (anche per gli assistenti AI)

- I notebook di pulizia vanno in `Project/cleaning/`. Ognuno modifica solo il proprio notebook.
- Non si usa mai `git push --force`. Prima di lavorare si fa `git pull`.
- `personale/` e `DataManipulation-AlbertSchool/` sono nel `.gitignore`: è materiale personale e del corso, e non va nel repo.
- I messaggi di commit sono in italiano, al passivo (es. "Aggiunta la pulizia del CRM").
- Ogni decisione di pulizia la prende chi possiede il notebook. Un assistente AI propone opzioni con i numeri, ma non decide al suo posto.
