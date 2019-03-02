Name:		signal-desktop
Version:	%{upstream_version}
Release:    0%{dot_version_suffix}%{?dist}
Summary:	Private messaging from your desktop
License:	GPLv3
URL:		https://github.com/signalapp/Signal-Desktop#readme

Source0: https://github.com/signalapp/Signal-Desktop/archive/v%{version}%{dash_version_suffix}.tar.gz

#ExclusiveArch:	x86_64
#BuildRequires: nodejs
BuildRequires: binutils
BuildRequires: yarn
BuildRequires: git
BuildRequires: python2
BuildRequires: gcc, gcc-c++
BuildRequires: node-gyp, npm
BuildRequires: desktop-file-utils
BuildRequires: make
BuildRequires: compat-openssl10-devel
# date
BuildRequires: coreutils
BuildRequires: bc

#Depends: gconf2, gconf-service, libnotify4, libappindicator1, libxtst6, libnss3, libasound2, libxss1
Requires: GConf2, libnotify, libappindicator, libXtst, nss
Requires: compat-openssl10

%description
Private messaging from your desktop

%prep
pwd
rm -rf Signal-Desktop-%{version}%{dash_version_suffix}
tar xfz %{S:0}

%build
cd Signal-Desktop-%{version}%{dash_version_suffix}
rm -vf yarn.lock

# Fix segfault (without binary openssl)
# sed -i 's|"https://github.com/scottnonnenberg-signal/node-sqlcipher.git#ed4f4d179ac010c6347b291cbd4c2ebe5c773741"|"3.2.1"|' package.json

mkdir -p $(pwd)/.mynpm

npm config set prefix $(pwd)/.mynpm 
npm install -g node@8.12.0

export PATH=$(pwd)/.mynpm/bin/:$PATH

# use a custom fork to enable fts5 but without the above madness
sed -i 's|"https://github.com/scottnonnenberg-signal/node-sqlcipher.git#36149a4b03ccf11ec18b9205e1bfd9056015cf07"|"https://github.com/drahnr/node-sqlcipher.git#79674867a7ff8beac598eabdeae275290bda481c"|' package.json

# Fix nodejs version
export LOCAL_NODE_VERSION="$(node -v | cut -b 2-)"
sed -i -- "s/    \"node\": .*/    \"node\": \"${LOCAL_NODE_VERSION}\"/g" package.json
unset LOCAL_NODE_VERSION
PATH=node_modules/.bin:$PATH yarn install

#yarn install --frozen-lockfile
#yarn generate --force
#yarn prepare-beta-build
#yarn build-release --linux dir

#yarn add --dev electron@~2.0.3  # electron-rebuild

# patch @journeyapps/sqlcipher to nuke binaries
# try and use a local copy of sqlcipher based on the original one

# yarn add --force @drahnr/sqlcipher
# d=.tmp-ja-sqlc

# rm -rf "$d"
# mkdir "$d"
# cp -pR node_modules/@drahnr/sqlcipher "$d"
# jq \
# 	'del(.bundledDependencies)|. * {"scripts":{"install":"node-pre-gyp install --build-from-source"}}' \
# 	$d/sqlcipher/package.json  >.$$ \
#     && mv .$$ $d/sqlcipher/package.json

# purge cache just in case (we didn't change version)
rm -rf $(yarn cache dir)/npm-@journeyapps/sqlcipher-*
yarn add --force "https://github.com/drahnr/node-sqlcipher.git#79674867a7ff8beac598eabdeae275290bda481c"

# overwrite some silly timestamp
# TODO shell math is not nice
echo \{time: $(echo "$(date '+%s') + 90 * 24 * 60 * 60" | bc)000\}  > ./config/local-development.json

# ... and make sure the timestamp task is not run by grunt, so we have to specify all the grund tasks manually
# since default would trigger the timestamp from commit creation again
# build
yarn generate exec:build-protobuf exec:transpile concat copy:deps sass

yarn --verbose build-release --linux dir

%install

# Electron directory of the final build depends on the arch
%ifnarch x86_64
    %global PACKDIR linux-ia32-unpacked
%else
    %global PACKDIR linux-unpacked
%endif


install -dm755 %{buildroot}%{_libdir}/%{name}
cp -r %{_builddir}/Signal-Desktop-%{version}%{dash_version_suffix}/release/%{PACKDIR}/* %{buildroot}%{_libdir}/%{name}

install -dm755 "%{buildroot}%{_datadir}/icons/hicolor"
for i in 16 24 32 48 64 128 256 512; do
    install -Dm644 %{_builddir}/Signal-Desktop-%{version}%{dash_version_suffix}/build/icons/png/${i}* %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps/%{name}.png
done

# right permissions for shared objects
install -m 755 %{_builddir}/Signal-Desktop-%{version}%{dash_version_suffix}/release/%{PACKDIR}/libffmpeg.so %{buildroot}%{_libdir}/%{name}
install -m 755 %{_builddir}/Signal-Desktop-%{version}%{dash_version_suffix}/release/%{PACKDIR}/libnode.so %{buildroot}%{_libdir}/%{name}

# create symlink
install -dm755 %{buildroot}%{_bindir}
ln -s %{_libdir}/%{name}/signal-desktop %{buildroot}%{_bindir}/signal-desktop

# create desktop entry
mkdir -p %{_builddir}%{_datadir}/applications/

cat > %{name}.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=Signal
GenericName=Messenger
Comment=Signal Private Messenger for the Desktop
Icon=signal-desktop
Exec=signal-desktop
Categories=Network;Messenger;
StartupNotify=true
EOF

install -Dm644 %{name}.desktop %{buildroot}%{_datadir}/applications/%{name}.desktop

%post
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
/usr/bin/update-desktop-database &> /dev/null || :
/sbin/ldconfig

%postun
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi
/usr/bin/update-desktop-database &> /dev/null || :
/sbin/ldconfig

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%files
%defattr(-,root,root)
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_bindir}/signal-desktop
%{_libdir}/%{name}/*

%changelog
* Fri Jan 25 2019 Bernhard Schuster <bernhard@ahoi.io> 1.20.0-1
  - bump to upstream version 1.20.0-rc3

* Wed Oct 31 2018 Bernhard Schuster <bernhard@ahoi.io> 1.17.2-1
  - bump to upstream version 1.17.2

* Sat Sep 8 2018 Bernhard Schuster <bernhard@ahoi.io> 1.16.0-1
  - bump to upstream version 1.16.0

* Thu Aug 16 2018 Bernhard Schuster <bernhard@ahoi.io> 1.15.5-1
  - bump to upstream version 1.15.5

* Sun Aug 12 2018 Bernhard Schuster <bernhard@ahoi.io> 1.15.4-1
  - bump to upstream version 1.15.4

* Tue Jul 17 2018 Bernhard Schuster <bernhard@ahoi.io> 1.14.1-1
  - bump to upstream version 1.14.1

* Mon Jun 25 2018 Bernhard Schuster <bernhard@ahoi.io> 1.13.0-1
  - bump to upstream version 1.13.0

* Mon Jun 4 2018 Bernhard Schuster <bernhard@ahoi.io> 1.12.0-1
  - bump to upstream version 1.12.0

* Tue May 15 2018 Bernhard Schuster <bernhard@ahoi.io> 1.11.0-1
  - bump to upstream version 1.11.0 and required spec file adjustments

* Sat Apr 14 2018 Bernhard Schuster <bernhard@ahoi.io> 1.7.1-1
  - bump to upstream version 1.7.1

* Wed Apr 11 2018 Bernhard Schuster <bernhard@ahoi.io> 1.7.0-1
  - bump to upstream version 1.7.0

* Sun Apr 8 2018 Bernhard Schuster <bernhard@ahoi.io> 1.6.1-1
  - bump to upstream version 1.6.1

* Sun Mar 4 2018 Bernhard Schuster <bernhard@ahoi.io> 1.5.2-3
  - update icons and desktop database

* Fri Mar 2 2018 Guilherme Cardoso <gjc@ua.pt> 1.5.2-1
  - Version bump

* Thu Mar 1 2018 Guilherme Cardoso <gjc@ua.pt> 1.5.1-1
  - Version bump

* Tue Feb 27 2018 Guilherme Cardoso <gjc@ua.pt> 1.5.0-1
  - Version bump

* Sun Feb 18 2018 Guilherme Cardoso <gjc@ua.pt> 1.3.0-2
  - Build from sources instead of unpacking .deb release

* Mon Feb 05 2018 Guilherme Cardoso <gjc@ua.pt> 1.3.0-1
  - Version bump
  - Added missing dependencies from original deb package

* Thu Nov 9 2017 Richard Monk <richardmonk@gmail.com> 1.0.37-1
  - Version bump

* Thu Nov 02 2017 Richard Monk <richardmonk@gmail.com> 1.0.35-1
  - Initial Packaging
