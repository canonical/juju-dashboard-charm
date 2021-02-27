#!/usr/bin/env python3
# Copyright 2021 Canonical
# See LICENSE file for licensing details.

"""Charm the service."""

import logging
import subprocess

from ops.charm import CharmBase
from ops.main import main
from ops.framework import StoredState

from charmhelpers.core import hookenv;

logger = logging.getLogger(__name__)


class JujuDashboardCharm(CharmBase):
    """Juju Dashboard Charm"""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on['dashboard'].relation_changed, self._on_dashboard_relation_changed)
        self.framework.observe(self.on['controller'].relation_changed, self._on_controller_relation_changed)
        # self._stored.set_default(things=[])33

    def _on_start(self, _):
        """
        Start the webserver to host the dashboard.
        """
        # XXX Is there a better way to do this?
        subprocess.run(
            "nohup python3 -m http.server 8080 --directory src/ > /dev/null 2>&1 & echo $! > run.pid",
            shell=True)
        hookenv.open_port(8080)

    def _on_config_changed(self, _):
        """
        XXX Not implemented
        Any values defined in the configuration will override the values
        provided by the controller relation.
        """
        logger.debug("Config changed")
        logger.debug(self.config["model-url-template"])
        # current = self.config["thing"]
        # if current not in self._stored.things:
        #     logger.debug("found a new thing: %r", current)
        #     self._stored.things.append(current)

    def _on_dashboard_relation_changed(self, event):
        """
        XXX Not implemented
        If the user wants to front the dashboard with a proxy return the
        information about where the dashboard is being hosted so that it can
        connect to the correct endpoint.
        """
        pass

    def _on_controller_relation_changed(self, event):
        """
        Receive the configuration data for the controller so that we can
        generate the config file for the dashboard. We also send the endpoint
        data that the dashboard is being hosted at so that this information can
        be relayed to the user via the controller when the user runs the
        `juju dashboard` command.
        """
        if not isInstance(self._stored.controllerData, dict):
            self._stored.controllerData = {}

        self._stored.controllerData['controllerURL'] = event.relation.data[event.app]['controller-url']
        self._stored.controllerData['modelURLTemplate'] = event.relation.data[event.app]['model-url-template']
        self._stored.controllerData['identityProviderURL'] = event.relation.data[event.app]['identity-provider-url']
        self._stored.controllerData['isJuju'] = event.relation.data[event.app]['is-juju']
        # Send the data to the controller for our endpoint
        # XXX get the machines IP address using:
        #   https://ops.readthedocs.io/en/latest/#ops.model.Network
        event.relation.data[event.app]['hostname'] = "0.0.0.0:8080"
        # XXX render data into the html page
        pass

if __name__ == "__main__":
    main(JujuDashboardCharm)
