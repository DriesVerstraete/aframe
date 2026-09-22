# aframe fork patch — fix CSBox/CSTube stress recovery

## Context / why

SPARK's wing-structural-model Phase 1 brief (`999-software/spark/briefs/
2026-09-22-codex-phase1-wing-structural-model-brief.md`) hit a real, well-diagnosed bug while
validating `aframe` against closed-form beam theory: for a uniform cantilever under a tip
point load, `CSBox.stress()`/`CSTube.stress()` do NOT reproduce the exact root bending stress
(`M*c/I` at the fixed end), even though nodal DEFLECTION matches closed-form Euler-Bernoulli
to 1e-6.

Root cause, already found by the prior pass (report:
`999-software/spark/briefs/2026-09-22-codex-phase1-wing-structural-model-report.md`, section
4): `CSBox.stress()` recovers element internal loads via `(F1 - F2)/2` (a difference of the
two nodal end-forces); `CSTube.stress()` uses `(F1 + F2)/2` (a SUM) for the equivalent
quantity — an internal inconsistency between the two cross-section classes for the same
underlying physics. Neither reproduces the exact root stress: `CSBox` is off by 4.17%,
`CSTube` by 95.8% (near-total cancellation, consistent with summing two nearly-equal-and-
opposite quantities that should not have been summed).

This brief's job: diagnose the correct per-element internal-force recovery for `aframe`'s
2-node Euler-Bernoulli beam element, fix BOTH `CSBox.stress()` and `CSTube.stress()`
consistently, and validate against exact closed-form beam theory. This unblocks SPARK's Phase
1 wing structural model, and matters beyond that single check — future SPARK work
(buckling, eventually composite ply stress recovery, both already scoped in
`999-software/spark/todos.md`) all depend on `aframe`'s stress recovery being correct.

Report to: `999-software/aframe/briefs/2026-09-22-codex-fix-cross-section-stress-recovery-report.md`.

## Branch & git rules

- This is the `999-software/aframe/` repo (fork of `LSDOlab/aframe`, `DriesVerstraete/aframe`),
  NOT `999-software/spark/`. Work here, not there.
- Branch `fix-cross-section-stress-recovery` off current `main`. Never commit to `main`
  directly. No PR — the PI's Claude session reviews and merges (same convention as `spark`).
- Update `local-patches.md` in the same commit as the fix — this is the fork's own log of
  what's changed vs. upstream `LSDOlab/aframe`, per its own header instructions.

## The work

1. **Understand `element_loads`'s actual convention.** Read `aframe/core/beam.py`'s
   `_local_stiffness_matrices`, `_transform_stiffness_matrices`, and wherever `element_loads`
   is actually computed/passed into a cross-section's `stress(element_loads)` method (trace the
   call site in `frame.py`'s `compute_stress()`) — confirm exactly what each of the 12 entries
   (`F_x1..M_z1, F_x2..M_z2`) physically represents (member end-forces/moments at each of the
   element's two local nodes, in the element's local coordinate frame — confirm this, don't
   assume) and their sign convention (do node-1 and node-2 forces represent the internal force
   the element exerts ON each node, or the reaction the node exerts ON the element — these
   differ by an overall sign and matter for getting the fix right).

2. **Derive the correct stress recovery.** For a 2-node Euler-Bernoulli beam element under only
   nodal loading (no distributed load along the element — true for every case relevant here),
   bending moment varies LINEARLY from one end to the other. The moment AT a given node is
   already directly present in that node's own entries of `element_loads` (e.g. `M_y1`, `M_z1`
   for node 1) — it should not need averaging or differencing with the other node's values to
   recover a single value. Determine whether the fix is: (a) evaluate stress separately at each
   of the element's two ends using that end's own forces directly (returning two stress values
   per element, not one), or (b) some other correct closed-form recovery — derive this from
   the actual beam theory and the confirmed sign convention from step 1, don't guess by pattern-
   matching the existing (buggy) code.

3. **Fix `CSBox.stress()` and `CSTube.stress()` consistently**, using the same corrected
   formula/convention in both (the fact that they currently use two DIFFERENT formulas for the
   same physics is itself a symptom of the bug — after the fix, verify both classes agree on
   what `element_loads`'s 12 entries mean and use them the same way).

4. **Closed-form validation.** Reproduce the exact validation SPARK's Phase 1 brief already
   specified: a uniform cantilever (constant cross-section, single material) under (a) a tip
   point load, (b) a uniform distributed load, for BOTH `CSBox` and `CSTube`. Compare stress AT
   THE ROOT (fixed end) against the exact closed-form `M*c/I`. Target: relative error < 1e-6
   (this is exact linear theory vs. an exact linear beam solver — should be near machine
   precision, matching how well deflection already matches). Also check `CSCircle`/`CSEllipse`
   if their `stress()` methods are non-trivial (recall from the source: both currently have
   `stress()` return `pass`/`None` — if genuinely unimplemented stubs, leave them, don't scope-
   creep into implementing new cross-section stress methods here).

5. **Check for the same bug pattern elsewhere.** `compute_mass_properties()`/other `Frame`
   methods that might similarly combine per-node quantities — a quick check, not a full audit,
   to see if this averaging-convention bug is isolated to `stress()` or more widespread. Report
   what you find either way.

6. **Regression check.** Run `aframe`'s own existing test suite (`pytest tests/` in this repo,
   whatever env has `csdl_alpha` — check `999-software/spark`'s `csdl_acdesign` env, `aframe`
   is already installed editable there) before and after the fix, confirm nothing existing that
   was passing now fails (a fix to a genuinely wrong formula could change other tests' expected
   numbers if any of them were tuned to the old, wrong output — flag this explicitly if you find
   it, don't just silently update expected values).

## Boundaries — DO NOT

- Do not touch anything in `999-software/spark/` — that repo has its own active branches (the
  wing-structural-model work, waiting on this fix, and possibly others). This brief's scope is
  entirely within `999-software/aframe/`.
- Do not implement new cross-section stress methods for `CSCircle`/`CSEllipse` if they're
  genuinely unimplemented stubs — out of scope, not what's blocking anything right now.
- Do not implement buckling (`CSBox.buckle()`/`CSTube`'s missing buckle method) — separate,
  already logged, not this brief's job.
- Do not add a modal/eigenvalue solve to `Frame`/`Simulation` — separate, not this brief's job.
- No merge to `main` — leave the branch for review.

## Acceptance criteria

- GIVEN the corrected `CSBox.stress()`/`CSTube.stress()`, WHEN evaluated at the root of a
  uniform cantilever under a tip point load, THEN relative error vs. exact `M*c/I` is < 1e-6
  for both cross-section types.
- GIVEN the same setup under a uniform distributed load instead, THEN the same < 1e-6 bar
  holds.
- GIVEN `aframe`'s own existing test suite, WHEN run before and after the fix, THEN report
  exact pass/fail counts for both and explain any change (a previously-passing test that now
  fails because it depended on the old wrong formula needs explicit discussion, not a silent
  "fixed" claim).

## Report back

Tag every item DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED per
`07-shared-knowledge/methods/codex-brief-conventions.md`. Report:
- The env python path, first line.
- What `element_loads`'s 12 entries actually represent and their sign convention (step 1) —
  state this explicitly, it's the foundation the fix rests on.
- The exact corrected formula and why it's correct (step 2).
- Closed-form validation numbers, both cross-section types, both load cases (step 4).
- Whether the same bug pattern appears elsewhere (step 5).
- `aframe`'s own test suite pass/fail counts before and after (step 6).
- Commit your work on the branch, `local-patches.md` updated in the same commit. No merge.
