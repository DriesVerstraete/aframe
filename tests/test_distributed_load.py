import numpy as np
import pytest

import aframe as af
import csdl_alpha as csdl


@pytest.mark.parametrize("kind", ("box", "tube"))
def test_uniform_distributed_load_matches_cantilever_closed_form(kind):
    length, load, nodes = 5.0, 200.0, 13
    recorder = csdl.Recorder(inline=True)
    recorder.start()
    if kind == "box":
        width, height, cap, web = 0.12, 0.20, 0.01, 0.008
        section = af.CSBox(*[csdl.Variable(value=np.full(nodes - 1, value)) for value in (cap, cap, web, height, width)])
        inertia = (width * height**3 - (width - 2 * web) * (height - 2 * cap)**3) / 12
        fiber = height / 2
    else:
        radius, thickness = 0.10, 0.01
        section = af.CSTube(csdl.Variable(value=np.full(nodes - 1, radius)), csdl.Variable(value=np.full(nodes - 1, thickness)))
        inertia = np.pi * (radius**4 - (radius - thickness)**4) / 4
        fiber = radius
    mesh = np.zeros((nodes, 3))
    mesh[:, 1] = np.linspace(0, length, nodes)
    beam = af.Beam("cantilever", csdl.Variable(value=mesh), 70e9, 26e9, 2700, section)
    beam.fix(0)
    distributed = np.zeros((nodes - 1, 6))
    distributed[:, 2] = load
    beam.add_distributed_load(csdl.Variable(value=distributed))
    frame = af.Frame([beam])
    frame.solve()
    stress = frame.compute_stress()[beam.name].value
    recorder.stop()
    root_stress = stress[0, 0, 0] if kind == "box" else stress[0, 0]
    expected_deflection = load * length**4 / (8 * 70e9 * inertia)
    expected_stress = load * length**2 * fiber / (2 * inertia)
    assert abs(abs(frame.displacement[beam.name].value[-1, 2]) - expected_deflection) / expected_deflection < 1e-6
    assert abs(root_stress - expected_stress) / expected_stress < 1e-6
