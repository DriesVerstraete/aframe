Read AGENTS.md at the workspace root (999-software/spark/AGENTS.md — this fork follows the
same conventions) and coding-style.md it points to. This task is scoped to
999-software/aframe (a fork of LSDOlab/aframe, DriesVerstraete/aframe), not spark itself.

Review the branch fix-cross-section-stress-recovery in 999-software/aframe against
999-software/aframe/briefs/2026-09-22-codex-fix-cross-section-stress-recovery-brief.md and its
report at
999-software/aframe/briefs/2026-09-22-codex-fix-cross-section-stress-recovery-report.md.

This is a bug-fix to a real, already-diagnosed defect (found by SPARK's Phase 1 wing-
structural-model work): `CSBox.stress()` and `CSTube.stress()` used two DIFFERENT, mutually
inconsistent formulas to recover per-element internal loads from `element_loads` (`CSBox` used
a difference `(F1-F2)/2`, `CSTube` used a sum `(F1+F2)/2`), and neither reproduced the exact
closed-form root stress of a cantilever under a tip load (CSBox was 4.2% off, CSTube 95.8% off
— near-total cancellation). Run git diff yourself — don't take the report's claims on faith.
Reproduce each acceptance criterion independently. Specifically:

1. **The claimed fix and its justification.** Read `aframe/core/beam.py` (`_local_stiffness_
   matrices`, `_transform_stiffness_matrices`) and `frame.py` (`compute_stress()`) yourself to
   independently determine what `element_loads`'s 12 entries actually represent and their sign
   convention — don't just accept the report's stated convention. Confirm the corrected
   `CSBox.stress()`/`CSTube.stress()` formula is actually consistent with that convention and
   with real Euler-Bernoulli beam theory (a 2-node element under nodal-only loading has a
   LINEARLY varying internal moment between its two ends — the moment AT a given node should
   be directly recoverable from that node's own entries, not an average/difference across
   both ends, unless you independently derive why an average/difference IS correct here).
2. **Closed-form validation, reproduced yourself.** Build the same uniform-cantilever tip-load
   and distributed-load cases (both `CSBox` and `CSTube`) and compare root stress against the
   exact `M*c/I` formula yourself, in a fresh script — don't copy the report's numbers.
   Acceptance bar is < 1e-6 relative error (exact linear theory vs. exact linear solver).
3. **Consistency between CSBox and CSTube.** Confirm both cross-section classes now use the
   SAME underlying formula/convention for recovering internal loads from `element_loads` — the
   original bug was exactly that they didn't. Diff the two `stress()` methods and confirm they
   are now structurally consistent (same recovery logic, different only in section-specific
   geometry: area/I/etc.), not just independently patched to pass the same numeric test by
   coincidence.
4. **Regression check on aframe's own test suite.** Run `pytest tests/` yourself (env: check
   `999-software/spark`'s `csdl_acdesign`, `aframe` is installed editable there) before AND
   after checking out this branch, compare counts. If any previously-passing test now fails,
   or if the report claims a previously-passing test was "updated" because it depended on the
   old wrong formula, scrutinize that specific case closely — a test that was tuned to match a
   known-wrong output is a real finding, not a footnote.
5. **Scope discipline.** Confirm nothing else changed — no buckling implementation, no modal/
   eigenvalue solve added, no changes outside `cs.py` unless clearly necessary and explained.
   Confirm `local-patches.md` was updated in the same commit as the fix, describing what
   changed and why (per that file's own stated convention).

Write your complete tagged review now to
999-software/aframe/briefs/2026-09-22-codex-fix-cross-section-stress-recovery-gemini-review.md,
including PASS/FAIL, and an explicit statement of whether this is ready to merge and unblock
SPARK's Phase 1 wing-structural-model work (999-software/spark/briefs/
2026-09-22-codex-phase1-wing-structural-model-report.md, section 4, is the original diagnosis
this fix is meant to resolve — check that this fix's numbers actually address what that report
found, not a different or narrower problem).
