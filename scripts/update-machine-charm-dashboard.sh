#! /bin/bash

dist_path=./machine-charm/src/dist

# delete existing version
rm -rf $dist_path/*

echo "Downloading the latest release..."
rm -f *.tar.bz2

wget -qO- https://api.github.com/repos/canonical/juju-dashboard/releases/latest \
| grep tar.bz2 \
| cut -d : -f 2,3 \
| tr -d \" \
| wget -qi -

echo "Extracting the dashboard..."
tar -xf *.tar.bz2 -C $dist_path

# clean up
rm -f *.tar.bz2
rm -f $dist_path/config.js.go $dist_path/config.local.js

echo "Done!"
