%global debug_package %{nil}

%global __strip /bin/true

%global __brp_mangle_shebangs /bin/true

Name: atlassian-fisheye
Epoch: 100
Version: 4.8.10
Release: 1%{?dist}
BuildArch: noarch
Summary: Atlassian Fisheye
License: Apache-2.0
URL: https://www.atlassian.com/software/fisheye
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: fdupes
Requires(pre): shadow-utils
Requires: java

%description
Fisheye is the on-premise source code repository browser for enterprise
teams. It provides your developers with advanced browsing and search for
SVN, Git, Mercurial, Perforce and CVS code repositories, from any web
browser.

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%install
install -Dpm755 -d %{buildroot}%{_unitdir}
install -Dpm755 -d %{buildroot}/opt/atlassian/fisheye
cp -rfT fisheye %{buildroot}/opt/atlassian/fisheye
install -Dpm644 -t %{buildroot}%{_unitdir} fisheye.service
chmod a+x %{buildroot}/opt/atlassian/fisheye/bin/start.sh
chmod a+x %{buildroot}/opt/atlassian/fisheye/bin/stop.sh
fdupes -qnrps %{buildroot}/opt/atlassian/fisheye

%check

%pre
set -euxo pipefail

FISHEYE_HOME=/var/atlassian/application-data/fisheye

if [ ! -d $FISHEYE_HOME -a ! -L $FISHEYE_HOME ]; then
    mkdir -p $FISHEYE_HOME
fi

if ! getent group fisheye >/dev/null; then
    groupadd \
        --system \
        fisheye
fi

if ! getent passwd fisheye >/dev/null; then
    useradd \
        --system \
        --gid fisheye \
        --home-dir $FISHEYE_HOME \
        --no-create-home \
        --shell /usr/sbin/nologin \
        fisheye
fi

chown -Rf fisheye:fisheye $FISHEYE_HOME
chmod 0750 $FISHEYE_HOME

%post
set -euxo pipefail

FISHEYE_CATALINA=/opt/atlassian/fisheye

chown -Rf fisheye:fisheye $FISHEYE_CATALINA
chmod 0700 $FISHEYE_CATALINA

%files
%license LICENSE
%dir /opt/atlassian
%{_unitdir}/fisheye.service
/opt/atlassian/fisheye

%changelog
