#!/usr/bin/env python3
# Copyright 2022 Penelope Valentine Gale
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Charm the service.

Refer to the following post for a quick-start guide that will help you
develop a new k8s charm using the Operator Framework:

    https://discourse.charmhub.io/t/4208
"""

import logging
import os

from jinja2 import Environment, FileSystemLoader

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus


logger = logging.getLogger(__name__)


class JujuDashboardKubernetesCharm(CharmBase):
    """Juju Dashboard Kubernetes Charm"""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)

        self.framework.observe(self.on.dashboard_pebble_ready, self._on_dashboard_pebble_ready)

    def _on_dashboard_pebble_ready(self, event):
        """Things are ready; go ahead and start up our service."""

        # Grab the config template.
        env = Environment(loader=FileSystemLoader(os.getcwd()))
        env.filters['bool'] = bool

        config_template = env.get_template("src/config.js.template")
        _ = config_template.render(
            base_app_url="/",
            controller_api_endpoint="/api",
            identity_provider_url="",
            is_juju=True
        )

        # TODO: Get from controller relation when it's fixed in juju
        controller_url = "wss://10.1.91.69:17070"
        nginx_template = env.get_template("src/nginx.conf.template")
        _ = nginx_template.render(
            # nginx proxy_pass expects the protocol to be https
            controller_ws_api=controller_url.replace("wss", "https"),
            dashboard_root="/srv"
        )
        """ TODO: integrate the following into the layer def.

                    "ports": [
                        {
                            "containerPort": 80,
                        }
                    ],
                    'volumeConfig': [{
                        'name': 'configs',
                        'mountPath': '/srv/configs',
                        'files': [
                            {
                                'path': 'config.js',
                                'content': congig_js
                            },
                            {
                                'path': 'nginx.conf',
                                'content': nginx_config
                            }
                        ]
        """

        # Get a reference the container attribute on the PebbleReadyEvent
        container = event.workload
        # Define an initial Pebble layer configuration
        pebble_layer = {
            "summary": "dashboard layer",
            "description": "pebble config layer for dashboard",
            "services": {
                "dashboard": {
                    "override": "replace",
                    "summary": "dashboard",
                    "command": "",
                    "startup": "enabled",
                    "environment": {},
                }
            },
        }
        # Add initial Pebble config layer using the Pebble API
        container.add_layer("dashboard", pebble_layer, combine=True)
        # Autostart any services that were defined with startup: enabled
        container.autostart()
        # Learn more about statuses in the SDK docs:
        # https://juju.is/docs/sdk/constructs#heading--statuses
        self.unit.status = ActiveStatus()


if __name__ == "__main__":
    main(JujuDashboardKubernetesCharm)
