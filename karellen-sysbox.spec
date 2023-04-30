%global debug_package %{nil}
%global _missing_build_ids_terminate_build 0

Name: karellen-sysbox
Version: 0.6.1.17
Release: 2
License: ASL 2.0
Summary: Sysbox
Url: https://github.com/karellen/%{name}

BuildRequires: git
BuildRequires: make
BuildRequires: iproute
BuildRequires: automake
BuildRequires: autoconf
BuildRequires: libtool
BuildRequires: pkg-config
BuildRequires: wget
BuildRequires: tar
BuildRequires: gzip
BuildRequires: unzip
BuildRequires: glibc-static
BuildRequires: systemd-rpm-macros

Requires: docker
Requires: systemd

Provides: sysbox

Source0: %{name}-%{version}.tar.gz

%description
Karellen-sysbox is an UNOFFICIAL Fedora/RHEL/CentOS spin of the Nestybox Sysbox.
Depending on whether you're using it with moby-engine or docker-ce either
/etc/sysconfig/docker or /etc/docker/daemon.json have to be modified respectively,
using configuration available in /etc/sysconfig/docker-karellen-sysbox or
/etc/docker/daemon-karellen-sysbox.json respectively.
Restart docker daemon (systemctl restart docker) after configuration changes.

%ifarch x86_64
  %global sys_arch amd64
  %global protoc_arch x86_64
%endif
%ifarch aarch64
  %global sys_arch arm64
  %global protoc_arch aarch_64
%endif
%ifarch arm
  %global sys_arch armf
%endif
%ifarch armel
  %global sys_arch armel
%endif

%prep
%autosetup
cd /tmp
mkdir -p $HOME/.local
export PATH="$PATH:$HOME/.local/bin:$HOME/.local/go/bin"
wget https://go.dev/dl/go1.19.8.linux-%{sys_arch}.tar.gz
tar -C $HOME/.local -xzf go1.19.8.linux-%{sys_arch}.tar.gz
curl -LO https://github.com/protocolbuffers/protobuf/releases/download/v3.15.8/protoc-3.15.8-linux-%{protoc_arch}.zip
unzip protoc-3.15.8-linux-%{protoc_arch}.zip -d $HOME/.local
go install github.com/golang/protobuf/protoc-gen-go@latest
export PATH="$PATH:$(go env GOPATH)/bin"

%build
export PATH="$PATH:$HOME/.local/bin:$HOME/.local/go/bin"
export PATH="$PATH:$(go env GOPATH)/bin"

cd sysbox
make sysbox-static-local

%install
export PATH="$PATH:$HOME/.local/bin:$HOME/.local/go/bin"
export PATH="$PATH:$(go env GOPATH)/bin"

cp sysbox/OSS_DISCLOSURES.md .
cp sysbox/LICENSE LICENSE-nestybox
cp LICENSE LICENSE-karellen

install -Dpm 644 packaging/docker-karellen-sysbox \
                 %{buildroot}%{_sysconfdir}/sysconfig/docker-karellen-sysbox
install -Dpm 644 packaging/daemon-karellen-sysbox.json \
                 %{buildroot}%{_sysconfdir}/docker/daemon-karellen-sysbox.json

install -Dpm 644 packaging/sysctl.d/99-sysbox-sysctl.conf -t %{buildroot}%{_sysctldir}/
install -Dpm 644 packaging/systemd/sysbox-fs.service \
                 packaging/systemd/sysbox-mgr.service \
                 packaging/systemd/sysbox.service -t %{buildroot}%{_unitdir}/

cd sysbox
make DESTDIR=%{buildroot}%{_bindir} install

%files
%license OSS_DISCLOSURES.md LICENSE-nestybox LICENSE-karellen
%config %{_sysconfdir}/sysconfig/docker-karellen-sysbox
%config %{_sysconfdir}/docker/daemon-karellen-sysbox.json

%{_bindir}/sysbox-fs
%{_bindir}/sysbox-mgr
%{_bindir}/sysbox-runc
%{_bindir}/sysbox
%{_sysctldir}/99-sysbox-sysctl.conf
%{_unitdir}/sysbox-fs.service
%{_unitdir}/sysbox-mgr.service
%{_unitdir}/sysbox.service

%post
%sysctl_apply 99-sysbox-sysctl.conf
%systemd_post sysbox-fs.service sysbox-mgr.service sysbox.service

%preun
%systemd_preun sysbox-fs.service sysbox-mgr.service sysbox.service

%postun
%systemd_postun_with_restart sysbox-fs.service sysbox-mgr.service sysbox.service

%changelog
* Sun Apr 30 2023 Arcadiy Ivanov <arcadiy@ivanov.biz> 0.6.1.17-2
- Remove Debian-only kernel sysctl (arcadiy@ivanov.biz)

