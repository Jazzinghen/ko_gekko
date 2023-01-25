#!/bin/bash

# Functions
function cleanup {
    echo "Removing temporary data..."
    #rm -rf "${out_dir}"
    popd >/dev/null || exit
}

# Main
runner_dir=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
pushd "${runner_dir}" >/dev/null || exit

trap cleanup EXIT

out_dir="$(mktemp -d --suffix=kogekko)"
chmod 777 "${out_dir}"

KOGEKKO_DOWNLOADS="${out_dir}" docker compose run --rm ko_gekko pipenv run python src/main.py "$@"

downloaded_files=$(find "${out_dir}" -mindepth 1 -maxdepth 1 -type f,d | wc -l)

echo "${out_dir}"
find "${out_dir}" -mindepth 1 -maxdepth 1 -type f,d

if ((downloaded_files > 0)); then
    final_download_dir="${runner_dir}/ko_gekko_downloads/"
    cp -r "${out_dir}" "${final_download_dir}" || exit
fi
