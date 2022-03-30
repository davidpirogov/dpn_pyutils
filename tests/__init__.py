#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

# =============================================
# check min, python version
if sys.version_info < (3, 8):
    raise SystemError("dpn_pyutils requires Python version >= 3.8")
