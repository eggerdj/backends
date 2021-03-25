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

import json


class BosonicBackend(Backend, ABC):
    """Abstract base class for atomic mixture backends."""

    def get_empty_circuit(self) -> QuantumCircuit:
        """
        Convenience  function  to set up an  empty  circuit  with the  right  QuantumRegisters.
        For each atomic species specified in the config file, one quantum register is added to the circuit.

        Returns:
            qc: A quantum circuit ready to use for atomic mixture experiments.

        """
        config = self.configuration().to_dict()

        try:
            num_wires = config['n_qubits']
            num_species = len(config['atomic_species'])

        except NameError:
            raise QiskitError("backend needs to be initialized with config file first")

        if not (isinstance(num_wires, int) and num_wires % num_species == 0):
            raise QiskitError("num_wires {num_wires} must be multiple of num_species {num_species}")

        from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit

        qregs = [QuantumRegister(num_wires/num_species, species) for species in config['atomic_species']]

        class_reg = ClassicalRegister(num_wires, 'c{}'.format(num_wires))
        empty_circuit = QuantumCircuit(*qregs, class_reg)

        return empty_circuit

    def draw(self, qc: QuantumCircuit):
        """
         Modified circuit drawer to better display atomic mixture quantum  circuits.

        Args:
            qc: The quantum circuit to draw.
        """
        # TODO Implement here
        pass


class CoherentSpinsDevice(BosonicBackend):
    """Atomic mixture hardware backend."""

    def __init__(self, provider):
        self.url = 'http://localhost:9000/shots'

        # Get the config from the url
        r = requests.get(url=self.url + '/config')

        super().__init__(
            configuration=BackendConfiguration.from_dict(r.json()),
            provider=provider)

    @classmethod
    def _default_options(cls) -> Options:
        return Options(shots=1)

    @property
    def access_token(self) -> str:
        """Returns: the access token used."""
        return self.provider().access_token

    def run(self, circuits: Union[QuantumCircuit, List[QuantumCircuit]], **kwargs) -> ColdAtomJob:
        """Run a quantum circuit or list of quantum circuits."""
        header = {'access_token': self.access_token, 'SDK': 'qiskit'}

        payload = circuit_to_cold_atom(circuits, self)

        res = requests.post(self.url + '/upload/', data={'json': json.dumps(payload)})  # headers=header)
        res.raise_for_status()
        response = res.json()

        print(type(response))
        print(response)

        if 'job_id' not in response:
            raise Exception

        return ColdAtomJob(self, response['job_id'])


class AtomicMixtureDevice(BosonicBackend):
    """Atomic mixture hardware backend."""

    def __init__(self, provider):
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


class AtomicMixtureSimulator(BosonicBackend):
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


class CoherentSpinsQubits(BosonicBackend):
    """Backend to describe a cold atom hardware using qubits encoded in coherent spins of trapped BECs
    as proposed in https://arxiv.org/pdf/2010.15923."""

    _DEFAULT_CONFIGURATION = {
        'backend_name': 'coherent_spin_qubits',
        'backend_version': '0.0.1',
        'n_qubits': 5,
        'simulator': False,
        'local': False,
        # all-to-all coupling:
        'coupling_map': [[0, 1], [0, 2], [1, 2], [0, 3], [1, 3], [2, 3], [0, 4], [1, 4], [2, 4], [3, 4], [1, 0],
                         [2, 0], [2, 1], [3, 0], [3, 1], [3, 2], [4, 0], [4, 1], [4, 2], [4, 3]],
        'description': 'Cold atom qubits encoded in coherent spins of trapped BECs',
        'basis_gates': ['id', 'rx', 'rz', 'cz'],
        'memory': False,
        'max_shots': 1000,
        'open_pulse': False,
        'gates': [],
        'conditional': False,
    }

    def __init__(self, provider=None, config_dict=None):

        if config_dict is None:
            config_dict = self._DEFAULT_CONFIGURATION

        super().__init__(
            configuration=BackendConfiguration.from_dict(config_dict),
            provider=provider)

    @classmethod
    def _default_options(cls):
        return Options(shots=1)

    def run(self, circuits, **kwargs):
        """Run a simulation job. TODO"""
        pass
