# 2026-08-05 · scrProjectEdit — usability review and container rebuild

**Ask:** *"review the scrProjectEdit — I think this can be vastly improved — additionally the
submit button is floating in the middle of the screen rather than fixed below the container of
the form object. Make this more usable and change/add controls where you see fit."*

**Status:** authored, validated (23/23, no notes), **not landed**. `BUILD-BOOK.md` step 4d is
still unchecked, which is why the whole screen could be rebuilt rather than patched.

---

## 1. The reported bug, and why it was guaranteed rather than unlucky

`actionBar` was anchored responsively:

```yaml
actionBar:   Y: =Parent.Height - 132     # follows the screen
btnPrSave:   Y: =706                     # does not
btnPrCancel: Y: =706
lblPrMissingCap / lblPrMissing: Y: =652 / 670
```

Those numbers agree only on a screen exactly 768 tall. Combined with the freeze rule
(*layout formulas are overwritten with constants on paste* — memory, 2026-08-04), the bar landed
at the real bottom of the screen while the buttons kept 706: the Save button floating mid-screen,
exactly as reported.

**Fixed at the anchor level, not with a better constant.** The footer is now:

- `actionBarBg` — opaque Rectangle, `Y: =Parent.Height - 88`, `Height: =88`
- `actionBarRow` — horizontal auto-layout container, **the identical anchor expression**

`actionBarRow`'s children (`lblPrMissing` → `btnPrCancel` → `btnPrSave`, message left, buttons
right) carry **no X/Y at all** — the container places them. Whatever Studio freezes, the bar and
its contents freeze to the same value. The opaque backing rectangle stays for the reason it
always existed: a stale frozen `Height` still cannot let the scrolling form show through the
Save row.

Band table is now `0..64` header · `64..Parent.Height-88` form · `88` action bar.

## 2. The bigger problem the review turned up

`frmPrScroll` is a **vertical** auto-layout container, but its children were ordered for a
**two-column grid**:

```
lblPrNameCap · lblPrPhaseCap · txtPrName · cboPrPhase · lblPrPathCap · lblPrPriorityCap · …
```

In a one-column container that renders as *caption, caption, field, field* — **no label belonged
to any field.** Nothing errors, nothing warns; the form just reads as nonsense. This is the
single biggest usability defect on the screen and it was invisible in the source because the
names looked paired.

Rebuilt as `row*` (horizontal) → `col*` (vertical) → caption 18 + gap 8 + control 36 = 62.
**57 auto-layout containers, 0 children carrying X/Y** (asserted programmatically).

Structure now: Details (3 fields × 2 rows + description) · **People** (split out; 3 pickers) ·
Classification (3 `cmpTermPicker`s) · Tasks · Transactions · Issues, with a rule + section
heading between each and the whole column on an opaque `formSheet`.

## 3. Five more defects found while reading

| # | Defect | Consequence |
|---|---|---|
| a | `OnVisible` had **no `;`** after `Reset( txtNiName )` | Studio would reject the entire screen on paste |
| b | `dtpPrStart` / `dtpPrTarget` had **no `DefaultDate`** | an Edit opened blank and Patched `Blank()` over the stored dates — **silent data loss** |
| c | `cboNiStatus` = `["Open","In Progress","Blocked","Resolved"]` | two values are not members of `issue_status` |
| d | `cboNiImpact` = `["Low","Medium","High"]`, and `i_impact` never appeared in the Patch | one invalid value, and the field was staged then dropped |
| e | all **five** modal galleries were `Visible: =gN*Open` | permanently open, sitting on the identical X/Y as their own selection chip, querying `SearchUserV2` with an empty term — the pick was never visible |

(b) is the dangerous one: no error, just a date that quietly disappears — the quiet-wrong class
the one-way gap cannot detect. **The other three edit screens need auditing for the same shape.**

## 4. Usability changes beyond the bug

- **Pickers collapse to a clearable chip.** Search box beside a flat `Classic/Button` reading
  `Name  ✕`, `DisplayMode.Disabled` when empty. Clearing now also `Reset()`s the search box —
  the old `Classic/Icon` clear did not, so the stale term instantly re-opened the gallery.
- **Results expand inline** (canvas-design §5: a hidden child takes no space) as a *sibling* of
  the row, full width, `Height: =132`. Replaces the whole absolute-overlay pattern and the
  one-picker-at-a-time gate: nothing can cover a row the user needs to click.
- **Staged lists cost nothing when empty** — `Visible: =!IsEmpty(col…)` + a constant `Height:
  =200` + an empty-state line + a live count in the heading, instead of 1,160px of unconditional
  blank space. Rows are two-line (name / meta) at 44px with a rule and a trash icon.
- **One primary action on the screen.** The three "+ Add" buttons dropped to `Outline`.
- **The modals are containers**: scrim → opaque `md*Bg` → `md*Body` (vertical, `LayoutOverflowY
  .Scroll`) → rows, with Add/Cancel **outside** the body on the card's own anchor so they stay
  pinned to the card's bottom edge however tall the body grows. Cards sized so one open picker
  fits without internal scrolling (task/issue 700×540 body 460; transaction 780×680 body 600).
- **`lblPrMissingCap` folded into `lblPrMissing`** via `With(…)`, so `Len(lblPrMissing.Text) = 0`
  is still exactly the test `btnPrSave.DisplayMode` needs.
- Derived fields (`project_date_complete`, `project_perc_completion`) are **stated on screen**
  instead of left to be discovered.
- Cancel reads **"Discard"** when anything is staged; the header's staged-count chip appears only
  when there is work to lose.

## 5. Deliberately NOT done

- **No `cmpAppBar` on this screen.** Its fly-out nav rail would let a user navigate away from an
  editor holding unsaved staged children with no warning. A close-only header is right here.
- **No confirm-on-discard dialog.** `cmpConfirmDialog` exists and would fit, but it is a new
  instance on a screen that has never landed once — the "Discard" label + staged-count chip is
  the cheap version. Worth revisiting after the first successful paste.
- **`Height` left constant everywhere it could have been dynamic** — see the staged-gallery
  decision in `INDEX.md`.

## 6. Open threads this leaves

1. **Audit `scrTaskEdit` / `scrTransactionEdit` / `scrIssueEdit`** for defect (b) — date pickers
   with no `DefaultDate` on an edit path — and for hardcoded combobox `Items` that have drifted
   from `schema.yaml` (defects c/d).
2. **Hook candidate, now concrete:** the column-token validator does not look inside `Items: =[…]`
   array literals, which is how three invalid Choice values survived. Extend it to check each
   array literal against the matching Choice column's `values:`.
3. Nested auto-layout is now three deep in places (`frmPrScroll` → `row*` → `col*`). Every token
   used is photo-confirmed, but the nesting depth itself has never crossed the gap — **if this
   paste fails, that is the first thing to suspect**, and the fallback is to flatten `col*` back
   into single-column rows (caption immediately followed by its control), which keeps the pairing
   fix and loses only the column layout.
