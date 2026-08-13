#!/usr/bin/env bash
# Build Biomni Singularity images.
#
# Usage:
#   bash build.sh light             # build light image only
#   bash build.sh full              # build full image only
#   bash build.sh rapids_celltypist # build RAPIDS + CellTypist GPU image
#   bash build.sh all               # build all images
#
# Default (no args): builds light image.
#
# Prerequisites:
#   - singularity installed

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# .def recipes live here (singularity_docs/, git-tracked); built .sif images
# go to ../singularity/, which is a symlink to /vol/projects/CIIM/singularity.
OUT_DIR="${SCRIPT_DIR}/../singularity"

build_image() {
    local name="$1"
    local def="${SCRIPT_DIR}/${name}.def"
    local out="${OUT_DIR}/${name}.sif"

    echo "Building ${name}.sif from ${def} ..."
    singularity build --fakeroot --force "${out}" "${def}"
    echo "Build complete: ${out}"
}

TARGET="${1:-light}"

case "${TARGET}" in
    light)
        build_image "biomni_light"
        ;;
    full)
        build_image "biomni_full"
        ;;
    rapids_celltypist)
        build_image "rapids_celltypist"
        ;;
    ciim)
        build_image "ciim"
        ;;
    gemma4)
        build_image "gemma4"
        ;;
    genotype)
        build_image "genotype"
        ;;
    agent)
        build_image "agent"
        ;;
    ldsc)
        build_image "ldsc"
        ;;
    ciim_R_base)
        build_image "ciim_R_base"
        ;;
    aging_clocks_py)
        build_image "aging_clocks_py"
        ;;
    aging_clocks_R)
        build_image "aging_clocks_R"
        ;;
    all)
        build_image "biomni_light"
        build_image "biomni_full"
        build_image "rapids_celltypist"
        build_image "ciim"
        build_image "gemma4"
        build_image "genotype"
        build_image "agent"
        build_image "ldsc"
        build_image "ciim_R_base"
        build_image "aging_clocks_py"
        build_image "aging_clocks_R"
        ;;
    *)
        echo "Usage: $0 [light|full|rapids_celltypist|ciim|gemma4|ldsc|ciim_R_base|aging_clocks_py|aging_clocks_R|all]"
        exit 1
        ;;
esac
