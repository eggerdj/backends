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

from typing import Dict, Tuple
from flask import Flask, json, request
from flask_api import status
import uuid
from abc import ABC, abstractmethod

MIXTURES_NAME = 'cold_atom_mixtures'
MIXTURES_VERSION = '0.0.1'

# configuration dictionary of the device backend
mixtures_configuration = {
    'backend_name': MIXTURES_NAME,
    'backend_version': MIXTURES_VERSION,
    'url': 'http://127.0.0.1:5000/mixtures',
    'simulator': False,
    'local': False,
    'coupling_map': [[0, 1]],
    'description': 'Setup of an atomic mixtures experiment with one \
    trapping site and two atomic species, namely Na and Li.',
    'basis_gates': ['rx', 'delay'],
    'atomic_species': ['na', 'li'],
    'gates': [
        {'name': 'delay',
         'parameters': ['tau', 'delta'],
         'qasm_def': 'gate delay(tau, delta) {}',
         'coupling_map': [[0, 1]],
         'description': 'evolution under SCC Hamiltonian for time tau'},
        {'name': 'rx',
         'parameters': ['theta'],
         'qasm_def': 'gate rx(theta) {}',
         'coupling_map': [[0]],
         'description': 'Rotation of the sodium spin'}
    ],
    'supported_instructions': [
        'delay',
        'rx',
        'measure',
        'barrier'
    ],
    'memory': True,
    'n_qubits': 2,
    'conditional': False,
    'max_shots': 60,
    'max_experiments': 3,
    'open_pulse': False,
    'credits_required': False,
}

# configuration dictionary of the simulator backend
mixtures_sim_configuration = {
    'backend_name': 'atomic_mixtures_meanfield_simulator',
    'backend_version': '0.0.1',
    'url': 'http://127.0.0.1:5000/mixtures/simulator',
    'simulator': True,
    'local': False,
    'coupling_map': None,
    'description': 'Cold atom simulator',
    'basis_gates': ['delay', 'couple', 'rx', 'ry'],
    'atomic_species': ['na', 'li'],
    'memory': False,
    'n_qubits': 8,
    'conditional': False,
    'max_shots': 60,
    'max_experiments': 1,
    'open_pulse': False,
    'gates': [
        {'name': 'delay',
         'parameters': ['tau', 'delta'],
         'qasm_def': 'gate delay(tau, delta) {}',
         'coupling_map': [[0, 1, 2, 3, 4, 5, 6, 7]],
         'description': 'evolution under SCC Hamiltonian for time tau'},
        {'name': 'couple',
         'parameters': ['omega'],
         'qasm_def': 'gate couple(omega) {}',
         'coupling_map': [[4, 5], [5, 6], [6, 7]],
         'description': 'raman-assisted tunnel coupling of Li states on neighbouring sites'},
        {'name': 'rx',
         'parameters': ['theta'],
         'qasm_def': 'gate rx(theta) {}',
         'coupling_map': [[0], [1], [2], [3], [4], [5], [6], [7]],
         'description': 'x-Rotation of the spin'},
        {'name': 'ry',
         'parameters': ['theta'],
         'qasm_def': 'gate ry(theta) {}',
         'coupling_map': [[0], [1], [2], [3], [4], [5], [6], [7]],
         'description': 'y-Rotation of the spin'}
    ],
    'supported_instructions': [
        'delay',
        'couple',
        'rx',
        'ry',
        'measure',
        'barrier'
    ],
}


class ColdAtomSetup(ABC):
    """Base class for Mock Setup"""
    def __init__(self):
        pass

    @abstractmethod
    def run_qiskit_job(self, job_config: Dict) -> Tuple[str, str]:
        """Runs a Qiskit job and returns a Job ID."""

    @abstractmethod
    def get_qiskit_job(self, job_id: str, token: str) -> Dict:
        """Gets the result of a Qiskit job."""


class MockSetup(ColdAtomSetup):
    """Mock class to demonstrate the logic."""

    def run_qiskit_job(self, job_config: Dict) -> Tuple[str, str]:
        """Runs a Qiskit job and returns a Job ID."""
        return str(uuid.uuid1()), 'initializing'

    def get_qiskit_job(self, job_id: str, token: str) -> Dict:
        """Gets the result of a Qiskit job."""
        return {}


api = Flask(__name__)


@api.route('/mixtures/config', methods=['GET'])
def get_mixtures():
    return json.dumps(mixtures_configuration)


@api.route('/mixtures/simulator/config', methods=['GET'])
def get_mixtures_simulator():
    return json.dumps(mixtures_sim_configuration)


@api.route('/mixtures', methods=['PUT'])
def handle_mixtures_run():
    data = request.get_json()

    print('data')
    print(data)

    job_id, job_status = MockSetup().run_qiskit_job(data)

    return {'job_id': job_id, 'status': job_status}


@api.route('/mixtures/simulator', methods=['PUT'])
def handle_mixtures_simulator_run():
    data = request.get_json()
    print(data)

    return {'job_id': ''}


@api.route('/mixtures', methods=['GET'])
def handle_mixtures_result():
    """Method to retrieve the result from the backend."""

    job_id = request.args.get('job_id')
    token = request.args.get('access_token')

    # hardcoded some result_dict to showcase the temporary data structure.
    result_dict = {
        'backend_name': MIXTURES_NAME,
        'backend_version': MIXTURES_VERSION,
        'job_id': job_id,
        'qobj_id': '1234',
        'success': 'true',
        'header': {},
        'status': 'finished',
        'results': [
            {
                "header": {"name": "experiment_0"},
                "shots": 3,
                "success": True,
                "meas_return": "single",
                "meas_level": 1,
                "data": {      # slot 1 (Na)      # slot 2 (Li)
                    "memory": [[[90012.,  9988.], [5100., 4900.]],  # Shot 1
                               [[89900., 10100.], [5000., 5000.]],  # Shot 2
                               [[90000., 10000.], [5050., 4950.]]]  # Shot 3
                }
            }
        ]
    }

    return result_dict


@api.route('/mixtures/status', methods=['PUT'])
def handle_mixtures_status():
    data = request.get_json()

    job_status = 'finished'
    status_code = status.HTTP_200_OK

    return {'job_id': data['job_id'], 'status': job_status}, status_code


if __name__ == '__main__':
    api.run()
