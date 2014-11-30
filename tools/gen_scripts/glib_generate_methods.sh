#!/bin/bash

# Note that JHBUILD_SOURCES should be defined to contain the path to the root
# of the jhbuild sources. The script assumes it resides in the
# tools/gen_scripts directory and the defs files will be placed in glib/src.

if [ -z "$JHBUILD_SOURCES" ]; then
  echo -e "JHBUILD_SOURCES must contain the path to the jhbuild sources."
  exit 1;
fi

PREFIX="$JHBUILD_SOURCES/glib"
ROOT_DIR="$(dirname "$0")/../.."
OUT_DIR="$ROOT_DIR/glib/src"
GIR_DIR="$ROOT_DIR/gir"

GENERATOR_PY="$JHBUILD_SOURCES/glibmm/tools/defs_gen/gir-defs-generator.py"
$GENERATOR_PY "$GIR_DIR"/GLib-2.0.gir > "$OUT_DIR"/glib_functions.defs
$GENERATOR_PY "$GIR_DIR"/GModule-2.0.gir > "$OUT_DIR"/gmodule_functions.defs
$GENERATOR_PY "$GIR_DIR"/GObject-2.0.gir > "$OUT_DIR"/gobject_functions.defs
