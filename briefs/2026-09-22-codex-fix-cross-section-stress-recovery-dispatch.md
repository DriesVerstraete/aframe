# Dispatch: fix aframe's CSBox/CSTube stress recovery

**Use an isolated worktree for this — the `999-software/spark` checkout's own
`codex-phase1-wing-structural-model` branch (waiting on this fix) is not affected, since this
work is entirely in `999-software/aframe/`. But use a worktree for `aframe` too, in case
anything else touches its shared checkout while you work.**

1. Activate the CSDL environment first, and prove it (aframe is already installed editable
   here, so this is also where you'll run its test suite):
   `source /Users/dverstraete/miniconda3/etc/profile.d/conda.sh && conda activate csdl_acdesign && python -c "import sys; print(sys.executable)"`
   Quote the printed path as the first line of your report.
2. Read the full brief now, start to finish, before doing anything:
   `999-software/aframe/briefs/2026-09-22-codex-fix-cross-section-stress-recovery-brief.md`
3. Read the reference sources directly before writing anything:
   `999-software/aframe/aframe/core/beam.py` (`_local_stiffness_matrices`,
   `_transform_stiffness_matrices` — the element formulation `element_loads` comes from)
   `999-software/aframe/aframe/core/frame.py` (`compute_stress()` — where `element_loads` is
   built and passed to a cross-section's `stress()`)
   `999-software/aframe/aframe/core/cs.py` (`CSBox.stress()`, `CSTube.stress()` — the two
   inconsistent, buggy implementations)
   `999-software/spark/briefs/2026-09-22-codex-phase1-wing-structural-model-report.md`
   (section 4 — the original diagnosis that found this bug, read it for the exact numbers
   already established)
4. New branch `fix-cross-section-stress-recovery` off current `main`, isolated worktree.
   Execute the brief now.
5. Write your complete tagged report to:
   `999-software/aframe/briefs/2026-09-22-codex-fix-cross-section-stress-recovery-report.md`
