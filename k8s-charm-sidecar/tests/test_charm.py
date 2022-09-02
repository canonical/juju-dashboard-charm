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
        self.harness.set_can_connect('dashboard', True)
        self.container = self.harness.model.unit.get_container('dashboard')
        self.container.make_dir('/srv')

    def test_initial_hooks(self):
        print("test")

    def test_on_controller_relation_changed(self):
        rel_id = self.harness.add_relation("controller", "controller")
        self.harness.add_relation_unit(rel_id, "controller/0")
        self.harness.update_relation_data(rel_id, "controller", {
            "controller-url": "wss://10.10.10.1:107070",
            "is-juju": True,
            "identity-provider-url": ""
        })

        nginx_config = self.container.pull('/srv/nginx.config').read()
        self.assertTrue("https://10.10.10.1:107070" in nginx_config)

        config = self.container.pull('/srv/config.js').read()
        self.assertTrue("isJuju: true" in config)
