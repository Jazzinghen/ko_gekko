#!/bin/bash

# Functions
function cleanup {
    echo "Removing temporary data..."
    # This command might fail in case of user namespace redirection.
    rm -rf "${out_dir}" 2>/dev/null
    popd >/dev/null || exit
}

# Main
# Find the actual location of the script and go there
runner_dir=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
pushd "${runner_dir}" >/dev/null || exit

trap cleanup EXIT

# Create a temporary directory to store all the output from the container and
# set the permissions to read/write for everyone in case of user namespace
# redirection
out_dir="$(mktemp -d --suffix=kogekko)"
chmod 777 "${out_dir}"

# Actually call the application in docker passing all the remaining arguments
KOGEKKO_DOWNLOADS="${out_dir}" docker compose run --rm ko_gekko \
    pipenv run python src/main.py "$@"

# Check if we downloaded something
downloaded_files=$(find "${out_dir}" -mindepth 1 -maxdepth 1 -type f,d | wc -l)

# In case we downloaded things let's copy them to the local download folder,
# fixing permissions as well
if ((downloaded_files > 0)); then
    final_download_dir="${runner_dir}/ko_gekko_downloads"
    cp -rfT "${out_dir}" "${final_download_dir}" || exit
fi
