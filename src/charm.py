#!/usr/bin/env python3
# Copyright 2021 Canonical
# See LICENSE file for licensing details.

"""Charm the service."""

import os
import signal
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
        self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on["dashboard"].relation_changed, self._on_dashboard_relation_changed)
        self.framework.observe(self.on["controller"].relation_changed, self._on_controller_relation_changed)
        self._stored.set_default(controllerData={})
        hookenv.open_port(8080)

    def _on_start(self, _):
        """
        Start the webserver to host the dashboard.
        """
        self.start_server()

    def _on_upgrade_charm(self, _):
        """
        Restart the webserver to host the dashboard.
        """
        self.restart_server()

    def _on_config_changed(self, _):
        """
        XXX Not implemented
        Any values defined in the configuration will override the values
        provided by the controller relation.
        """
        # logger.info(self.config["model-url-template"])
        self.generate_and_save_index()
        self.restart_server()

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
        self._stored.controllerData["controller-url"] = event.relation.data[event.app]["controller-url"]
        self._stored.controllerData["model-url-template"] = event.relation.data[event.app]["model-url-template"]
        self._stored.controllerData["identity-provider-url"] = event.relation.data[event.app].get("identity-provider-url", "Fail")
        self._stored.controllerData["is-juju"] = event.relation.data[event.app]["is-juju"]
        # Send the data to the controller for our endpoint
        # XXX get the machines IP address using:
        #   https://ops.readthedocs.io/en/latest/#ops.model.Network
        #event.relation.data[event.app]["hostname"] = "0.0.0.0:8080"
        # XXX render data into the html page
        self.generate_and_save_index()
        self.restart_server()

    def generate_and_save_index(self):
        """
        Take the configuration values and render them to the index.html file
        for display on the static page.
        """
        index_template = open("src/index.html.template", "r")
        index_data = index_template.read()
        index_template.close()

        index_data = index_data.replace("{controller-url}", self._stored.controllerData.get("controller-url", ""))
        index_data = index_data.replace("{model-url-template}", self._stored.controllerData.get("model-url-template", ""))
        index_data = index_data.replace("{identity-provider-url}", self._stored.controllerData.get("identity-provider-url", ""))
        index_data = index_data.replace("{is-juju}", self._stored.controllerData.get("is-juju", ""))
        index_data = index_data.replace("{port}", "")

        index = open("src/index.html", "w")
        index.write(index_data)
        index.close()

    def start_server(self):
        subprocess.run(
            "nohup python3 -m http.server 8080 --directory src/dist/ > /dev/null 2>&1 & echo $! > run.pid",
            shell=True
        )

    def restart_server(self):
        with open("run.pid", 'r') as pid_file:
            os.kill(int(pid_file.readline()), signal.SIGTERM)
        self.start_server()

if __name__ == "__main__":
    main(JujuDashboardCharm)
