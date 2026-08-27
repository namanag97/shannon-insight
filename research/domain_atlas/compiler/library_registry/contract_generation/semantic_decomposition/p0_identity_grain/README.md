# P0 identity/equality and grain/cardinality

This P0 corpus mines the 674 rich API candidates for public types and operations that may carry
identity, equality, grain or cardinality semantics. Suffixes and operation names are routing
signals only: `Id`, `Ref`, `Key`, `Record`, `Event`, `Result` and similar words do not establish
meaning, ownership or substitutability.

There are exactly 46 owner packets—two axes for each of 23 families. Exact public type names shared
across families become collision records requiring shared-foundation, profile, ACL, rename,
duplicate-rejection or unresolved decisions. No common name is automatically unified.

`global-symbol-collisions.jsonl` is stricter than name collision detection. It finds repeated type,
trait and operation identifiers across candidate libraries, distinguishes byte-identical repeated
definitions from conflicting definitions, and requires a canonical shared owner/import or a
qualified local identity. Until adjudicated, the compiler refusal is
`AMBIGUOUS_PUBLIC_SYMBOL_OWNER`.

Run `python3 build_p0.py`, then `python3 validate.py`.
