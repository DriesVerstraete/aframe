# Local patches — SPL fork of LSDOlab/aframe

Tracks what's changed here vs. `upstream` (`LSDOlab/aframe`), same convention as
`bladead_repo/local-patches.md`. Update this file in the same commit as any patch.
Status/history for the capability as a whole lives in
`001-dashboard/capabilities/aframe.md` + `aframe-log.md`, not here — this file is just the
patch list.

## Patches

None yet. Forked 2026-09-22 at `5aaabad` ("Add rotation attribute to Frame class to
facilitate extraction of rotations") as the wing structural model's foundation for SPARK
(`01-programs/01-program-csdl-aircraft-design/03-projects/02-spark-structures/`).

## Known gaps to patch (not yet done)

- `CSBox.buckle()` — literal empty stub (`pass`). Needs panel/plate buckling
  (see SPARK's `999-software/spark/todos.md` buckling item — AeroSandbox's closed-form plate
  buckling formula is the planned source).
- `CSTube` — no `buckle()` method at all. Needs local-crippling buckling (AeroSandbox's
  thin-walled-tube crippling formula).
- No canned modal/eigenvalue solve — `Frame` assembles real `K`/`M` matrices but only
  `Simulation` (time-domain transient) consumes them. SPARK needs a generalized eigenvalue
  helper (`scipy.linalg.eigh(K, M)` to start, non-differentiable; a differentiable version
  only if/when the vehicle-level optimizer needs frequency margin as a live constraint).

## Syncing with upstream

`git fetch upstream && git merge upstream/main` (or rebase, PI's call at the time) — upstream
has no tags/releases (confirmed 2026-09-22), so there's no version to target beyond `main`.
Re-run SPARK's structural tests after any sync, before trusting the result.
