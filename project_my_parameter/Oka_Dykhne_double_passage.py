# %%[markdown]
# Oka(2021)をもとに
# ユニタリ変換後のHamiltonianで占有確率を数値計算<br>
# $$\Delta_x \sin{\omega t} \sigma_x
#  + \Delta_y \cos{\omega t} \sin{2 \omega t}\sigma_y
#  + \varepsilon_0 \cos{\omega t} \sigma_z\\$$
# に対してユニタリ変換する
# - 1回目の遷移
#   - kは大きくしすぎない(xとyは同程度のオーダーまで)
# - 2回目の遷移
#   - k = 0.
#   - v = -1, m = 0.1, k = 1

# %%
# multiple-passage TLZ modelにおける断熱状態の占有確率を数値計算結果と理論値で比較する
import _pathmagic # noqa
import math
import cmath
import scipy
import numpy as np
import matplotlib.pyplot as plt

from my_module.function import q, adia_eng, to_LZ
from my_module.calculator import calculate_occupation_probability
from scipy.integrate import quad

# parameter
eps_0 = -50  # energy slope
D_z = 4  # minimal energy gap
D_y = 20  # twist strength
F = -1  # sweep speed Fの値は変更しない(初期値 -1)(時間反転させないため)
t_i = -math.pi / abs(F)  # initial time
t_f = math.pi / abs(F)  # final time

tp_1 = -math.pi / (2 * abs(F))  # first transition time
tp_2 = math.pi / (2 * abs(F))  # second transition time

# constant
h = 1  # Dirac constant (should not change, initial value: 1)
n = 500  # step
t_eval = np.linspace(t_i, t_f, n)  # time
delta = (D_z - (4 * D_y / eps_0**2)*eps_0*F/4)**2 / (2 * abs(eps_0) * abs(F))  # adiabatic parameter
phi_s = (math.pi/4
         + delta * (math.log(delta) - 1)
         + cmath.phase(scipy.special.gamma(1 - 1j*delta)))  # Stokes phase(弧度法)
print("Stokes phase: ", phi_s)
TLZ = -math.pi * (D_z - (4 * D_y / eps_0**2) * eps_0 * F / 4)**2 / (abs(eps_0) * abs(F))
# １回目の遷移がOkaモデルと全体の符号が反転している場合は分子の第２項の符号をマイナスにする
zero_approx = abs(D_z - (4 * D_y / eps_0**2) * eps_0 * F / 4) / (abs(eps_0) * (-F))
# -pi/2のときは分子の第二項の符号が変わる
# 被積分関数の符号と合わせる


def H(t, component):
    """
    Complex Hamiltonian

    Args:
        t (float): time
        component (string): 成分

    Returns:
        float: 時刻tにおけるcomponentで指定した成分を返す。
    """
    H = {
        'x': eps_0 * cmath.cos(q(t, F)),
        'y': 0.125 * (4 * D_y / eps_0**2) * eps_0**2 * cmath.sin(2 * q(t, F))**2,
        'z': D_z * cmath.sin(q(t, F)),
        'x_dot': -eps_0 * cmath.sin(q(t, F)),
        'y_dot': 0.125 * (4 * D_y / eps_0**2) * eps_0**2 * 4 * cmath.sin(2 * q(t, F)) * cmath.cos(2 * q(t, F)),
        'z_dot': D_z * cmath.cos(q(t, F))
    }

    return H[component]


def Re_E(t):
    """
    define real part of adiabatic energy (unitary transformed)

    Args:
        t (float): time

    Returns:
        float: adiabatic energy
    """
    Integrand = adia_eng(tp_1 + 1j*t, to_LZ(H, F))
    return Integrand.real


# integral of transition probability
ll_Re_E = 0  # lower limit
ul_Re_E = zero_approx  # upper limit
TP, _ = quad(Re_E, ll_Re_E, ul_Re_E)
TP *= -4 * (-F) / abs(F)


def Im_E_1(t):
    Integrand = adia_eng(tp_1 + 1j*t, to_LZ(H, F))
    return Integrand.imag


# integral of phase term
ll_Im_E_1 = 0  # lower limit
ul_Im_E_1 = zero_approx  # upper limit
phase_term1, _ = quad(Im_E_1, ll_Im_E_1, ul_Im_E_1)
phase_term1 *= (-F) / abs(F)


def Im_E_2(t):
    Integrand = adia_eng(tp_2 + 1j*t, to_LZ(H, F))
    return Integrand.imag


# integral of phase term
ll_Im_E_2 = 0  # lower limit
ul_Im_E_2 = zero_approx  # upper limit
phase_term2, _ = quad(Im_E_2, ll_Im_E_2, ul_Im_E_2)
phase_term2 *= (-F) / abs(F)


def E_3(t):
    Integrand = adia_eng(t, to_LZ(H, F))
    return Integrand.real


# integral of phase term
ll_E_3 = tp_1  # lower limit
ul_E_3 = tp_2  # upper limit
phase_term3, _ = quad(E_3, ll_E_3, ul_E_3)
phase_term3 *= (-F) / abs(F)
print("dynamical phase: ", phase_term3 % (2*math.pi))

# 各時間における波動関数を算出
OP_array = calculate_occupation_probability(H, t_i, t_f, n)

# 終時間における状態0の占有確率
phase = phase_term2 - phase_term1 + phase_term3
P_f_adia = 4 * math.exp(TP) * math.cos(phase)**2
# occupation probability (adiabatic)
P_f_HS = (4 * math.exp(TP) * (1 - math.exp(TP)) * math.cos(phi_s + phase)**2)
# occupation probability (heuristic solution)

# 出力用プログラム
# 値を表示する
dic = {
    'eps_0': eps_0,
    'D_z': D_z,
    'D_y': D_y,
    'P_TLZ': math.exp(TLZ),
    'P_TP': math.exp(TP),
    'P_f_adiabatic': P_f_adia,
    'P_f_HS1': P_f_HS,
    'P_f_num': OP_array[-1],
}
ll = max([len(mm) for mm in dic.keys()])
for mm, ii in dic.items():
    print(f'{mm:{ll}} : {ii}')

# %%
# グラフ表示
P_TP = math.exp(TP)
P_TLZ = math.exp(TLZ)
P_f_adia += t_eval*0
P_f_HS += t_eval*0
P_TP += t_eval*0
P_TLZ += t_eval*0
plt.plot(t_eval, OP_array, label="numerical", color="tab:blue")
# plt.plot(t_eval, P_f_adia, label="adiabatic(24)")
plt.plot(t_eval, P_f_HS, label="theoretical (2nd transition)", color="tab:green")
plt.plot(t_eval, P_TP, label="theoretical (1st transition)", color="tab:red")
plt.plot(t_eval, P_TLZ, label="first transition (Oka's function)", linestyle=":", color="tab:orange")
plt.xlim([-3, 3])
plt.ylim([-0.1, 1.1])
plt.xlabel(r"time $t$")
plt.ylabel(r"occupation probability $P$")
plt.title(rf"$\varepsilon_0 = {eps_0}, \Delta_z = {D_z}, \Delta_y = {eps_0**2 * (4 * D_y / eps_0**2) / 4:.0f}, \omega = {-F}$")
plt.legend()
plt.show()
