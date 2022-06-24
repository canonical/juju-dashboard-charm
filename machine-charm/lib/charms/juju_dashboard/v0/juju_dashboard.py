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

# The unique Charmhub library identifier, never change it
LIBID = "2d0d08ebc336404ba91a9a4daf5c40ee"

# Increment this major API version when introducing breaking changes
LIBAPI = 0

# Increment this PATCH version before using `charmcraft publish-lib` or reset
# to 0 if you are raising the major API version
LIBPATCH = 1


class JujuDashboardProvider:
    """
    Usage:

    class YourCharm(...):
        ...
        def on_juju_dashboard_relation_event(self, event):
            data = JujuDashboardProvider(self, event).data
            ctrl_url = data['controller-url']
            id_url data['identity-provider-url']
            is_juju = data['is-juju']
            
    """
    def __init__(self, charm, event):
        self.charm = charm
        self.event = event

    @property
    def data(self):
        return self.event.relation.data[event.app]
    

class JujuDashboardRequirer:
    """
    Usage:

    class YourCharm(...):
        ...
        def on_juju_dashboard_relation_event(self, event):
            JujuDashboardProvider(self, event).data.update(event, data={
                ...
            })
    """
    def __init__(self, charm, event):
        self.charm = charm
        self.event = event

    
