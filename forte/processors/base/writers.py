# Copyright 2019 The Forte Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Writers are simply processors with the side-effect to write to the disk.
This file provide some basic writer implementations.
"""
import gzip
import logging
import os
from abc import abstractmethod, ABC
import json
from typing import Optional

from texar.torch.hyperparams import HParams

from forte.common.resources import Resources
from forte.data.base_pack import PackType
from forte.processors.base.base_processor import BaseProcessor
from forte.utils.utils_io import maybe_create_dir, ensure_dir

logger = logging.getLogger(__name__)

__all__ = [
    'JsonPackWriter',
]


class JsonPackWriter(BaseProcessor[PackType], ABC):
    def __init__(self):
        super().__init__()
        self.zip_pack: bool = False
        self.indent: Optional[int] = None

    def initialize(self, resources: Resources, configs: HParams):
        super(JsonPackWriter, self).initialize(resources, configs)

        if not configs.output_dir:
            raise NotADirectoryError('Root output directory is not defined '
                                     'correctly in the configs.')

        if not os.path.exists(configs.output_dir):
            os.makedirs(configs.output_dir)

        self.zip_pack = configs.zip_pack
        self.indent = configs.indent

    @abstractmethod
    def sub_output_path(self, pack: PackType) -> str:
        r"""Allow defining output path using the information of the pack.

        Args:
            pack: The input datapack.
        """
        raise NotImplementedError

    @staticmethod
    def default_configs():
        r"""This defines a basic ``Hparams`` structure.
        """
        return {
            'output_dir': None,
            'zip_pack': False,
            'indent': None,
        }

    def _process(self, input_pack: PackType):
        sub_path = self.sub_output_path(input_pack)
        if sub_path == '':
            raise ValueError(
                "No concrete path provided from sub_output_path.")

        maybe_create_dir(self.configs.output_dir)
        p = os.path.join(self.configs.output_dir, sub_path)

        ensure_dir(p)

        out_str: str = input_pack.serialize()

        if self.configs.indent:
            out_str = json.dumps(
                json.loads(out_str), indent=self.configs.indent)

        if self.configs.zip_pack:
            with gzip.open(p + '.gz', 'wt') as out:
                out.write(out_str)
        else:
            with open(p, 'w') as out:
                out.write(out_str)
