# schema/ — the schema snapshot

The authoritative record of the eight `tm*` lists' **true internal column names**, captured from
the actual SharePoint columns (provisioning is manual, so names aren't known until created and
may be `_x0020_`-mangled). The `context/schema.md` brief holds the design + decisions with
⟨capture⟩ placeholders; this folder holds the machine-checkable snapshot the `pre-paste-review`
agent and the (proposed) column-token validator hook check against.

Populate this once the lists exist. `/pull-reconcile` cross-checks pulled field references here.
