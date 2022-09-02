# juju-dashboard

## Description

This is a charm built to deploy the Juju dashboard.

It replaces previous methods of delivering the dashboard with a Juju
native one.

## Usage

TODO

## Relations

This charm provides an http interface called "dashboard."

It requires the "juju-dashboard" interface on the Juju controller charm.

## OCI Images

This charm uses the JAAS team's build of the dashboard: canonicalwebteam/jaas-dashboard:latest

## Contributing

Please see the [Juju SDK docs](https://juju.is/docs/sdk) for guidelines
on enhancements to this charm following best practice guidelines, and
`CONTRIBUTING.md` for developer guidance.
