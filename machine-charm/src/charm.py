#!/usr/bin/env python3
# Copyright 2021 Canonical
# See LICENSE file for licensing details.

import logging
import os

from charmhelpers.core import hookenv  # FIXME: This needs to be ported to ops.
from charms.juju_dashboard.v0.juju_dashboard import JujuDashData, JujuDashReq
from jinja2 import Environment, FileSystemLoader
from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus

logger = logging.getLogger(__name__)


class JujuDashboardCharm(CharmBase):
    """Juju Dashboard Charm"""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.install, self._on_install)
        # self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
        # self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on["controller"].relation_changed,
                               self._on_controller_relation_changed)
        self.framework.observe(self.on["dashboard"].relation_changed,
                               self._on_dashboard_relation_changed)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self._stored.set_default(controllerData={})

    def _on_install(self, _):
        os.system("apt install -y nginx")  # TODO: use linux system tools
        hookenv.open_port(8080)

    def _on_dashboard_relation_changed(self, event):
        event.relation.data[self.app]["port"] = "8080"

    def _on_controller_relation_changed(self, event):
        """ """
        requires = JujuDashReq(self, event.relation, event.app)
        if not requires.data["controller_url"]:
            self.unit.status = BlockedStatus("Missing controller URL")
            return

        self._configure(**requires.data)

    def _on_config_changed(self, _):
        relation = self.model.get_relation("controller")
        if relation:
            data = JujuDashData(relation.data[relation.app])
            self._configure(data['controller_url'], data['identity_provider_url'], data['is_juju'])

    def _configure(self, controller_url, identity_provider_url, is_juju):
        """ """

        # Load up nginx templates and poke at system.
        env = Environment(loader=FileSystemLoader(os.getcwd()))
        env.filters['bool'] = bool

        config_template = env.get_template("src/config.js.template")
        config_template.stream(
            base_app_url="/",
            controller_api_endpoint="/api",
            identity_provider_url=identity_provider_url,
            is_juju=is_juju
        ).dump("src/dist/config.js")

        controller_url.replace("wss", "https")
        if not controller_url.startswith('https://'):
            controller_url = 'https://{}'.format(controller_url)

        if self.config.get('dns-name'):
            hookenv.open_port(443)
            hookenv.close_port(8080)

        nginx_template = env.get_template("src/nginx.conf.template")
        nginx_template = nginx_template.stream(
            # nginx proxy_pass expects the protocol to be https
            controller_ws_api=controller_url.replace("wss", "https"),
            dashboard_root=os.getcwd(),
            dns_name=self.config.get('dns-name')
        ).dump("/etc/nginx/sites-available/default")

        nginx_status = os.system("sudo systemctl restart nginx")
        # If restarting nginx returns a 0 status it should have been succesfull
        if nginx_status == 0:
            self.unit.status = ActiveStatus()
        else:
            self.unit.status = BlockedStatus("Could not start nginx")


if __name__ == "__main__":
    main(JujuDashboardCharm)
