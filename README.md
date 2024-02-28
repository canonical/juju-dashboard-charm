# Juju Dashboard Charm

This repository contains charms that deploy the dashboard for [Juju](https://juju.is) and [JAAS](https://jaas.ai) into Machine and Kubernetes environments.

[![Charm for Juju Dashboard
](https://charmhub.io/juju-dashboard/badge.svg)](https://charmhub.io/juju-dashboard)
[![Charm for Juju Dashboard k8s](https://charmhub.io/juju-dashboard-k8s/badge.svg)](https://charmhub.io/juju-dashboard-k8s)

# Building and Testing the Machine Charm

Building the machine charm is fairly straightforward. You need a machine with Juju 3.0+ installed. The rest of the steps, in brief, are:

```sh
# From the root directory of this repo

# Build the charm
cd ./machine-charm
charmcraft pack

# Bootstrap a test controller. Make a make a model, and deploy an application, so that the dashboard has things to show.
juju bootstrap localhost localhost-test
juju add-model test
juju switch test
juju deploy ubuntu

# Switch to the controller model and setup the dashboard
juju switch controller
# If apt fails to install packages when deploying the dashboard you may need to run the following:
# sudo iptables -P FORWARD ACCEPT
juju deploy ./juju-dashboard*.charm dashboard
juju relate controller dashboard
juju dashboard
```

Once you login following the instructions in the output of `juju dashboard` you should be able to see the controller model, as well as the test model and test application that you deployed.

## Update the dashboard to latest version

This script pulls that latest Github release of the dashboard and extracts it to the appropriate folder in `machine-charm`:

```sh
./scripts/update-machine-charm-dashboard.sh
```

# Building and Testing the k8s charm

This guide covers every step necessary to build and test a k8s charm, from updating the facades in js-libjuju, to rebuilding the dashboard source, to building the charm. You can skip some steps if you don't need to update every part of the toolchain.

## Install Juju 3.0

Bulid from [source](https://github.com/juju/juju), or `snap install --channel=3.0/beta juju`

## Install Docker Engine

Follow the [guide on the docker website](https://docs.docker.com/desktop/install/linux-install/) to install the latest version of the Docker engine.

## Bootstrap microk8s

[Follow the guide here](https://juju.is/docs/olm/microk8s)

In brief:

```
snap install microk8s --classic

sudo usermod -a -G microk8s $USER
sudo chown -f -R $USER ~/.kube
su - $USER

microk8s status --wait-ready
microk8s.enable hostpath-storage dns

microk8s config | juju add-k8s --client micro
juju bootstrap micro
```

## juju-dashboard

### Using the latest release

There is no need to `git clone` the repository, in the section "[Building the Kubernetes Charm](#building-the-kubernetes-charm)" we will set the `<image-id>` to `canonicalwebteam/juju-dashboard:latest`

### Building from source

[Source](https://github.com/canonical/juju-dashboard#readme)

1. Checkout `git@github.com:canonical/juju-dashboard.git`
2. Build the container with `DOCKER_BUILDKIT=1 docker build -t juju-dashboard .`
3. Take note of the image id. You can get it with `docker image inspect juju-dashboard | grep "Id"`
4. Add the docker image that you just build to microk8s' build in docker repo, as it cannot talk to the docker registry on the host machine: `docker image save juju-dashboard | microk8s ctr image import -`

## Building the Kubernetes Charm

You're finally ready to build the charm! Change to the root directory of this repo, and run:

```sh
# Build the charm
cd ./k8s-charm
charmcraft pack

# Switch to the controller model and deploy the dashboard
juju switch controller
# image id must include: "sha256:..."
# using latest OCI release
juju deploy --resource dashboard-image=canonicalwebteam/juju-dashboard:latest ./juju-dashboard*.charm dashboard
# alternatively, using a custom OCI image
# juju deploy --resource dashboard-image=<image id> ./juju-dashboard*.charm dashboard
juju relate controller dashboard
juju dashboard
```

Login to the dashboard, per the instructions from the `juju dashboard` command.

# Tips and Tricks for Testing

## Acccess the Dashboard Without a Proxy

Sometimes, it may be useful to access the dashboard directly, rather than through the ssh tunnel. (E.g., you are trying to determine which part of the pipeline has broken, or access a test server remotely.)

This is made difficult in development environments, where the controller will typically be using self signed certs. Modern browsers will simply refuse to connect to the controller API. Here's a workaround:

### In Firefox, Accept the Controller's Self Signed Cert

You must tell your browser to trust the controller's cert in order to get a working dashboard. This requires Firefox, or another browser that allows you to override the security warning. Here's how to do so:

1. From the CLI, execute `juju switch controller && juju status`
2. Note the ip address for the controller, and for the dashboard.
3. Open Firefox, and visit https://<controller ip>:17070
4. Click to the advanced part of the security prompt, and accept the risk.
5. Firefox will display a "bad request" page. This is okay. You have successfully accepted the ssl cert!

### Visit the dashboard

1. From the CLI, execute `juju dashboard`, and make note of the username and password. You don't need to leave the command running, as you are accessing the dashboard directly, rather than using the proxy server.
2. In Firefox, visit https://<dashboard ip>.
3. Login with username and password you obtained in step 1.

# Releasing

## Machine charm

```sh
charmcraft login
cd ./machine-charm
charmcraft pack
charmcraft upload juju-dashboard*.charm
charmcraft release juju-dashboard --channel=... --revision=...
```

## K8s charm

### Update the Docker image

```sh
git clone git@github.com:canonical/juju-dashboard.git
cd juju-dashboard
DOCKER_BUILDKIT=1 docker build -t juju-dashboard .
```

Get the the docker image ID with `docker image inspect juju-dashboard | grep "Id"`

```sh
charmcraft login
charmcraft upload-resource juju-dashboard-k8s dashboard-image --image=[image-id]
```

### Update the charm

```sh
charmcraft login
cd ./k8s-charm
charmcraft pack
charmcraft upload juju-dashboard-k8s*.charm
charmcraft release juju-dashboard-k8s --channel=... --revision=[output-from-upload] --resource=dashboard-image:[resource-revision-number]
```
