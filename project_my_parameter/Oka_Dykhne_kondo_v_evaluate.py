# %%[markdown]
# Oka_Dykhne_kondo.pyで$F$を固定して$\nu$を変化させるプログラムです。
# energy slope $\nu$を横軸、遷移確率$P$を縦軸にしたグラフを出力します。
# $\nu$, $F$の符号反転はそれぞれ、時間反転、エネルギー反転に対応します。
# - 現状Integration Warningが出ます。→調査中

# %%
import _pathmagic # noqa
import math
import cmath
import numpy as np
import matplotlib.pyplot as plt

from my_module.function import TLZ_theoretical, q, adia_eng
from scipy.integrate import quad

# parameter
eps_0_values = np.linspace(-2, 2, 100)  # energy slope
D_z = 0.1  # minimal energy gap
k = 1  # geodesic curvature

# constant
h = 1  # Dirac constant (should not change)
F = -1  # sweep speed (should not change)(時間反転させないため)
TP_list = []  # transition probability


def Hc(t, component):
    """
    define complex Hamiltonian and its derivative
    with respect to parameter sweep

    Args:
        t (float): time
        component (string): component of vector

    Returns:
        float: specified component
    """
    H = {}

    H['x'] = -eps_0 * cmath.cos(q(t, F))
    H['y'] = 0.25 * k * eps_0**2 * cmath.cos(q(t, F)) * cmath.sin(2*q(t, F))
    H['z'] = D_z * cmath.sin(q(t, F))
    H['x_dot'] = eps_0 * cmath.sin(q(t, F))
    H['y_dot'] = (0.25 * k * eps_0**2
                  * (-cmath.sin(q(t, F))*cmath.sin(2*q(t, F))
                     + 2*cmath.cos(q(t, F))*cmath.cos(2*q(t, F))))
    H['z_dot'] = D_z * cmath.cos(q(t, F))

    return H[component]


def Re_E(t):
    """
    define real part of adiabatic energy (unitary transformed)

    Args:
        t (float): time

    Returns:
        float: real part of adiabatic energy (unitary transformed)
    """
    Integrand = adia_eng(tp + 1j*t, Hc, ut=True, F=F)
    return Integrand.real


for eps_0 in eps_0_values:
    if abs(eps_0) < 0.03:  # avoid Integration Warning
        continue

    tp = math.pi / (2*abs(F))  # transition time
    zero_approx = abs(D_z - k*abs(eps_0)*F/4) / (abs(eps_0) * (-F))
    # -pi/2のときは分子の第二項の符号が変わる
    # 被積分関数の符号と合わせる
    # zero of adiabatic energy (approximated)

    # imaginary part of integral of adiabatic energy (unitary transformed)
    ll_Re_E = 0  # lower limit
    ul_Re_E = zero_approx  # upper limit
    log_TP, _ = quad(Re_E, ll_Re_E, ul_Re_E)
    log_TP *= -4 * (-F) / abs(F)

    TP = math.exp(log_TP)
    TP_list.append(TP)

eps_0_values = eps_0_values[abs(eps_0_values) >= 0.03]  # avoid Integration Warning
plt.plot(eps_0_values, TP_list, label="numerical")
plt.plot(eps_0_values, TLZ_theoretical(eps_0_values, F, D_z, k),
         linestyle=":", label="theoretical")
plt.legend()
plt.ylim(-0.1, 1.1)
plt.show()