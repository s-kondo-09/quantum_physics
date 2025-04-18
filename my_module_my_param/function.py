import numpy as np


def q(t, F):
    """
    define parameter sweep

    q = adiabatic parameter * time

    Args:
        t (float): time
        F (float): sweep speed (adiabatic parameter)

    Returns:
        float: parameter sweep
    """
    return -F * t


def phi_dot(t, Ham, eps=0):
    """
    define derivative of azimuthal angle

    Args:
        t (complex): time
        eps (float): epsilon

    Returns:
        float: derivative of azimuthal angle
    """
    H_x = Ham(t, "x")
    H_y = Ham(t, "y")
    H_x_dot = Ham(t, "x_dot")
    H_y_dot = Ham(t, "y_dot")

    num = -H_x * H_y_dot + H_x_dot * H_y
    den = H_x**2 + H_y**2
    return num / (den + eps)


def adia_eng(t, Ham, ut=False, real=False, F=None):
    """define adiabatic energy

    Args:
        t (complex): time
        Ham (function): Hamiltonian
        ut (bool, optional): unitary transformed. Defaults to False.
        real (bool, optional): real part. Defaults to False.
        F (float, optional): sweep speed. If `ut=True`, this parameter must be specified. Defaults to None.

    Returns:
        complex: adiabatic energy
    """
    H_x = Ham(t, "x")
    H_y = Ham(t, "y")
    H_z = Ham(t, "z")
    phi_d = phi_dot(t, Ham)

    if ut:
        if F is None:
            raise ValueError("if `ut` is `True`, the argument 'F' must be specified.")
        else:
            return np.sqrt(H_x**2 + H_y**2 + (H_z + 0.5 * (-F) * phi_d)**2)
    elif real:
        return np.sqrt(H_x**2 + H_y**2 + H_z**2).real
    else:
        return np.sqrt(H_x**2 + H_y**2 + H_z**2)


def eig_vec(t, Ham, s):
    """
    eigenvector

    Args:
        t (float): time
        Ham (function): Hamiltonian
        s (state): upper or lower

    Returns:
        array: eigenvector
    """
    H_x = Ham(t, "x", real=True)
    H_y = Ham(t, "y", real=True)
    H_z = Ham(t, "z", real=True)
    adia_energy = adia_eng(t, Ham, real=True)

    # lower stateを求めるときは断熱エネルギーを符号反転する
    if s == "lower":
        adia_energy = -adia_energy

    eig_vec = np.array([H_x - H_y * 1j, adia_energy - H_z])
    eig_vec /= np.linalg.norm(eig_vec)  # normalization
    return eig_vec


def adia_param(v, F, m, k):
    return (m - k * v * F / 4)**2 / (2 * abs(v) * abs(F))


def TLZ_theoretical(v, F, m, k):
    TLZ = -np.pi * (m + k * v * F / 4)**2 / (abs(v) * abs(F))
    return np.exp(TLZ)


def func_psi_module(t, Ham, var, h=1):
    """
    state vector

    (t_f)における系の状態ベクトル(psi(t_f))を求める関数です。
    psiの第1成分をa+ib, 第2成分をc*idとします。
    var[0]=a,var[1]=b, var[2]=c, var[3]=dとします。

    Args:
        t (float): time
        var (list): 状態ベクトルの各成分を要素とするlist
        h (float, optional): Dirac constant. Default to 1.

    Returns:
        list: 微分方程式
    """

    H_x = Ham(t, "x", real=True)
    H_y = Ham(t, "y", real=True)
    H_z = Ham(t, "z", real=True)

    dadt = (+1 / h) * (H_x * var[3] - H_y * var[2] + H_z * var[1])
    dbdt = (-1 / h) * (H_x * var[2] + H_y * var[3] + H_z * var[0])
    dcdt = (+1 / h) * (H_x * var[1] + H_y * var[0] - H_z * var[3])
    dddt = (-1 / h) * (H_x * var[0] - H_y * var[1] - H_z * var[2])

    return [dadt, dbdt, dcdt, dddt]


if __name__ == '__main__':
    print(q(1, 1))
