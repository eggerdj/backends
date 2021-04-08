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

from typing import Union
from qiskit.providers import (
    BackendV1,
    BaseBackend,
    JobTimeoutError,
    JobError,
    JobStatus,
)
from qiskit.providers import JobV1 as Job
from qiskit.result import Result

import json


class ColdAtomJob(Job):
    def __init__(self, backend: Union[BackendV1, BaseBackend], job_id: str):
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

        header = {"access_token": token, "SDK": "qiskit"}

        while True:
            elapsed = time.time() - start_time
            if timeout and elapsed >= timeout:
                raise JobTimeoutError("Timed out waiting for result")

            params = {"job_id": self._job_id, "access_token": token}
            result = requests.get(
                self._backend.url + "/get_job_result/", params=params, headers=header
            ).json()

            if result["status"] == "finished":
                break
            if result["status"] == "error":
                raise JobError("API returned error:\n" + str(result))

            time.sleep(wait)

        return result

    def result(self, timeout: float = None, wait: float = 5.0) -> Result:
        """Retrieve a result from the backend."""
        result_dict = self._wait_for_result(timeout, wait=wait)

        return Result.from_dict(result_dict)

    def status(self):
        header = {"access_token": self._backend.access_token, "SDK": "qiskit"}

        # TODO: adjust this payload
        if not self.job_id():
            raise Exception

        payload = {"job_id": self.job_id()}

        r = requests.get(
            self._backend.url + "/get_job_status/", params={"json": json.dumps(payload)}
        )

        status_string = r.json()["status"]

        # If the backend can not be reached return ERROR as a status
        if r.status_code != 200:
            status = JobStatus.ERROR
        elif status_string == "initializing":
            status = JobStatus.INITIALIZING
        elif status_string == "queued":
            status = JobStatus.QUEUED
        elif status_string == "validating":
            status = JobStatus.VALIDATING
        elif status_string == "running":
            status = JobStatus.RUNNING
        elif status_string == "cancelled":
            status = JobStatus.CANCELLED
        elif status_string == "done":
            status = JobStatus.DONE
        else:
            status = JobStatus.ERROR

        return status

    # TODO: Make detail key of response retrievable

    def cancel(self):
        pass

    def submit(self):
        pass
