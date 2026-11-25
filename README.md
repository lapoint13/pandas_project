# Pandas project: hotel bookings (PMS + CRM)

Project for the *Pandas & Data Manipulation* course (Master in AI & Entrepreneurship, Albert School), by Jacopo Saporetti and Alessandro Fioretti.

The final presentation is `Project/Final_Presentation.pdf`.

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
  Final_Presentation.pdf           our final presentation (12 slides)
  run_all.py                       runs the whole pipeline: the five notebooks below, in order
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
  describe/
    describe.ipynb                 Describe: profile and quality report of the final table (changes nothing)
  analysis/
    analysis.ipynb                 Analyse: 7 questions, findings and charts before & after (changes nothing)
```

The files in `data/raw/` are never modified: each notebook reads them, works on a copy and saves the result in `data/processed/`.

## How to run

```
git clone https://github.com/lapoint13/pandas_project.git
cd pandas_project
python -m venv .venv
.venv\Scripts\activate           # on Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Tested with Python 3.12. To run the whole pipeline in one go, from raw files to clean tables, use `cd Project` and then `python run_all.py` (about 10 seconds; add `--verbose` to see every notebook's output). It runs the five notebooks below in order, each in its own folder and with a fresh state, without modifying them.

To run one step at a time, open a notebook and use **Restart & Run All**: some cells create a flag and then change the values it marks, so a cell run a second time on its own resets its flag. Every notebook reads the data with paths relative to its own folder, for example `pd.read_excel("../data/raw/hotel_reservations_pms.xlsx", sheet_name="bookings")`. Order:
1. `cleaning/pms_cleaning.ipynb` and `cleaning/crm_cleaning.ipynb` (any order);
2. `merge/merge.ipynb`, which reads the two files in `data/processed/`;
3. `describe/describe.ipynb` and `analysis/analysis.ipynb` (any order), which read `merged_clean.csv`. The analysis also reads the raw files, for the "before" of each chart.

To work on the final table, read it with its dates:

```python
df = pd.read_csv("../data/processed/merged_clean.csv",
                 parse_dates=["arrival_date", "reservation_status_date", "record_updated_at"])
```

## Phases

- **Phase A.** Each file is cleaned on its own:
  - PMS: Jacopo, `pms_cleaning.ipynb`.
  - CRM: Alessandro, `crm_cleaning.ipynb`.
- **Phase B.** Merge of the two files on the booking code (`booking_id` in the PMS, `BookingRef` in the CRM), then consistency checks between the files and recomputed values: `merge.ipynb`.
- **Describe.** Profile and quality report of the final table: where the rows come from, missing values (structural or real gaps), main numbers and categories, and how many rows each cleaning step touched (88.1% of the bookings have no cleaning flag): `describe.ipynb`.
- **Analyse.** Seven questions, each with a chart before and after the cleaning, a CHECK cell and the finding: price per night, cancellations, deposit type, lead time, market segments, months, special requests: `analysis.ipynb`. Key finding: the 2,924 `Non Refund` bookings are cancelled in 99.5% of cases, so every cancellation rate is also shown without them.

## Cleaning rules (for both files)

1. **Measure first, then decide.** Every decision comes after a CHECK cell with the numbers it is based on.
2. **A value becomes NaN only if it is impossible on its own.** Recovering a value from the other file happens in Phase B, after the merge.
3. **Before the merge, do no harm:** no step may damage the merge key or the shared columns, or delete information that the other file can recompute or check.
4. **Before changing a value we create a flag column** (boolean) marking the rows touched, so original data can be told apart from modified or estimated data. Format fixes (spaces, case, spelling, units) keep the same information and get no flag. Some flags only mark rows to watch (e.g. `adr_zero`, `no_guests`) and change no value.
5. **No invented data.** A fill that is not proven is called an ESTIMATE, and its row is marked by the flag.
6. **Pandas functions seen in class where possible.** A few standard ones not shown in class are used where the course has no equivalent, e.g. `pd.to_timedelta` for date arithmetic, `rename`, `set_index` and `to_dict`. The analysis also uses `.plot` for the charts, `pd.cut` for the lead time classes and `str.zfill` for the month labels.

## Phase A result: PMS

The notebook goes from 24,480 rows to 24,250 rows × 29 columns:
- 150 exact copies removed;
- 80 bookings that had two versions merged: the most recent one wins. The CRM agrees with the newer version in 76 of the 77 testable pairs, and never with the older one. 3 gaps of the newer version are filled from the older one (`combine_first`).

Flags:

| Flag | Rows | Meaning |
|---|---|---|
| `meal_undefined` | 236 | `Undefined` is not a meal plan of the `info` dictionary: set to NaN (same rule as `Undefined` in the CRM). All in the Resort Hotel |
| `filled_from_old_version` | 3 | gaps of the newer version filled from the older one (2 `meal`, 1 `children`) |
| `adr_invalid` | 70 | adr negative or above 1,000: set to NaN, to be recomputed from the CRM in Phase B (65 have a CRM price and are recomputed; 5 stay NaN) |
| `adr_outlier` | 1 | adr above 1,000 that the CRM also shows (BK323523, 5,400 euro for 1 night): kept as an unverified extreme, because agreement between the files is consistency, not proof. Excluded from price analyses |
| `adr_zero` | 377 | adr = 0; the CRM price is 0 too in all 362 rows that have one (15 have none). Excluded from price analyses |
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

1. **Shared columns in one column.** The PMS is the reference; the CRM fills it where the PMS is missing: `hotel` ← `property`, `arrival_date` ← `checkin_date` (the PMS year, month and day columns are filled from it too), `adults` ← `n_adults`, `is_canceled` ← `reservation_status`.
2. **Conflicts between the files.** A value is changed only when a third column (usually the price) proves which file is right; otherwise it is kept and flagged.
3. **Recomputed values** with `total_price = adr × nights`, which holds on 22,436 of the 22,708 testable rows (adr, nights and price known, adr and nights above zero).
4. **Other checks** that change no value: weekend nights, repeated guests, repeated status dates, bookings identical except the code (see "Known limits").
5. **Export** to `data/processed/merged_clean.csv`: 25,000 rows × 68 columns. `property` and `checkin_date` are dropped as duplicates; `n_adults` stays, because of the unresolved adults conflicts.

Flags:

| Flag | Rows | Meaning |
|---|---|---|
| `arrival_conflict` | 45 | different arrival date; the CRM dates confirm the PMS in every testable row. PMS kept |
| `adults_from_crm` | 19 | PMS above 10 adults (20-55), CRM 1-2, a price for 1-2 people: CRM value taken |
| `adults_conflict` | 56 | one adult of difference, no evidence either way: PMS kept, CRM in `n_adults` |
| `adults_unverified` | 2 | more than 10 adults in the PMS, no CRM value to check. adr > 0 (the profile of the 19 errors): set to NaN (1 row); adr 0 (the profile of the real groups): kept (1 row) |
| `status_from_pms` | 50 | `Canceled` in the CRM but status date = departure day: changed to `Check-Out` |
| `nights_conflict` | 35 | CRM dates disagree with the PMS nights; the price confirms the PMS in 31 of the 32 testable rows (the other one has an inflated CRM price, see `price_inflated`). PMS kept |
| `status_date_from_pms` | 35 | the same rows: the CRM status date (often before the arrival, even before the booking) becomes arrival + nights |
| `price_inflated` | 273 | CRM price always 15-60% higher than adr × nights, while the PMS adr matches the typical price of the room: price recomputed. 272 found in 6.1, plus 1 once the week nights are rebuilt in 6.2 |
| `week_nights_from_crm` | 18 | week nights rebuilt from the CRM dates (check-outs) |
| `week_nights_estimated` | 15 | week nights rebuilt from `total_price / adr` (ESTIMATE) |
| `adr_from_crm` | 177 | missing adr recomputed as `total_price / nights`. Without an adr, these CRM prices could not be tested in 6.1: at the 6.1 rate (1.2%) about 2 could be inflated (ESTIMATE) |
| `adr_estimated` | 3 | missing adr of 0-night stays set to 0 (ESTIMATE) |
| `price_from_pms` | 466 | missing `total_price` recomputed as adr × nights |
| `repeated_inconsistent` | 266 | `is_repeated_guest` contradicts the history (not repeated with past stays, or repeated with no history). Values unchanged |

Still missing on PMS rows: adr 10 and `stays_in_week_nights` 2 (no source in either file), adults 1 (BK305879, set to NaN by `adults_unverified`), and, as in Phase A, meal 719 and children 809.

Using the final table:
- **Price analyses:** filter on `adr > 0` and nights above zero, not on the Phase A flags. After Phase B there are 381 rows with adr 0 (`adr_zero` marks 377; the other 4 come from `adr_estimated` and `adr_from_crm`) and 148 stays of 0 nights (`zero_nights` marks 147). Exclude `adr_outlier` too.
- **Per-person analyses:** filter on `adults > 0` (38 bookings have 0 adults and some children).
- **`date_inconsistent`** describes the raw CRM: 87 of its 88 rows are resolved in Phase B (`merge.ipynb`, 5.5), and only BK318605 is still inconsistent. Do not use it as a filter.
- **`agent_id` and `company_id`** are codes saved as numbers: count them, never average them.

Known limits:
- **Weekend nights.** `stays_in_weekend_nights` matches the nights of Saturday and Sunday in only 12,078 of 24,248 rows, but the nights starting on Sunday and Monday in all of them: the dates and the weekend count are one day apart. No column shows which is right, so nothing is changed and the analysis draws no conclusions by day of the week.
- **Repeated status dates.** The 151 rows on 2015-01-01 are one block of cancelled Groups bookings, all booked on the same day: not a code for "unknown". Other frequent dates are days with many cancellations, not always one block (2015-10-21: 280 of 298 cancelled, booked on 16 different days).
- **Bookings identical except the code.** 87 rows are equal to an earlier row in every column except `booking_id` (169 rows in groups of 2-3). Almost all are cancelled Groups or Offline TA/TO bookings: most likely group blocks, so they are kept (`merge.ipynb`, 7.4).
- **CRM prices that could not be tested.** The 6.1 check needs the PMS adr and nights. The 177 `adr_from_crm` prices (about 2 inflated, ESTIMATE) and the prices of the 729 CRM-only rows that have one (about 9, ESTIMATE) could not be tested.
