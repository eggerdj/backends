# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from qiskit.circuit import Gate


class SpinsRXGate(Gate):
    r"""Rotation of the collective spin of a cold atomic BEC around the x-axis

    **Circuit symbol:**

    .. parsed-literal::

             ┌───────────┐
        q_0: ┤ Rx(omega) ├
             └───────────┘
    """
    def __init__(self, omega, label=None):
        """Create new RX gate."""
        super().__init__('rx', 1, [omega], label=label)


class SpinsRZGate(Gate):
    r"""Rotation of the collective spin of a cold atomic BEC around the z-axis

    **Circuit symbol:**

    .. parsed-literal::

             ┌───────────┐
        q_0: ┤ Rz(delta) ├
             └───────────┘

    """

    def __init__(self, delta, label=None):
        """Create new RZ gate."""
        super().__init__('rz', 1, [delta], label=label)


class OneAxisTwistingGate(Gate):
    r"""Evolution of a coherent spin under the one-axis-twisting Hamiltonian generated by Lz^2'.

    **Circuit symbol:**

    .. parsed-literal::

             ┌──────────┐
        q_0: ┤ OAT(chi) ├
             └──────────┘
    """

    def __init__(self, chi, label=None):
        """Create new OAT gate."""
        super().__init__('OAT', 1, [chi], label=label)


class GeneralRotation(Gate):
    r"""Evolution of a coherent spin under the one-axis-twisting Hamiltonian generated by
    the Hamiltonian H = chi*Lz^2 + delta*Lz + omega*Lx
    """

    def __init__(self, chi, delta, omega, label=None):
        """Create new general rotation gate."""
        super().__init__('rot', 1, [chi, delta, omega], label=label)
