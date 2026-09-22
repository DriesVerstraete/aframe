import numpy as np
import pytest

import aframe as af
import csdl_alpha as csdl


LENGTH = 5.0
YOUNGS_MODULUS = 70.0e9
SHEAR_MODULUS = 26.0e9
DENSITY = 2700.0
TIP_LOAD = 1000.0
DISTRIBUTED_LOAD = 200.0
NODES = 13


def _cross_section(kind):
    if kind == "box":
        width, height, cap, web = 0.12, 0.20, 0.01, 0.008
        section = af.CSBox(
            ttop=csdl.Variable(value=np.full(NODES - 1, cap)),
            tbot=csdl.Variable(value=np.full(NODES - 1, cap)),
            tweb=csdl.Variable(value=np.full(NODES - 1, web)),
            height=csdl.Variable(value=np.full(NODES - 1, height)),
            width=csdl.Variable(value=np.full(NODES - 1, width)),
        )
        inertia = (width * height**3 - (width - 2.0 * web) * (height - 2.0 * cap)**3) / 12.0
        return section, height / 2.0, inertia
    radius, thickness = 0.10, 0.01
    section = af.CSTube(
        radius=csdl.Variable(value=np.full(NODES - 1, radius)),
        thickness=csdl.Variable(value=np.full(NODES - 1, thickness)),
    )
    inertia = np.pi * (radius**4 - (radius - thickness)**4) / 4.0
    return section, radius, inertia


def _root_stress(kind, loads):
    recorder = csdl.Recorder(inline=True)
    recorder.start()
    section, extreme_fiber, inertia = _cross_section(kind)
    mesh = np.zeros((NODES, 3))
    mesh[:, 1] = np.linspace(0.0, LENGTH, NODES)
    beam = af.Beam("cantilever", csdl.Variable(value=mesh), YOUNGS_MODULUS, SHEAR_MODULUS, DENSITY, section)
    beam.fix(0)
    beam.add_load(csdl.Variable(value=loads))
    frame = af.Frame([beam])
    frame.solve()
    stress = frame.compute_stress()[beam.name].value
    recorder.stop()
    return (stress[0, 0, 0] if kind == "box" else stress[0, 0]), extreme_fiber, inertia


def _distributed_loads():
    step = LENGTH / (NODES - 1)
    loads = np.zeros((NODES, 6))
    loads[:, 2] = DISTRIBUTED_LOAD * step
    loads[[0, -1], 2] *= 0.5
    return loads


@pytest.mark.parametrize("kind", ["box", "tube"])
def test_tip_load_root_stress_matches_euler_bernoulli(kind):
    loads = np.zeros((NODES, 6))
    loads[-1, 2] = TIP_LOAD
    stress, extreme_fiber, inertia = _root_stress(kind, loads)
    expected = TIP_LOAD * LENGTH * extreme_fiber / inertia
    assert abs(stress - expected) / expected < 1.0e-6


@pytest.mark.parametrize("kind", ["box", "tube"])
def test_distributed_load_root_stress_matches_euler_bernoulli(kind):
    stress, extreme_fiber, inertia = _root_stress(kind, _distributed_loads())
    expected = DISTRIBUTED_LOAD * LENGTH**2 * extreme_fiber / (2.0 * inertia)
    assert abs(stress - expected) / expected < 1.0e-6
