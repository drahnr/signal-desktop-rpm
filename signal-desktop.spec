Name:		signal-desktop
Version:	1.5.2
Release:	2%{?dist}
Summary:	Private messaging from your desktop
License:	GPLv3
URL:		https://github.com/signalapp/Signal-Desktop#readme

Source0:	https://github.com/signalapp/Signal-Desktop/archive/v%{version}.tar.gz

#ExclusiveArch:	x86_64
BuildRequires:binutils
BuildRequires: yarn
BuildRequires: git
BuildRequires: python2
BuildRequires: gcc, gcc-c++
BuildRequires: node-gyp, npm
BuildRequires: desktop-file-utils

#Depends: gconf2, gconf-service, libnotify4, libappindicator1, libxtst6, libnss3, libasound2, libxss1
Requires:   GConf2, libnotify, libappindicator, libXtst, nss

%description
Private messaging from your desktop

%prep
pwd
rm -rf Signal-Desktop-%{version}
tar xfz %{S:0}

%build
cd Signal-Desktop-%{version}
yarn install
yarn pack-prod --force

%install

# Electron directory of the final build depends on the arch
%ifnarch x86_64
    %global PACKDIR linux-ia32-unpacked
%else
    %global PACKDIR linux-unpacked
%endif


install -dm755 %{buildroot}%{_libdir}/%{name}
cp -r %{_builddir}/Signal-Desktop-%{version}/dist/%{PACKDIR}/* %{buildroot}%{_libdir}/%{name}

install -dm755 "%{buildroot}%{_datadir}/icons/hicolor"
for i in 16 24 32 48 64 128 256 512; do
    install -Dm644 %{_builddir}/Signal-Desktop-%{version}/build/icons/png/${i}* %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps/%{name}.png
done

# right permissions for shared objects
install -m 755 %{_builddir}/Signal-Desktop-%{version}/dist/%{PACKDIR}/libffmpeg.so %{buildroot}%{_libdir}/%{name}
install -m 755 %{_builddir}/Signal-Desktop-%{version}/dist/%{PACKDIR}/libnode.so %{buildroot}%{_libdir}/%{name}

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
%{_datadir}/applications/signal-desktop.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_bindir}/signal-desktop
%{_libdir}/%{name}/*

%changelog
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