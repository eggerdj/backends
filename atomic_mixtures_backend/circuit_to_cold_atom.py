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

"""converts a circuit to a JSon payload"""

from typing import Union, List

from qiskit import QuantumCircuit, QiskitError
from qiskit.providers import BackendV1


def circuit_to_data(circuit: QuantumCircuit, backend: BackendV1):
    """ helper function that converts a QuantumCircuit into a list of symbolic instructions
    as required by the Json format which is sent to the backend"""

    # Load the native gates that the backend supports form its configuration dict
    try:
        native_gates = {_.name: _.coupling_map for _ in backend.configuration().gates}
        native_instructions = backend.configuration().supported_instructions
    except NameError:
        raise QiskitError("backend needs to be initialized with config file first")

    instructions = []

    # validating all instructions in the circuit: Checking that the backend supports the instruction and that
    # the coupling maps of the gate fit the applied wire structure of the applied gates
    for inst in circuit.data:

        name = inst[0].name

        # get the correct wire indices of the instruction with respect
        # to the total index of the qubit objects in the circuit
        wires = [circuit.qubits.index(qubit) for qubit in inst[1]]

        params = []
        try:
            for param in inst[0].params:
                params.append(float(param))
        except TypeError:
            raise QiskitError('Cannot run circuit with unbound parameters.')

        # check if instruction is supported by the backend
        assert name in native_instructions, "{} does not support {}.".format(backend.name(), name)

        # for the gates, check whether coupling map fits
        if name in native_gates.keys():
            couplings = native_gates[name]
            assert wires in couplings, \
                "coupling {} not supported for gate {} on {}; possible couplings: {}"\
                .format(wires, name, backend.name(), couplings)

        instructions.append((name, wires, params))

    return instructions


def circuit_to_cold_atom(circuits: Union[List[QuantumCircuit], QuantumCircuit],
                         backend: BackendV1,
                         shots: int = 60):
    """
    Converts a circuit to a JSon payload.

    Args:
        circuits: The circuits that need to be run.
        backend: The backend on which the circuit should be run
        shots: The number of shots for each circuit.

    Returns:
        A list of dicts.
    """
    if isinstance(circuits, QuantumCircuit):
        circuits = [circuits]

    experiments = {}
    for idx, circuit in enumerate(circuits):
        experiments['experiment_%i' % idx] = {'data': circuit_to_data(circuit, backend),
                                              'shots': shots,
                                              'num_wires': circuit.num_qubits}

    return experiments
