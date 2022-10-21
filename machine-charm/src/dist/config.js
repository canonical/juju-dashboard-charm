var jujuDashboardConfig = {
  // API host to allow app to connect and retrieve models
  controllerAPIEndpoint: "/api",
  // Configurable base url to allow deploying to different paths.
  baseAppURL: "/",
  // If true then identity will be provided by a third party provider.
  identityProviderAvailable: true,
  // The URL of the third party identity provider.
  identityProviderURL: "api/some/provider/url",
  // Is this application being rendered in Juju and not JAAS. This flag should
  // only be used for superficial updates like logos. Use feature detection
  // for other environment features.
  isJuju: true,
};