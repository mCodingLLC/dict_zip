#    Copyright 2022 MCODING, LLC.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
#    dict_zip module written and maintained
#    by James Murphy <james@mcoding.io>

import os
import glob
from setuptools import setup, Extension, find_packages


sources = glob.glob("src/dict_zip/*.c")
optimize_arg = "/O2" if os.name == "nt" else "-O3"
lto_arg = "/GL" if os.name == "nt" else "-flto"

dict_zip_extension = Extension(
    "dict_zip._dict_zip",
    sources=sources,
    extra_compile_args=[
        optimize_arg,
        lto_arg,
    ],
)

setup(ext_modules=[dict_zip_extension], packages=find_packages(exclude=["tests"]))
