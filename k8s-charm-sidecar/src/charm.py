#!/usr/bin/env python3
# Copyright 2021 Ubuntu
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Charm the service.

Refer to the following post for a quick-start guide that will help you
develop a new k8s charm using the Operator Framework:

    https://discourse.charmhub.io/t/4208
"""

import os
import logging

from jinja2 import Environment, FileSystemLoader

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus


logger = logging.getLogger(__name__)


 class JujuDashboardKubernetesCharm(CharmBase):
    """Juju Dashboard Kubernetes Charm"""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.start, self.configure_pod)
        self.framework.observe(self.on.config_changed, self.configure_pod)
        self._stored.set_default(spec=None)

    def configure_pod(self, event):
        """Assemble the pod spec and apply it, if possible."""
        if "image" not in self.model.config:
            message = "Missing required config: image"
            logger.info(message)
            self.model.unit.status = BlockedStatus(message)
            return

        env = Environment(loader=FileSystemLoader(os.getcwd()))
        env.filters['bool'] = bool

        config_template = env.get_template("src/config.js.template")
        congig_js = config_template.render(
            base_app_url="/",
            controller_api_endpoint="/api",
            identity_provider_url="",
            is_juju=True
        )

        # TODO: Get from controller relation when it's fixed in juju
        controller_url = "wss://10.1.91.69:17070"
        nginx_template = env.get_template("src/nginx.conf.template")
        nginx_config = nginx_template.render(
            # nginx proxy_pass expects the protocol to be https
            controller_ws_api=controller_url.replace("wss", "https"),
            dashboard_root="/srv"
        )

        self.model.unit.status = MaintenanceStatus("Setting pod spec")
        self.model.pod.set_spec({
            "version": 3,
            "containers": [
                {
                    "name": self.app.name,
                    "image": self.model.config["image"],
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
                    }],
                }
            ],
        })

        self.model.unit.status = ActiveStatus()


if __name__ == "__main__":
    main(JujuDashboardKubernetesCharm)
