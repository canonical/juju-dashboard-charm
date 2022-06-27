"""TODO: Add a proper docstring here.

This is a placeholder docstring for this charm library. Docstrings are
presented on Charmhub and updated whenever you push a new version of the
library.

Complete documentation about creating and documenting libraries can be found
in the SDK docs at https://juju.is/docs/sdk/libraries.

See `charmcraft publish-lib` and `charmcraft fetch-lib` for details of how to
share and consume charm libraries. They serve to enhance collaboration
between charmers. Use a charmer's libraries for classes that handle
integration with their charm.

Bear in mind that new revisions of the different major API versions (v0, v1,
v2 etc) are maintained independently.  You can continue to update v0 and v1
after you have pushed v3.

Markdown is supported, following the CommonMark specification.
"""

import re

from ops.charm import CharmBase
from ops.model import Application, Relation

from typing import Mapping


# The unique Charmhub library identifier, never change it
LIBID = "2d0d08ebc336404ba91a9a4daf5c40ee"

# Increment this major API version when introducing breaking changes
LIBAPI = 0

# Increment this PATCH version before using `charmcraft publish-lib` or reset
# to 0 if you are raising the major API version
LIBPATCH = 1


class JujuDashReq:
    """Implementation of the "requires" (client) side of the relation.

    Counterintuitively, this is the Dashboard. The Juju Controller is "providing" us with
    the information the Dashboard needs to connect.
    """
    def __init__(self, charm: CharmBase, relation: Relation, provider: Application):
        """Populate our relation data.

        Also tries to send the endpoint data that the dashboard is being hosted at. This
        information can be relayed to the user via the controller when the user runs the
        `juju dashboard` command.

        Args:
            charm: the charm that is using this library.

            relation: the relation with the Juju controller. Usually even.relation in a
                relation handler.

            provider: The Application providing the controller data. Usually a
                juju-controller application.
        """
        self.data = JujuDashData(relation.data[provider])

        # Update the relation with our own ingress ip
        if charm.unit.is_leader():
            # TODO: handle the situation where there are multiple dashes, and the endpoint
            # is the haproxy address.
            ip = str(charm.model.get_binding(relation).network.ingress_address)
            relation.data[charm.model.app]['dashboard-ingress'] = ip


class JujuDashData(Mapping):

    def __init__(self, data):
        """Parse the config data from the controller into a Mapping.

        Note: The controller charm provides the full controller path but we use this path
        to generate the controller and model paths so we need to remove the supplied
        "/api" suffix.

        Args:
            relation: the relation with the Juju controller. Usually even.relation in a
                relation handler.

            provider: The Application providing the controller data. Usually a
                juju-controller application.

        """
        self._data = {
            "controller_url": re.sub(r'\/api$', '', data.get("controller-url", "")),
            "identity_provider_url": data.get("identity-provider-url", ""),
            "is_juju": data.get("is-juju", True),
        }

    def __contains__(self, key):
        return key in self._data

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, key):
        return self._data[key]

    def __repr__(self):
        return repr(self._data)
