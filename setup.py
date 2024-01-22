# -*- coding: utf-8 -*-
"""
Created on Sun Feb 20 16:39:55 2022

@author: juntong
"""

import setuptools

setuptools.setup(
    name="StitchImage",
    version="0.1.4",
    description="a tool can stitch images",
    # install_requires = ["setuptools", "PIL", "numpy"],
    package_data={'': ["README.md", "LICENSE"],
                  "StitchImage": ["*.json"]},
    packages=setuptools.find_packages(),
)
