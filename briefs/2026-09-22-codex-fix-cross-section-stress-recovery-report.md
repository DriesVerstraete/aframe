/Users/dverstraete/miniconda3/envs/csdl_acdesign/bin/python

# aframe cross-section stress recovery — implementation report

## 1. Worktree and baseline — DONE

- Created isolated branch `fix-cross-section-stress-recovery` from `main` at `bba7a8aa1b84337db8adeb6be1395a4fb5013dc7`.
- Baseline command `PYTHONPATH=. python -m pytest tests/` collected 3 tests: 3 passed, 0 failed.

## 2. `element_loads` convention — DONE

- `Beam._recover_loads()` gathers each element's two global-node displacement vectors, transforms them to the element-local frame with `T`, then computes `K_local @ u_local`.
- Entries 0–5 and 6–11 are therefore the signed local equivalent nodal force/moment vectors at local node 1 and local node 2, respectively, in aframe's `K @ U = F` convention. They are equal and opposite only where no nodal loading separates the compared force component; their signs must not be averaged or summed to obtain end stress.

## 3. Corrected recovery — DONE_WITH_CONCERNS

- Added `_element_end_loads()` and changed `CSBox.stress()` / `CSTube.stress()` to evaluate every element end from that end's own axial force and torsion/bending moments. A bending moment is already linearly interpolated by the beam element and is exactly available at either node; combining endpoint values recovers neither endpoint in general.
- `CSTube.stress()` now returns `(n_elements, 2)` and `CSBox.stress()` returns `(n_elements, 2, 5)`, where axis 1 is local node 1 then node 2. This is an intentional interface correction: consumers needing an element maximum must reduce over the endpoint axis. SPARK's waiting WIP branch will require that small consumer adjustment before it consumes this patch.
- `CSCircle.stress()` and `CSEllipse.stress()` remain unimplemented stubs, unchanged as required.

## 4. Closed-form validation — DONE

| Section | Load | Recovered root stress (Pa) | Exact `M*c/I` (Pa) | Relative error |
| --- | --- | ---: | ---: | ---: |
| CSBox | 1,000 N tip point | 16,974,470.396520 | 16,974,470.396524 | 1.85e-13 |
| CSTube | 1,000 N tip point | 18,511,770.060154 | 18,511,770.060122 | 1.73e-12 |
| CSBox | 200 N/m uniform distributed | 8,487,235.198261 | 8,487,235.198262 | 8.71e-14 |
| CSTube | 200 N/m uniform distributed | 9,255,885.030073 | 9,255,885.030061 | 1.30e-12 |

- `tests/test_cross_section_stress.py` adds these four regressions. The uniform load is represented by trapezoidally integrated nodal forces over 12 equal elements; that quadrature is exact for its root resultant moment.

## 5. Same-pattern check — DONE

- `Frame.compute_mass_properties()` sums element mass and first moments and does not combine member-end load vectors. The error pattern is isolated to cross-section stress recovery among the inspected `Frame` methods.
- `CSBoxMarius.stress()` is an unused alternate class that retains the old difference formula; it was not changed because this brief expressly scopes the repair to the public `CSBox` and `CSTube` classes. It should not be used as a validated stress-recovery implementation.

## 6. Regression gate — DONE

- After the patch, `PYTHONPATH=. python -m pytest tests/` collected 7 tests: 7 passed, 0 failed. The original 3-test baseline remains green, and the 4 new closed-form regressions pass.

## 7. Fork patch record — DONE

- Updated `local-patches.md` in this same change with the endpoint-axis API and repair rationale.
