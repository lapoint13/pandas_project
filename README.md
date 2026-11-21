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
      merged_clean.csv             merged and checked table, written by merge.ipynb
  cleaning/
    pms_cleaning.ipynb             Phase A of the PMS: Load, Assess, Clean, Export
    crm_cleaning.ipynb             Phase A of the CRM: Load, Assess, Clean, Export
  merge/
    merge.ipynb                    Phase B: Merge, checks between the files, recomputed values, Export
```

The files in `data/raw/` are never modified: each notebook reads them, works on a copy and saves the result in `data/processed/`.

## How to run

```
python -m venv .venv
.venv\Scripts\activate           # on Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Then open a notebook and use **Run All**. Every notebook reads the data with paths relative to its own folder, for example `pd.read_excel("../data/raw/hotel_reservations_pms.xlsx", sheet_name="bookings")`. Order:
1. `cleaning/pms_cleaning.ipynb` and `cleaning/crm_cleaning.ipynb` (any order);
2. `merge/merge.ipynb`, which reads the two files in `data/processed/`.

## Phases

- **Phase A.** Each file is cleaned on its own:
  - PMS: Jacopo, `pms_cleaning.ipynb`.
  - CRM: Alessandro, `crm_cleaning.ipynb`.
- **Phase B.** Merge of the two files on the booking code (`booking_id` in the PMS, `BookingRef` in the CRM), then consistency checks between the files and recomputed values: `merge.ipynb`. Describe and Analyse come next.

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
| `meal_undefined` | 236 | `Undefined` is not a meal plan of the `info` dictionary: set to NaN (same rule as `Undefined` in the CRM). All in the Resort Hotel |
| `adr_invalid` | 70 | adr negative or above 1,000: set to NaN, to be recomputed from the CRM in Phase B |
| `adr_outlier` | 1 | adr above 1,000 confirmed by the CRM (BK323523, 5,400 euro for 1 night): kept, to be excluded from price analyses |
| `adr_zero` | 377 | adr = 0, confirmed by the CRM too; to be excluded from price analyses |
| `week_nights_missing` | 35 | `stays_in_week_nights` = -1, a code for "unknown": set to NaN |
| `zero_nights` | 147 | 0-night stays, kept |
| `no_guests` | 31 | 0 adults, 0 children, 0 babies, kept |
| `children_missing` | 809 | children missing, all in the City Hotel: left NaN. No other column or file can check a fill, and the mode (0) would remove every child from these rows |

NaN left: adr 190, `stays_in_week_nights` 35, meal 719 (483 missing + 236 `Undefined`), children 809.

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

## Phase B result: merge

`pd.merge(pms, crm, on="booking_id", how="outer")`: **25,000 rows** (23,750 in both files, 500 only in the PMS, 750 only in the CRM). The columns `in_pms` and `in_crm` say where each row comes from.

1. **Shared columns in one column.** The PMS is the reference; the CRM fills it where the PMS is missing: `hotel` ← `property`, `arrival_date` ← `checkin_date`, `adults` ← `n_adults`, `is_canceled` ← `reservation_status`.
2. **Conflicts between the files.** A value is changed only when a third column (usually the price) proves which file is right; otherwise it is kept and flagged.
3. **Recomputed values** with `total_price = adr × nights`, which holds on 22,436 of 22,708 checkable rows.
4. **Export** to `data/processed/merged_clean.csv`: 25,000 rows × 65 columns. `property` and `checkin_date` are dropped as duplicates; `n_adults` stays, because of the unresolved adults conflicts.

Flags:

| Flag | Rows | Meaning |
|---|---|---|
| `arrival_conflict` | 45 | different arrival date; the CRM dates confirm the PMS in every testable row. PMS kept |
| `adults_from_crm` | 19 | PMS above 10 adults (20-55), CRM 1-2, price of 1-2 people: CRM value taken |
| `adults_conflict` | 56 | one adult of difference, no evidence either way: PMS kept, CRM in `n_adults` |
| `adults_unverified` | 2 | more than 10 adults in the PMS, no CRM value to check |
| `status_from_pms` | 50 | `Canceled` in the CRM but status date = departure day: changed to `Check-Out` |
| `nights_conflict` | 35 | CRM dates disagree with the PMS nights; the price confirms the PMS. PMS kept |
| `price_inflated` | 272 | CRM price always 15-60% higher than adr × nights, while the PMS adr matches the typical price of the room: price recomputed |
| `week_nights_from_crm` | 18 | week nights rebuilt from the CRM dates (check-outs) |
| `week_nights_estimated` | 15 | week nights rebuilt from `total_price / adr` (ESTIMATE) |
| `adr_from_crm` | 177 | missing adr recomputed as `total_price / nights` |
| `adr_estimated` | 3 | missing adr of 0-night stays set to 0 (ESTIMATE) |
| `price_from_pms` | 466 | missing `total_price` recomputed as adr × nights |

Still missing on PMS rows: adr 10, `stays_in_week_nights` 2 (no source in either file).

## How we collaborate (also for AI assistants)

- The cleaning notebooks go in `Project/cleaning/`. Each person owns their notebook: changes to the other person's notebook are agreed first.
- Never use `git push --force`. Run `git pull` before working.
- `personale/` and `DataManipulation-AlbertSchool/` are in `.gitignore`: personal and course material, not part of the repo.
- Commit messages are in Italian, in the passive form (e.g. "Aggiunta la pulizia del CRM").
- Every cleaning decision is taken by the owner of the notebook. An AI assistant proposes options with numbers, but does not decide for them.
