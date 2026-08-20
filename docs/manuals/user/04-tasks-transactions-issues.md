# 4 · Tasks, transactions and issues

The three kinds of work that hang off a project. All three are created from the project screen
and all three follow the same form conventions ([chapter 1](01-getting-started.md#conventions-every-screen-shares)).

---

## Tasks

A task is a piece of work. The form is in sections:

- **Task** — name `*`, stage `*`, priority `*`, status, start date, description
- **People and dates** — who is on it and when it is due
- **Client** — the client it is for, whether a client section is involved, and the client's
  lifecycle stage
- **Products** — link the instruments the task concerns (**＋ Add a product**; "No products
  linked yet" until you do)
- **Output** — everything below the **Task produces output?** toggle

### Stage drives the project ring

A task's **stage** is what moves its project's completion percentage. Nothing else does. Setting
a task to *Completed* also stamps its completion date automatically; moving it back to any other
stage clears that stamp.

### The output section

Turning **Task produces output?** on reveals output audience, output language, output
requirements, content format, branding and whether approval is required.

> **Turning the toggle off and saving clears every one of those fields.** That is deliberate —
> a hidden section must not leave values stored where nobody can see or correct them. If you
> only meant to collapse the section from view, do not save with it off.

### Health is not a field

There is no health control on the task form, because health is computed:

- **Red** — the task has an open issue of critical impact, or one typed as a blockage,
  exception or limitation; **or** the task is not complete and its target date has passed
- **Amber** — the task has any other open issue
- **Green** — no open issues

To change a task's health, resolve or re-type the issue against it, or fix the target date.

---

## Transactions

A transaction records one trade against the project: **label** `*`, **trade date** `*`,
**currency** `*` and **notional in that native currency**.

### The currency rule

**The app records notional in its native currency and never converts it.** Consequently:

- Per-currency figures are shown throughout.
- **No screen in this app shows a blended, cross-currency total**, and none will be added.

The reason is that a rate frozen at write time can never be restated or audited later, whereas
converting at report time can be. Cross-currency conversion is handled by other desk tools,
outside this app. If you need a blended number, it comes from there.

---

## Issues

An issue records what is going wrong: **summary** `*`, **status** `*`, type, impact, description,
target resolution date, and optionally the **related task** or **related transaction**.

Linking an issue to a task is what feeds that task's health, so link it when the issue really is
about that task — that link is the mechanism that turns a task amber or red.

Closing an issue removes it from the open-issue lists on Home and from the desk-wide open-issue
figures, and re-computes the health of the task it was linked to.
