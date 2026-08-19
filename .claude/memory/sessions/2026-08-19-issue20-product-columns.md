# 2026-08-19 · Issue #20 — four optional columns on taskmaster_products

## What was asked
Product Underlying (single-line text, ticker or list of tickers, uppercased on write —
"a choice column with custom on-the-fly additions would be optimal"), Product Wrapper
(single-line text), Product Maturity (numeric), Product Features (multi-line). None required.
Both the edit form and the product list.

## Two decisions taken to the user BEFORE writing the schema
Internal names freeze at creation, so neither could be assumed.

**Underlying → plain Text with an EMERGENT pick list.** Three options were put up: plain Text
with suggestions, a governed `mapping_underlyings` list with on-the-fly create, and a real
SharePoint fill-in Choice. The user chose the first. The fill-in Choice was argued against and
should stay rejected: `Choices()` returns only the DEFINED values, so the app cannot offer the
fill-ins back — the column would grow values the form could never show — the write path for an
arbitrary value is unverified in this dialect, and it cannot hold several tickers without
multi-select. The mapping list remains the upgrade path if the vocabulary ever needs governing.

**Maturity → YEARS, decimals allowed.** The issue said "numeric" without a unit, which does not
survive a name freeze. Confirmed as a tenor in years (0.25 = three months), NOT a calendar
maturity date; the caption says so at the point of entry. A real maturity date would be a
separate DateTime column, never a reinterpretation of this one.

## Schema — `schema/schema.yaml`
Four columns on `taskmaster_products`, all `required: false`, **none indexed**: nothing filters
or sorts on them yet, and an index is the one property here that can be added later without
consequence. **NOT YET IN SHAREPOINT** — and this is the ordering constraint for the paste: a
Patch naming a column the list does not have fails the WHOLE write, so provisioning has to come
first or the screen stops saving products at all, not just the new fields.

`product_underlying` carries the note that uppercasing is the APP's job and only the app's —
a row written by a flow or a hand edit in the list UI arrives in whatever case it was typed, so
readers must treat the column as case-insensitive.

## scrProductEdit
- `gPdUnd` is the underlying box's `Default`, not a copy of it. **A text input has no `.Text`
  setter**, so a suggestion chip appends to the global and `Reset`s the control; `OnChange`
  keeps the global in step while typing, so both agree whichever way the text arrived.
- **The vocabulary is emergent**: `Concat` every stored value into one comma-string, `Split` it
  back into single tickers, trim/upper, `Distinct`, sort. That is what makes a multi-ticker
  product contribute each ticker separately. Not delegable and does not need to be — it reads
  reference data bounded by the row limit, and if it ever goes stale nothing else breaks.
- Chips filter out tickers already in the box, comparing **comma-wrapped, de-spaced tokens**.
  The bare `in` is a substring test and would hide `AA` whenever `AAPL` was present.
- **Normalisation happens at WRITE time, not in the box.** Uppercasing as the user types needs a
  Reset per keystroke and fights the cursor. Per-token: trimmed, uppercased, empties dropped,
  rejoined with ", ", trailing separator cut afterwards — `Concat`'s separator argument is not
  grounded in this dialect.
- Maturity is `Classic/TextInput@2.3.2` + `Format: =TextFormat.Number`, read as
  `Value(.Text)` — scrTransactionEdit's notional idiom. **There is no grounded modern
  number-input token**; `TextInputType.Number` is a guess and a guess fails the whole paste.
  An empty box writes `Blank()`, not 0: unknown and a zero-year tenor must not look alike.

## scrReference — the product list
Row grows 44 → 80: a third line carrying underlying · wrapper · maturity, and a fourth for
features. Blank spec fields COLLAPSE rather than printing a dash each — three placeholders read
as damage, and a product with none of these is the normal case.

Features were left off the row first and **added on the user's instruction**. Prose in a fixed
row needs two things: stored NEWLINES become spaces (a Note's line break would render here and
push the rest of the sentence out of an 18px box, so the row would appear truncated at a random
word), and a 100-character cap with an ellipsis so a long entry ENDS rather than clipping
mid-glyph. It takes its own line — prose beside three short tokens reads as one run-on string.
**The cost is rows on screen:** the 466px viewport holds ~5.8 products where the 44px row held
~10. Accepted deliberately; the compact alternative is to append a shortened features string to
the spec line and stay at 62.

## The one ungrounded token — `Split(...).Value`
`Distinct()` naming its column `Value` is confirmed in this app (`cmpNestedSelect` comment), but
**no probe has ever read a `Split()` row's column here** — cmpNestedSelect only ever takes
`CountRows(Split(...))`. MS Learn's Split page says `Value` in three example rows and then uses
`.Result` in a fourth; the canvas-app convention is `Value` and that is what shipped. It appears
in exactly TWO places (the OnVisible vocabulary build and the save-time normaliser) so that if
Studio rejects it the fix is one token in two spots, not a redesign.

## State
Authored, validated 22/22, **NOT landed**. Provision the four columns FIRST.
