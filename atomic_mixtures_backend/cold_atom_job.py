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

"""Job for cold atom instances."""
from typing import Dict

import time
import requests

from qiskit.providers import JobV1 as Job
from qiskit.providers import JobTimeoutError, JobError
from qiskit.providers import BackendV1 as Backend
from qiskit.providers import JobStatus
from qiskit.result import Result


class ColdAtomJob(Job):

    def __init__(self, backend: Backend, job_id: str):
        """

        Args:
            backend: The backend on which the job was run.
            job_id: The ID of the job.
        """
        super().__init__(backend, job_id)

    def _wait_for_result(self, timeout: float = None, wait: float = 5.0) -> Dict:
        """
        Query the backend to get the result.

        Args:
            timeout:
            wait:

        Returns:
            result dictionary formatted according to Qiskit schemas.
        """
        token = self._backend.access_token
        start_time = time.time()

        header = {
            "access_token": token,
            "SDK": "qiskit"
        }

        while True:
            elapsed = time.time() - start_time
            if timeout and elapsed >= timeout:
                raise JobTimeoutError('Timed out waiting for result')

            params = {'job_id': self._job_id, 'access_token': token}
            result = requests.get(self._backend.url, params=params, headers=header).json()

            if result['status'] == 'finished':
                break
            if result['status'] == 'error':
                raise JobError('API returned error:\n' + str(result))
            time.sleep(wait)

        return result

    def result(self, timeout: float = None, wait: float = 5.0) -> Result:
        """Retrieve a result from the backend."""
        result_dict = self._wait_for_result(timeout, wait=wait)

        return Result.from_dict(result_dict)

    def status(self):
        header = {
            "access_token": self._backend.access_token,
            "SDK": "qiskit"
        }
        result = requests.put(self._backend.url + '/status',
                              json={'job_id': self._job_id,
                                    'access_token': self._backend.access_token},
                              headers=header)

        code = result.status_code

        print(result)
        print(code)

        if code == 100:
            status = JobStatus.RUNNING
        elif code == 200:
            status = JobStatus.DONE
        elif code in [201, 202]:
            status = JobStatus.INITIALIZING
        else:
            status = JobStatus.ERROR
        return status

    def cancel(self):
        pass

    def submit(self):
        pass
