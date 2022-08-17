# Copyright 2022 Penelope Valentine Gale
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

import unittest

from ops.testing import Harness

from charm import JujuDashboardKubernetesCharm


class TestCharm(unittest.TestCase):
    def setUp(self):
        self.harness = Harness(JujuDashboardKubernetesCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin_with_initial_hooks()

    def test_initial_hooks(self):
        print("test")
