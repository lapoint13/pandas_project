# Pandas project: hotel bookings (PMS + CRM)

Project for the *Pandas & Data Manipulation* course (Master in AI & Entrepreneurship, Albert School).

We start from two files on the same bookings of two hotels, exported by two different systems:
- **PMS** (`hotel_reservations_pms.xlsx`), the hotel management system;
- **CRM** (`hotel_bookings_crm.csv`).

Brief: **Load → Merge → Describe → Clean → Analyse**. The code must run top to bottom on the raw files, and every step says what it does, why, and how many rows there are before and after. The full brief is in `Project/ProjectPresentation.pdf`.

We started cleaning before the merge was explained in class. As agreed with the professor, each file is cleaned on its own first, and every cleaning step done before the merge must respect two rules: it must not harm the merge, and it must not delete information that the other file can recompute or check. Everything that needs both files is done after the merge.

## Structure

```
.gitignore
requirements.txt
Project/
  ProjectPresentation.pdf          project brief
  data/
    raw/
      hotel_reservations_pms.xlsx  raw PMS (sheet "bookings"; the sheet "info" is the column dictionary)
      hotel_bookings_crm.csv       raw CRM (";" separator, decimal comma)
    processed/
      pms_clean.csv                clean PMS, written by pms_cleaning.ipynb
      crm_clean.csv                clean CRM, written by crm_cleaning.ipynb
  cleaning/
    pms_cleaning.ipynb             Phase A of the PMS: Load, Assess, Clean, Export
    crm_cleaning.ipynb             Phase A of the CRM: Load, Assess, Clean, Export
```

The files in `data/raw/` are never modified: each notebook reads them, works on a copy and saves the result in `data/processed/`.

## How to run

```
python -m venv .venv
.venv\Scripts\activate           # on Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Then open a notebook and use **Run All**. The notebooks in `Project/cleaning/` read the data with paths relative to their own folder, for example `pd.read_excel("../data/raw/hotel_reservations_pms.xlsx", sheet_name="bookings")`. Order: first the two cleaning notebooks, then the merge notebook, which reads the files in `data/processed/`.

## Phases

- **Phase A.** Each file is cleaned on its own:
  - PMS: Jacopo, `pms_cleaning.ipynb`.
  - CRM: Alessandro, `crm_cleaning.ipynb`.
- **Phase B.** Merge of the two files on the booking code (`booking_id` in the PMS, `BookingRef` in the CRM), then consistency checks between the files, Describe and Analyse.

## Cleaning rules (for both files)

1. **Measure first, then decide.** Every decision comes after a CHECK cell with the numbers it is based on.
2. **A value becomes NaN only if it is impossible on its own.** Recovering a value from the other file happens in Phase B, after the merge.
3. **Before the merge, do no harm:** no step may damage the merge key or the shared columns, or delete information that the other file can recompute or check.
4. **Before changing a value we create a flag column** (boolean) marking the rows touched, so original data can be told apart from modified or estimated data.
5. **No invented data.** A fill that is not proven is called an ESTIMATE, and its row is marked by the flag.
6. **Only pandas functions seen in class.**

## Phase A result: PMS

The notebook goes from 24,480 rows to 24,250 rows × 27 columns:
- 150 exact copies removed;
- 80 bookings that had two versions merged: the most recent one wins, as the CRM confirms.

Flags:

| Flag | Rows | Meaning |
|---|---|---|
| `meal_recoded` | 236 | `Undefined` recoded to `SC` (no meal, as the original paper of the dataset says) |
| `adr_invalid` | 71 | adr negative or above 1,000: set to NaN, to be recomputed from the CRM in Phase B |
| `adr_zero` | 377 | adr = 0, confirmed by the CRM too; to be excluded from price analyses |
| `week_nights_missing` | 35 | `stays_in_week_nights` = -1, a code for "unknown": set to NaN |
| `zero_nights` | 147 | 0-night stays, kept |
| `no_guests` | 31 | 0 adults, 0 children, 0 babies, kept |
| `children_missing` | 809 | missing children filled with 0 (ESTIMATE) |

NaN left: adr 191, `stays_in_week_nights` 35, meal 483.

## Phase A result: CRM

The notebook goes from 24,608 rows to 24,500 rows × 25 columns:
- 8 empty rows and 100 exact copies removed;
- spellings fixed in `property`, `market_segment`, `reservation_status` and `guest_country`;
- 3 date formats in `checkin_date` read into real dates;
- `" days"` removed from `lead_time_days`, and the decimal comma in `total_price` changed to a dot.

Flags:

| Flag | Rows | Meaning |
|---|---|---|
| `segment_undefined` | 2 | `market_segment` = `Undefined`, set to NaN |
| `channel_undefined` | 3 | `distribution_channel` = `Undefined`, set to NaN |
| `country_placeholder` | 114 | `unknown` or `-` as country, set to NaN |
| `country_cn_ambiguous` | 228 | `CN`: China (already `CHN`) or Canada (never `CAN`)? Left unchanged |
| `lead_time_missing` | 25 | `lead_time_days` = 9999, a code for "unknown": set to NaN |
| `adults_over_10` | 2 | 26 and 55 adults, both `Group`: unchanged, to compare with the PMS |
| `date_inconsistent` | 88 | status date against check-in: 37 Check-Out before, 50 Canceled after, 1 No-Show before. Dates unchanged |

NaN left: `n_adults` 244, `total_price` 490, `lead_time_days` 25, `guest_country` 114, `market_segment` 2, `distribution_channel` 3 (plus `agent_id` and `company_id`, empty when there is no agent or company).

## To do in Phase B

The details are in the last cell of `pms_cleaning.ipynb`, "Notes for Phase B". In short:
- check that the shared columns of the two files agree;
- recompute adr from `total_price / nights`;
- rebuild the week nights;
- compare adults above 10 with `n_adults` of the CRM;
- decide on the 88 `date_inconsistent` rows using the PMS arrival date;
- check `total_price` = 0 (381 rows) and `n_adults` = 0 (79 rows) against the PMS.

## How we collaborate (also for AI assistants)

- The cleaning notebooks go in `Project/cleaning/`. Each person owns their notebook: changes to the other person's notebook are agreed first.
- Never use `git push --force`. Run `git pull` before working.
- `personale/` and `DataManipulation-AlbertSchool/` are in `.gitignore`: personal and course material, not part of the repo.
- Commit messages are in Italian, in the passive form (e.g. "Aggiunta la pulizia del CRM").
- Every cleaning decision is taken by the owner of the notebook. An AI assistant proposes options with numbers, but does not decide for them.
