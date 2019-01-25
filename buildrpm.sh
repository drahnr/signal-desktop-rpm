#!/usr/bin/env bash

set -x
set -e

NAME=${2}
DEST=${1}

pwd 2>&1
RPMBUILD_DIR="$(pwd)/rpmbuild"

mkdir -p "${RPMBUILD_DIR}/${DEST}/"{SOURCES,BUILD,RPMS,SRPMS,SPECS}

cd ${RPMBUILD_DIR}
rpmbuild \
--define "_topdir %(pwd)" \
--define "_builddir %{_topdir}/BUILD" \
--define "_rpmdir %{_topdir}/RPMS" \
--define "_srcrpmdir %{_topdir}/SRPMS" \
--define "_specdir %{_topdir}/SPECS" \
--define "_sourcedir  %{_topdir}/SOURCES" \
-ba SPECS/${NAME}.spec || exit 1

mkdir -p $(pwd)/${DEST}/{,s}rpm/
rm -vf $(fd '^'"${NAME}"'-.*debug.*\.rpm$' "${RPMBUILD_DIR}")
mv -vf $(fd '^'"${NAME}"'-.*\.rpm$' "${RPMBUILD_DIR}") "$(pwd)/${DEST}/rpm/"
mv -vf $(fd '^'"${NAME}"'-.*\.src\.rpm$' "${RPMBUILD_DIR}") "$(pwd)/${DEST}/srpm/"
