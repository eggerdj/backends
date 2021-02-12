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

from typing import Callable

from qiskit.providers import BackendV1 as Backend
from qiskit.providers.providerutils import filter_backends
from qiskit.providers.exceptions import QiskitBackendNotFoundError
from atomic_mixtures_backends import AtomicMixtureDevice, AtomicMixtureSimulator


class ColdAtomProvider:
    """
    Provider for cold atom backends.
    
    Typical usage is:
    .. code-block:: python
        from qiskit_cold_atom_provider import ColdAtomProvider
        ca = ColdAtomProvider('MY_TOKEN')
        backend = ca.backends.na_li
    where `'MY_TOKEN'` is the access token.
    Attributes:
        access_token (str): The access token.
        name (str): Name of the provider instance.
        backends (BackendService): A service instance that allows
                                   for grabbing backends.
    """

    def __init__(self, access_token: str):
        super().__init__()

        self.access_token = access_token
        self.name = 'cold_atom_provider'

        # Populate the list of backends
        self.backends = BackendService([AtomicMixtureSimulator(provider=self),
                                        AtomicMixtureDevice(provider=self)])

    def __str__(self):
        return "<ColdAtomProvider(name={})>".format(self.name)

    def __repr__(self):
        return self.__str__()

    def get_backend(self, name: str = None, **kwargs) -> Backend:
        """Return a single backend matching the specified filtering.
        Args:
            name: name of the backend.
            **kwargs: dict used for filtering.
        Returns:
            backend: a backend matching the filtering.
        Raises:
            QiskitBackendNotFoundError: if no backend could be found or
                more than one backend matches the filtering criteria.
        """
        backends = self.backends(name, **kwargs)
        if len(backends) > 1:
            raise QiskitBackendNotFoundError('More than one backend matches criteria.')
        if not backends:
            raise QiskitBackendNotFoundError('No backend matches criteria.')

        return backends[0]

    def __eq__(self, other):
        """Equality comparison.
        By default, it is assumed that two `Providers` from the same class are
        equal. Subclassed providers can override this behavior.
        """
        return type(self).__name__ == type(other).__name__


class BackendService:
    """A service class that allows for autocompletion
    of backends from provider.
    """

    def __init__(self, backends):
        """Initialize service
        Parameters:
            backends (list): List of backend instances.
        """
        self._backends = backends
        for backend in backends:
            setattr(self, backend.name(), backend)

    def __call__(self, name: str = None, filters: Callable = None, **kwargs):
        """A listing of all backends from this provider.
        Parameters:
            name: The name of a given backend.
            filters: A filter function.
        Returns:
            list: A list of backends, if any.
        """
        # pylint: disable=arguments-differ
        backends = self._backends
        if name:
            backends = [
                backend for backend in backends if backend.name() == name]

        return filter_backends(backends, filters=filters, **kwargs)
