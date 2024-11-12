// eslint-disable-next-line no-unused-vars
var jujuDashboardConfig = {
  // API host to allow app to connect and retrieve models. This address should
  // begin with `ws://` or `wss://` and end with `/api`.
  controllerAPIEndpoint: "wss://jimm.comsys-internal.v2.demo.canonical.com/api",
  // Configurable base url to allow hosting the dashboard at different paths.
  baseAppURL: "/",
  // The URL of the third party identity provider. This is typically provided
  // by the controller when logging in so it's not currently used directly.
  // But it is available in the charm so putting it here in the event that we
  // would like to use it in the future.
  identityProviderURL: "/",
  // Is this application being rendered in Juju and not JAAS. This flag should
  // only be used for superficial updates like logos. Use feature detection
  // for other environment features.
  isJuju: false,
  // If true, then Google Analytics and Sentry data will be sent.
  analyticsEnabled: false,
};
