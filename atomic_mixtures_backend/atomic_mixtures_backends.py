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

from abc import ABC
import requests
from typing import Union, List

from qiskit.providers import BackendV1 as Backend
from qiskit.providers.models import BackendConfiguration
from qiskit.providers import Options
from qiskit import QuantumCircuit, QiskitError

from circuit_to_cold_atom import circuit_to_cold_atom
from cold_atom_job import ColdAtomJob


class AtomicMixtureBackend(Backend, ABC):
    """Abstract base class for atomic mixture backends."""

    def get_empty_circuit(self) -> QuantumCircuit:
        """
        Convenience  function  to set -up an  empty  circuit  with the  right  QuantumRegisters.

        Returns:
            qc: A quantum circuit ready to use for atomic mixture experiments.

        """
        try:
            num_wires = self.configuration().to_dict()['n_qubits']
            species1, species2, = self.configuration().to_dict()['atomic_species']
        except NameError:
            raise QiskitError("backend needs to be initialized with config file first")

        assert (isinstance(num_wires, int) and num_wires % 2 == 0), \
            "num_wires should be even integer"

        from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit

        reg1 = QuantumRegister(num_wires/2, species1)
        reg2 = QuantumRegister(num_wires/2, species2)
        class_reg = ClassicalRegister(num_wires, 'c2')
        empty_circuit = QuantumCircuit(reg1, reg2, class_reg)

        return empty_circuit

    def draw(self, qc: QuantumCircuit):
        """
         Modified circuit drawer to better display atomic mixture quantum  circuits.

        Args:
            qc: The quantum circuit to draw.
        """
        # TODO Implement here
        pass


class AtomicMixtureDevice(AtomicMixtureBackend):
    """Atomic mixture hardware backend."""

    def __init__(self, provider):
        """
        Setting up the backend by obtaining the configuration dict from its url
        """
        self.url = 'http://127.0.0.1:5000/mixtures'

        # Get the config from the url
        r = requests.get(url=self.url + '/config')

        super().__init__(
            configuration=BackendConfiguration.from_dict(r.json()),
            provider=provider)

    @property
    def access_token(self) -> str:
        """Returns: the access token used."""
        return self.provider().access_token

    @classmethod
    def _default_options(cls) -> Options:
        return Options(shots=1)

    def run(self, circuits: Union[QuantumCircuit, List[QuantumCircuit]], **kwargs) -> ColdAtomJob:
        """Run a quantum circuit or list of quantum circuits."""
        header = {'access_token': self.access_token, 'SDK': 'qiskit'}

        data = circuit_to_cold_atom(circuits, self)

        res = requests.put(self.url, json=data, headers=header)
        res.raise_for_status()
        response = res.json()

        if 'job_id' not in response:
            raise Exception

        return ColdAtomJob(self, response['job_id'])


class AtomicMixtureSimulator(AtomicMixtureBackend):
    """Atomic mixture mean field simulator."""

    def __init__(self, provider):
        self.url = 'http://127.0.0.1:5000/mixtures/simulator'

        # Get the config from the url
        r = requests.get(url=self.url + '/config')

        super().__init__(
            configuration=BackendConfiguration.from_dict(r.json()),
            provider=provider)

    @classmethod
    def _default_options(cls):
        return Options(shots=1)

    def run(self, circuits, **kwargs):
        """Run a simulation job. TODO"""
        pass
