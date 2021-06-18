Name:		edeployPOS
Version:	1.0
Release:	0
Summary:	Install edeployPOS
License:	GPL
BuildArch:      x86_64

Source0:        %{name}.tar.gz

Requires:	bash yum unzip epel-release wget

BuildRoot:      %{_tmppath}

%description

%prep
%setup -q

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_bindir} $RPM_BUILD_ROOT/%{_tmppath}
cp -r edeployPOS-1.0/install_edeploypos $RPM_BUILD_ROOT/%{_bindir}
cp -r edeployPOS-1.0/ansible.zip $RPM_BUILD_ROOT/%{_tmppath}
cp -r edeployPOS-1.0/application.zip $RPM_BUILD_ROOT/%{_tmppath}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%{_bindir}/install_edeploypos
%{_tmppath}/ansible.zip
%{_tmppath}/application.zip

%post
unzip -oq %{_tmppath}/ansible.zip -d %{getenv:HOME}
unzip -oq %{_tmppath}/application.zip -d %{getenv:HOME}

%changelog

