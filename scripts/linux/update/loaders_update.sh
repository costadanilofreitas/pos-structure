#!/bin/bash
bash update_repos.sh &&
bash genesis_update.sh &&
bash install_lib.sh &&
hv -w