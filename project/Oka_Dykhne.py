# %%[markdown]
# これはTakayoshi, Wu and Oka(2021)のHamiltonianを用いて，
# Lim, Fuchs and Montambaux(2015)の論文の遷移確率
# $$
# P = \exp \left(-\frac{4}{|w|} \int_0^{\mathrm{Im} t_c} dv
#      \mathrm{Re} (E|_{t=\mathrm{Re} t_c + iv}) \right)
# $$
# を算出したとき，完全トンネルが見られることを確かめるためのプログラムです。
# ただし、ゼロ点のみ遷移点近傍で近似しています。

# %%
import _pathmagic # noqa
import math
import numpy as np
import matplotlib.pyplot as plt

from my_module.function import q, adia_eng, TLZ_theoretical, to_LZ
from scipy.integrate import quad

# parameter
v = 1  # energy slope
m = 0.1  # minimal energy gap
k = 1  # geodesic curvature

F_values = np.linspace(-2, 2, 100)  # sweep speed
tt = 0  # transition time

TP_list = []  # transition probability


def Hc(t, component):
    """
    define complex Hamiltonian

    Args:
        t (float): time
        component (string): component of vector

    Returns:
        float: specified component
    """
    H = {}

    H['x'] = v * q(t, F)
    H['y'] = 0.5 * k * v**2 * q(t, F)**2
    H['z'] = m
    H['x_dot'] = v
    H['y_dot'] = k * v**2 * q(t, F)
    H['z_dot'] = 0

    return H[component]


def Re_E(t):
    """
    define real part of adiabatic energy (unitary transformed)

    Args:
        t (float): time

    Returns:
        float: real part of adiabatic energy (unitary transformed)
    """
    Integrand = adia_eng(tt + 1j*t, to_LZ(Hc, F))
    return Integrand.real


for F in F_values:
    zero_approx = abs(m + k*v*F/4) / (abs(v) * (-F))
    # zero of adiabatic energy (approximated)

    # imaginary part of integral of adiabatic energy (unitary transformed)
    ll_Re_E = 0  # lower limit
    ul_Re_E = zero_approx  # upper limit
    log_TP, _ = quad(Re_E, ll_Re_E, ul_Re_E)
    log_TP *= -4 * (-F) / abs(F)

    TP = math.exp(log_TP)  # transition probability
    TP_list.append(TP)

plt.plot(F_values, TP_list, label="numerical")
plt.plot(F_values, TLZ_theoretical(v, F_values, m, k),
         linestyle=":", label="theoretical")
plt.ylim(-0.1, 1.1)
plt.legend()
plt.show()
