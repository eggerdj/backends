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

"""module to convert cold atom circuits to dictionaries"""

from typing import Union, List

from qiskit import QuantumCircuit, QiskitError
from qiskit.providers import BackendV1 as Backend


def circuit_to_data(circuit: QuantumCircuit, backend):
    # pylint: disable=missing-return-type-doc
    """
    helper function that converts a QuantumCircuit into a list of symbolic instructions
    as required by the Json format which is sent to the

    Args:
    circuits: The given QuantumCircuit
    backend: The backend on which the circuit should be run

    Returns:
        A list of tuples describing the instructions in the circuit

    Raises:
        QiskitError: If the backend does not support an instruction given in the circuit
    """

    try:
        native_gates = {_.name: _.coupling_map for _ in backend.configuration().gates}
        native_instructions = backend.configuration().supported_instructions
    except NameError as name_error:
        raise QiskitError(
            "backend needs to be initialized with config file first"
        ) from name_error

    instructions = []

    for inst in circuit.data:

        name = inst[0].name

        # get the correct wire indices of the instruction with respect
        # to the total index of the qubit objects in the circuit
        wires = [circuit.qubits.index(qubit) for qubit in inst[1]]

        params = []
        try:
            for param in inst[0].params:
                params.append(float(param))
        except TypeError as type_error:
            raise QiskitError(
                "Cannot run circuit with unbound parameters."
            ) from type_error

        # check if instruction is supported by the backend
        if name not in native_instructions:
            raise QiskitError(f"{backend.name()} does not support {name}")

        # for the gates, check whether coupling map fits
        if name in native_gates:
            couplings = native_gates[name]
            if wires not in couplings:
                raise QiskitError(
                    f"coupling {wires} not supported for gate "
                    f"{name} on {backend.name()}; possible couplings: {couplings}"
                )

        instructions.append((name, wires, params))

    return instructions


def circuit_to_cold_atom(
    circuits: Union[List[QuantumCircuit], QuantumCircuit],
    backend: Backend,
    shots: int = 60,
) -> dict:
    """
    Converts a circuit to a JSon payload.

    Args:
        circuits: The circuits that need to be run.
        backend: The backend on which the circuit should be run
        shots: The number of shots for each circuit.

    Returns:
        A list of dicts.

    Raises:
        QiskitError: If the maximum number of experiments or shots specified by the backend is exceeded
    """
    if isinstance(circuits, QuantumCircuit):
        circuits = [circuits]

    max_circuits = backend.configuration().max_experiments
    max_shots = backend.configuration().max_shots

    # check for number of experiments allowed by the backend
    if len(circuits) > max_circuits:
        raise QiskitError(
            f"{backend.name()} allows for max. {max_circuits} different circuits; "
            f"{len(circuits)} circuits were given "
        )

    # check for number of shots allowed by the backend
    if shots > max_shots:
        raise QiskitError(
            f"{backend.name()} allows for max. {max_shots} shots per circuit; "
            f"{shots} shots were requested"
        )

    experiments = {}
    for idx, circuit in enumerate(circuits):
        experiments["experiment_%i" % idx] = {
            "instructions": circuit_to_data(circuit, backend),
            "shots": shots,
            "num_wires": circuit.num_qubits,
        }

    return experiments
