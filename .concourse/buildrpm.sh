#!/usr/bin/env bash

set -x
set -e

REFERENCE_DIR="$(pwd)"

NAME="${1}"
SPEC_SOURCE_DIR="${REFERENCE_DIR}/${2}"
GIT_REPO_DIR="${REFERENCE_DIR}/${3}"
OUTPUT_RPM_DIR="${REFERENCE_DIR}/${4}"
OUTPUT_SRPM_DIR="${REFERENCE_DIR}/${5}"

pwd 2>&1
RPMBUILD_DIR="${REFERENCE_DIR}/rpmbuild"

mkdir -p "${RPMBUILD_DIR}/{SOURCES,BUILD,RPMS,SRPMS,SPECS}"

cp -v "${SPEC_SOURCE_DIR}/${NAME}.spec" "${RPMBUILD_DIR}/SPECS"

cd "${GIT_REPO_DIR}"
git archive --format=tar --prefix="${NAME}" HEAD | xz > "${NAME}.tar.xz"
cd -

cp -v "${GIT_REPO_DIR}/${NAME}*.tar.xz" "${RPMBUILD_DIR}/SOURCES"

cd "${RPMBUILD_DIR}"

dnf install -y 'dnf-command(builddep)'
dnf builddep -y "SPECS/${NAME}.spec"

rpmbuild \
--define "_topdir ${REFERENCE_DIR}" \
--define "_builddir %{_topdir}/BUILD" \
--define "_rpmdir %{_topdir}/RPMS" \
--define "_srcrpmdir %{_topdir}/SRPMS" \
--define "_specdir %{_topdir}/SPECS" \
--define "_sourcedir  %{_topdir}/SOURCES" \
-ba "SPECS/${name}.spec" || exit 1

mkdir -p "${RPMBUILD_DIR}/{,s}rpm"
rm -vf "${RPMBUILD_DIR}/RPMS/x86_64/${name}-*debug*.rpm"
cp -vf "${RPMBUILD_DIR}/RPMS/x86_64/${name}-*.rpm" "${OUTPUT_RPM_DIR}"
cp -vf "${RPMBUILD_DIR}/SRPMS/${name}-*.src.rpm" "${OUTPUT_SRPM_DIR}"
