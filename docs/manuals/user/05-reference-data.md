# 5 · Reference data

The **Reference** screen maintains the two lists the rest of the app picks from: **clients** and
**products**. Both are searchable, and both have a **＋ New** button at the top of the screen.

You can also reach either form without leaving what you are doing: any client or product picker
elsewhere in the app offers **＋ New**, and returns you to the form you came from once you save.

## Clients

Fields: **client name** `*`, **type** `*`, **coverage** `*`, notes, and the sales person.

The sales person comes from the company directory — you pick someone who exists rather than
typing a name. No person is ever created by this app.

## Products

A product is an instrument. Fields: **product ID** `*` (ISIN, ticker or an internal ID),
**description** `*`, **asset class** `*`, wrapper, underlying (a ticker, or several separated by
commas), maturity in years (`0.25` is three months), whether it is an ESG product, and features.

### Product IDs must be unique

The product ID is a business key, and the form checks for a duplicate before saving. If one
exists you are told, and nothing is written.

That check matters: two rows for the same instrument make every task that links to it ambiguous,
and the ambiguity is invisible afterwards. If you believe a product is missing, search for it by
ID before creating it.

## Editing reference data affects everything pointing at it

Renaming a client or correcting a product's description changes what every task and project
showing it displays. That is usually what you want. Deleting one is not — anything already
linked to it is left pointing at nothing.
