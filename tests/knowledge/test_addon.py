#
# SPDX-FileCopyrightText: 2020 Splunk, Inc. <sales@splunk.com>
# SPDX-License-Identifier: Apache-2.0
#
#
import pytest

from pytest_splunk_addon.standard_lib.addon_basic import Basic


class Test_App(Basic):
    def empty_method(self):
        pass
