#!/usr/bin/env bash

# get the absolute path of the root folder
# shellcheck disable=SC2164
ROOT=$(cd -- "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 ; pwd -P)

# emsdk_env.sh is fairly noisy, and suppress error message if the file doesn't
# exist yet (i.e. before building emsdk)
# shellcheck source=/dev/null
if [[ ! -v CI ]]; then
    # TODO: why does sourcing this in CI break?
    source "$ROOT/emsdk/emsdk/emsdk_env.sh" 2> /dev/null || true
fi
