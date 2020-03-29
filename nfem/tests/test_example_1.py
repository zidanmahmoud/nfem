import pytest
import nfem
from numpy.testing import assert_almost_equal


@pytest.fixture
def model():
    model = nfem.Model()

    model.add_node('A', x=0, y=0, z=0, support='xyz')
    model.add_node('B', x=1, y=1, z=0, support='z', fy=-1)
    model.add_node('C', x=2, y=0, z=0, support='xyz')

    model.add_truss('1', node_a='A', node_b='B', youngs_modulus=1, area=1)
    model.add_truss('2', node_a='B', node_b='C', youngs_modulus=1, area=1)

    return model


@pytest.fixture
def load_curve():
    return [0.01, 0.02, 0.03, 0.05, 0.10, 0.136, 0.15, 0.30, 0.50, 0.70, 1.00]


def test_linear(model, load_curve):
    for load_factor in load_curve:
        model = model.get_duplicate()
        model.lam = load_factor
        model.perform_linear_solution_step()

    actual = model.load_displacement_curve(('B', 'v'), skip_iterations=False)

    assert_almost_equal(actual.T, [
        [0.0, 0.0],
        [-0.0141421356237309, 0.01],
        [-0.028284271247461912, 0.02],
        [-0.04242640687119281, 0.03],
        [-0.07071067811865483, 0.05],
        [-0.14142135623730956, 0.1],
        [-0.19233304448274102, 0.136],
        [-0.21213203435596428, 0.15],
        [-0.42426406871192857, 0.3],
        [-0.7071067811865477, 0.5],
        [-0.9899494936611667, 0.7],
        [-1.4142135623730954, 1.0],
    ])


def test_nonlinear(model, load_curve):
    for load_factor in load_curve:
        model = model.get_duplicate()
        model.predict_tangential(strategy='lambda', value=load_factor)
        model.perform_non_linear_solution_step(strategy='load-control')

    actual = model.load_displacement_curve(('B', 'v'), skip_iterations=False)

    assert_almost_equal(actual.T, [
        [0.0, 0.0],
        [-0.0141421356237309, 0.01],
        [-0.0141421356237309, 0.01],
        [-0.01445385294069157, 0.01],
        [-0.029232168261022373, 0.02],
        [-0.029232168261022373, 0.02],
        [-0.029583961088618937, 0.02],
        [-0.04508115707238347, 0.03],
        [-0.04508115707238347, 0.03],
        [-0.04548206099190799, 0.03],
        [-0.07811813224935649, 0.05],
        [-0.07811813224935649, 0.05],
        [-0.0800642544308856, 0.05],
        [-0.17196521008299315, 0.1],
        [-0.17196521008299315, 0.1],
        [-0.19329409832903488, 0.1],
        [-0.1944705575501272, 0.1],
        [-0.3020342821741575, 0.136],
        [-0.3020342821741575, 0.136],
        [-0.3599334939928016, 0.136],
        [-0.38973115054939034, 0.136],
        [-0.4040424419683939, 0.136],
        [-0.4097227985203731, 0.136],
        [-0.4109927429816784, 0.136],
        [-1.3818016121742265, 0.15],
        [-1.3818016121742265, 0.15],
        [-0.048173143837289656, 0.15],
        [-0.24304097278704717, 0.15],
        [-0.38356697237160164, 0.15],
        [-0.6841279442266699, 0.15],
        [-0.48445150410973337, 0.15],
        [-0.25870256432199124, 0.15],
        [-0.3979726560292338, 0.15],
        [-0.8610731807717671, 0.15],
        [-0.5553527314822957, 0.15],
        [-0.38938046390527425, 0.15],
        [-0.7378521901933532, 0.15],
        [-0.5109394037563101, 0.15],
        [-0.32621496769185077, 0.15],
        [-0.4819459193825092, 0.15],
        [-0.24975162999785416, 0.15],
        [-0.38961144032777406, 0.15],
        [-0.7403558266866119, 0.15],
        [-0.5120602989717058, 0.15],
        [-0.32834527621662146, 0.15],
        [-0.4857095435022004, 0.15],
        [-0.26296310580675775, 0.15],
        [-0.40208809028599324, 0.15],
        [-0.9552894436315382, 0.15],
        [-0.5733560600850498, 0.15],
        [-0.40751359817275457, 0.15],
        [-1.1560803897026872, 0.15],
        [-0.5340804322102267, 0.15],
        [-0.36351230227954456, 0.15],
        [-0.5753913150520273, 0.15],
        [-0.4094025480181579, 0.15],
        [-1.2640674130913285, 0.15],
        [-0.4169338389551174, 0.15],
        [-2.398026613469672, 0.15],
        [-2.210890955430284, 0.15],
        [-2.1696047925052238, 0.15],
        [-2.1676325521538797, 0.15],
        [-2.3049305150748953, 0.3],
        [-2.3049305150748953, 0.3],
        [-2.2882252769773648, 0.3],
        [-2.2879518574996847, 0.3],
        [-2.430210406660552, 0.5],
        [-2.430210406660552, 0.5],
        [-2.41442652326544, 0.5],
        [-2.414213600845791, 0.5],
        [-2.5273506784488813, 0.7],
        [-2.5273506784488813, 0.7],
        [-2.518055843275997, 0.7],
        [-2.517989036832983, 0.7],
        [-2.661494276961419, 1.0],
        [-2.661494276961419, 1.0],
        [-2.648209089855375, 1.0],
        [-2.6480863731391198, 1.0],
    ])
