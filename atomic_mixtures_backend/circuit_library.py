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

from qiskit.circuit.gate import Gate


class MixturesRXGate(Gate):
    r"""Rotation of the collective spin of a cold atomic BEC around the x-axis

    **Circuit symbol:**

    .. parsed-literal::

             ┌───────┐
        q_0: ┤ Rx(ϴ) ├
             └───────┘

    .. math::

        RX(\theta) = exp(-i \frac{\theta}{4} (\hat{b}^\dagger_0 \hat{b}_1 + \hat{b}^\dagger_1\hat{b}_0))

    """

    def __init__(self, theta, label=None):
        """Create new RX gate."""
        super().__init__('rx', 1, [theta], label=label)

    def inverse(self):
        r"""Return inverted RX gate.

        :math:`RX(\theta)^{\dagger} = RX(-\theta)`
        """
        return MixturesRXGate(-self.params[0])


class MixturesRYGate(Gate):
    r"""Rotation of the collective spin of a cold atomic BEC around the y-axis

    **Circuit symbol:**

    .. parsed-literal::

             ┌───────┐
        q_0: ┤ Ry(ϴ) ├
             └───────┘

    .. math::

        RX(\theta) = exp(-i \frac{\theta}{4} (\hat{b}^\dagger_0 \hat{b}_1 + \hat{b}^\dagger_1\hat{b}_0))

    """

    def __init__(self, theta, label=None):
        """Create new RY gate."""
        super().__init__('ry', 1, [theta], label=label)

    def inverse(self):
        r"""Return inverted RY gate.

        :math:`RY(\theta)^{\dagger} = RY(-\theta)`
        """
        return MixturesRYGate(-self.params[0])


class MixturesSCCdrift(Gate):
    r"""Evolution of a cold atomic experiment under a many-body
    spin-changing collision (SCC) Hamiltonian
     for some given time tau (in milliseconds).

    **Circuit symbol:**

    .. parsed-literal::

             ┌────────┐
        q_0: ┤ SCC(τ) ├
             └────────┘
    """

    def __init__(self, num_wires, tau, label=None):
        """Create new SCC gate."""

        assert (isinstance(num_wires, int) and num_wires % 2 == 0), \
            "num_wires should be even integer"

        super().__init__('delay', num_wires, [tau], label=label)


class MixturesRamanCoupling(Gate):
    r"""coupling of the spin states of neighbouring sites

    **Circuit Symbol:**

    .. parsed-literal::

        q_0: ───■────
                │C(Ω)
        q_1: ───■────
    """

    def __init__(self, omega, label=None):
        """Create new coupling gate."""
        super().__init__('couple', 2, [omega], label=label)




