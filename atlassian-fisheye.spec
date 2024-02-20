# Copyright 2024 Wong Hoi Sing Edison <hswong3i@pantarei-design.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

%global debug_package %{nil}

%global source_date_epoch_from_changelog 0

%global __strip /bin/true

%global __brp_mangle_shebangs /bin/true

Name: atlassian-fisheye
Epoch: 100
Version: 4.8.15
Release: 1%{?dist}
Summary: Atlassian Fisheye
License: Apache-2.0
URL: https://www.atlassian.com/software/fisheye
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: -post-build-checks
Requires(pre): chrpath
Requires(pre): fdupes
Requires(pre): patch
Requires(pre): shadow-utils
Requires(pre): unzip
Requires(pre): wget

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
install -Dpm644 -t %{buildroot}%{_unitdir} fisheye.service
install -Dpm644 -t %{buildroot}/opt/atlassian atlassian-fisheye.patch

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

FISHEYE_DOWNLOAD_URL=http://product-downloads.atlassian.com/software/fisheye/downloads/fisheye-4.8.15.zip
FISHEYE_DOWNLOAD_DEST=/tmp/atlassian-fisheye-4.8.15.tar.gz
FISHEYE_DOWNLOAD_CHECKSUM=84e9b68f4f2f88dcf037635f44ab6db0b49971b106b5812abb01795d1241ec2e

FISHEYE_CATALINA=/opt/atlassian/fisheye
FISHEYE_PATCH=/opt/atlassian/atlassian-fisheye.patch

wget -c $FISHEYE_DOWNLOAD_URL -O $FISHEYE_DOWNLOAD_DEST
echo -n "$FISHEYE_DOWNLOAD_CHECKSUM $FISHEYE_DOWNLOAD_DEST" | sha256sum -c -

rm -rf $FISHEYE_CATALINA
mkdir -p $FISHEYE_CATALINA
TMP_DIR="$(mktemp -d)" && \
    unzip -d $TMP_DIR $FISHEYE_DOWNLOAD_DEST && \
    cp -rfT $TMP_DIR/* $FISHEYE_CATALINA && \
    rm -rf $TMP_DIR

cat $FISHEYE_PATCH | patch -p1 -d /
chmod a+x $FISHEYE_CATALINA/bin/start.sh
chmod a+x $FISHEYE_CATALINA/bin/stop.sh
find $FISHEYE_CATALINA -type f -name '*.so' -exec chrpath -d {} \;
find $FISHEYE_CATALINA -type f -name '*.bak' -delete
find $FISHEYE_CATALINA -type f -name '*.orig' -delete
find $FISHEYE_CATALINA -type f -name '*.rej' -delete
fdupes -qnrps $FISHEYE_CATALINA

chown -Rf fisheye:fisheye $FISHEYE_CATALINA
chmod 0700 $FISHEYE_CATALINA

%files
%license LICENSE
%dir /opt/atlassian
%dir /opt/atlassian/fisheye
%{_unitdir}/fisheye.service
/opt/atlassian//atlassian-fisheye.patch

%changelog
