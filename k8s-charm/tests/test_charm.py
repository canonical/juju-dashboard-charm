# Copyright 2021 Ubuntu
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

import unittest

from ops.model import ActiveStatus, MaintenanceStatus
from ops.testing import Harness

from charm import JujuDashboardKubernetesCharm


FAKE_ENDPOINT = {
    "bind-addresses": [{
        "macaddress": "",
        "interface-name": "foo",
        "addresses": [{"address": "10.10.10.10", "cidr": "10.10.10.0/24"}],
    }],
    "ingress-addresses": ["10.10.10.11"],
}


class TestCharm(unittest.TestCase):

    def setUp(self):
        self.harness = Harness(JujuDashboardKubernetesCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.set_leader(True)
        self.harness.begin_with_initial_hooks()

        self.rel_id = self.harness.add_relation('controller', 'juju-controller')
        self.harness.add_relation_unit(self.rel_id, "juju-controller/0")

        self.harness.framework.model._backend.network_get = \
            lambda endpoint_name, relation_id: FAKE_ENDPOINT

    def test_startup(self):
        # We should flip into Maintenance status after initial hooks.
        self.assertEqual(
            self.harness.model.unit.status,
            MaintenanceStatus("Waiting for controller relation.")
        )

    def test_relation(self):
        # We should properly setup the relation.
        self.harness.update_relation_data(self.rel_id, "juju-controller", {
            "controller-url": "api/some/controller/url",  # TODO: get real data
            "identity-provider-url": "api/some/provider/url",
            "is-juju": True
        })

        self.assertEqual(self.harness.model.unit.status, ActiveStatus())
