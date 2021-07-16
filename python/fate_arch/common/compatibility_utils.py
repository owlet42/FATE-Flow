#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import typing

from fate_arch.common import WorkMode, Backend, FederatedMode
from fate_arch.computing import ComputingEngine
from fate_arch.federation import FederationEngine
from fate_arch.storage import StorageEngine
from fate_arch.relation_ship import Relationship
from fate_arch.common import EngineType


def engines_compatibility(work_mode: typing.Union[WorkMode, int] = WorkMode.STANDALONE,
                          backend: typing.Union[Backend, int] = Backend.EGGROLL, **kwargs):
    keys = ["computing", "federation", "storage", "federated_mode"]
    engines = {}
    for k in keys:
        if kwargs.get(k) is not None:
            engines[k] = kwargs[k]
    if kwargs.get("computing") is None and (work_mode is None or backend is None):
        raise RuntimeError("must provide computing engine parameters or work_mode and backend parameters")
    if kwargs.get("computing") is None and kwargs.get("federation") is None:
        if isinstance(work_mode, int):
            work_mode = WorkMode(work_mode)
        if isinstance(backend, int):
            backend = Backend(backend)
        if backend == Backend.EGGROLL:
            if work_mode == WorkMode.CLUSTER:
                values = (ComputingEngine.EGGROLL, FederationEngine.EGGROLL)
            else:
                values = (ComputingEngine.STANDALONE, FederationEngine.STANDALONE)
        elif backend == Backend.SPARK_RABBITMQ:
            values = (ComputingEngine.SPARK, FederationEngine.RABBITMQ)
        elif backend == Backend.SPARK_PULSAR:
            values = (ComputingEngine.SPARK, FederationEngine.PULSAR)
        else:
            raise RuntimeError(f"unable to find default engines by work_mode: {work_mode} backend: {backend}")

        engines.update(dict(zip(keys[:2], values)))

    # set default storage engine and federation engine by computing engine
    for t in {EngineType.STORAGE, EngineType.FEDERATION}:
        if engines.get(t) is None:
            # use default relation engine
            engines[t] = Relationship.Computing[engines[EngineType.COMPUTING]][t]["default"]

    # set default federated mode by federation engine
    if engines.get("federated_mode") is None:
        if engines[EngineType.FEDERATION] == FederationEngine.STANDALONE:
            engines["federated_mode"] = FederatedMode.SINGLE
        else:
            engines["federated_mode"] = FederatedMode.MULTIPLE

    return engines
