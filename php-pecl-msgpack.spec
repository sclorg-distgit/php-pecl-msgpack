# centos/sclo spec file for php-pecl-msgpack, from:
#
# remirepo spec file for php-pecl-msgpack
# with SCL compatibility, from:
#
# Fedora spec file for php-pecl-msgpack
#
# Copyright (c) 2012-2019 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%if 0%{?scl:1}
%global sub_prefix  %{scl_prefix}
%if "%{scl}" == "rh-php70"
%global sub_prefix  sclo-php70-
%endif
%if "%{scl}" == "rh-php71"
%global sub_prefix  sclo-php71-
%endif
%if "%{scl}" == "rh-php72"
%global sub_prefix  sclo-php72-
%endif
%if "%{scl}" == "rh-php73"
%global sub_prefix  sclo-php73-
%endif
%scl_package        php-pecl-msgpack
%endif

%global pecl_name   msgpack
%global with_zts    0%{!?_without_zts:%{?__ztsphp:1}}
%global ini_name    40-%{pecl_name}.ini

Summary:       API for communicating with MessagePack serialization
Name:          %{?sub_prefix}php-pecl-msgpack
Version:       2.0.3
Release:       1%{?dist}%{!?scl:%{!?nophptag:%(%{__php} -r 'echo ".".PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')}}
Source:        http://pecl.php.net/get/%{pecl_name}-%{version}.tgz
License:       BSD
Group:         Development/Languages
URL:           http://pecl.php.net/package/msgpack

Patch1:        https://patch-diff.githubusercontent.com/raw/msgpack/msgpack-php/pull/125.patch

BuildRequires: %{?scl_prefix}php-devel >= 7
BuildRequires: %{?scl_prefix}php-pear
# https://github.com/msgpack/msgpack-php/issues/25
ExcludeArch: ppc64

Requires:      %{?scl_prefix}php(zend-abi) = %{php_zend_api}
Requires:      %{?scl_prefix}php(api) = %{php_core_api}

Provides:      %{?scl_prefix}php-%{pecl_name}               = %{version}
Provides:      %{?scl_prefix}php-%{pecl_name}%{?_isa}       = %{version}
Provides:      %{?scl_prefix}php-pecl(%{pecl_name})         = %{version}
Provides:      %{?scl_prefix}php-pecl(%{pecl_name})%{?_isa} = %{version}
%if "%{?scl_prefix}" != "%{?sub_prefix}"
Provides:      %{?scl_prefix}php-pecl-%{pecl_name}          = %{version}-%{release}
Provides:      %{?scl_prefix}php-pecl-%{pecl_name}%{?_isa}  = %{version}-%{release}
%endif

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter shared private
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif


%description
This extension provide API for communicating with MessagePack serialization.

MessagePack is an efficient binary serialization format. It lets you exchange
data among multiple languages like JSON but it's faster and smaller.
For example, small integers (like flags or error code) are encoded into a
single byte, and typical short strings only require an extra byte in addition
to the strings themselves.

If you ever wished to use JSON for convenience (storing an image with metadata)
but could not for technical reasons (encoding, size, speed...), MessagePack is
a perfect replacement.

Package built for PHP %(%{__php} -r 'echo PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')%{?scl: as Software Collection (%{scl} by %{?scl_vendor}%{!?scl_vendor:rh})}.


%package devel
Summary:       MessagePack developer files (header)
Group:         Development/Libraries
Requires:      %{name}%{?_isa} = %{version}-%{release}
Requires:      %{?scl_prefix}php-devel%{?_isa}
%if "%{?scl_prefix}" != "%{?sub_prefix}"
Provides:      %{?scl_prefix}php-pecl-%{pecl_name}-devel         = %{version}-%{release}
Provides:      %{?scl_prefix}php-pecl-%{pecl_name}-devel%{?_isa} = %{version}-%{release}
%endif

%description devel
These are the files needed to compile programs using MessagePack serializer.


%prep
%setup -qc
mv %{pecl_name}-%{version} NTS

%{?_licensedir:sed -e '/LICENSE/s/role="doc"/role="src"/' -i package.xml}

cd NTS
%patch1 -p1 -b .pr125

# Sanity check, really often broken
extver=$(sed -n '/#define PHP_MSGPACK_VERSION/{s/.* "//;s/".*$//;p}' php_msgpack.h)
if test "x${extver}" != "x%{version}%{?gh_date:-dev}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}%{?gh_date:-dev}.
   exit 1
fi
cd ..

# Drop in the bit of configuration
cat > %{ini_name} << 'EOF'
; Enable MessagePack extension module
extension = %{pecl_name}.so

; Configuration options

;msgpack.error_display = On
;msgpack.illegal_key_insert = Off
;msgpack.php_only = On
EOF


%build
cd NTS
%{_bindir}/phpize
%configure --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}


%install
# Install the NTS stuff
make -C NTS install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# Install the package XML file
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

# Test & Documentation
cd NTS
for i in $(grep 'role="test"' ../package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 $i %{buildroot}%{pecl_testdir}/%{pecl_name}/$i
done
for i in $(grep 'role="doc"' ../package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 $i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%check
# __autoload is deprecated
rm */tests/019.phpt
# Erratic results
rm */tests/034.phpt
rm */tests/035.phpt
# Known by upstream as failed test (travis result)
rm */tests/041.phpt
rm */tests/040*.phpt

cd NTS
: Minimal load test for NTS extension
%{__php} --no-php-ini \
    --define extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}

: Upstream test suite  for NTS extension
TEST_PHP_EXECUTABLE=%{__php} \
TEST_PHP_ARGS="-n -d extension_dir=$PWD/modules -d extension=%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{__php} -n run-tests.php --show-diff


# when pear installed alone, after us
%triggerin -- %{?scl_prefix}php-pear
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

# posttrans as pear can be installed after us
%posttrans
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

%postun
if [ $1 -eq 0 -a -x %{__pecl} ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%files
%{?_licensedir:%license NTS/LICENSE}
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so


%files devel
%doc %{pecl_testdir}/%{pecl_name}
%{php_incldir}/ext/%{pecl_name}


%changelog
* Tue Jul 23 2019 Remi Collet <remi@remirepo.net> - 2.0.3-1
- update to 2.0.3

* Thu Nov 15 2018 Remi Collet <remi@remirepo.net> - 2.0.2-3
- build for sclo-php72

* Thu Aug 10 2017 Remi Collet <remi@remirepo.net> - 2.0.2-2
- change for sclo-php71

* Wed Feb 15 2017 Remi Collet <remi@fedoraproject.org> - 2.0.2-1
- cleanup for SCLo build

* Wed Dec  7 2016 Remi Collet <remi@fedoraproject.org> - 2.0.2-1
- update to 2.0.2

* Thu Dec  1 2016 Remi Collet <remi@fedoraproject.org> - 2.0.1-5
- rebuild with PHP 7.1.0 GA

* Wed Sep 14 2016 Remi Collet <remi@fedoraproject.org> - 2.0.1-4
- rebuild for PHP 7.1 new API version

* Sat Jul 23 2016 Remi Collet <remi@fedoraproject.org> - 2.0.1-3
- ignore more tests with 7.1

* Sat Jun 11 2016 Remi Collet <remi@fedoraproject.org> - 2.0.1-2
- add patch for PHP 7.1
  open https://github.com/msgpack/msgpack-php/pull/87

* Tue Mar  1 2016 Remi Collet <remi@fedoraproject.org> - 2.0.1-1
- update to 2.0.1 (php 7, beta)
- use sources from pecl

* Tue Oct 27 2015 Remi Collet <remi@fedoraproject.org> - 2.0.0-1
- update to 2.0.0 (php 7, beta)

* Wed Oct 14 2015 Remi Collet <remi@fedoraproject.org> - 2.0.0-0.1.20151014git75991cf
- new snapshot, version bump to 2.0.0dev

* Tue Oct 13 2015 Remi Collet <remi@fedoraproject.org> - 0.5.7-0.7.20151002git7a5bdb1
- rebuild for PHP 7.0.0RC5 new API version
- new snapshot

* Fri Sep 18 2015 Remi Collet <remi@fedoraproject.org> - 0.5.7-0.6.20150702gitce27a10
- F23 rebuild with rh_layout

* Wed Jul 22 2015 Remi Collet <remi@fedoraproject.org> - 0.5.7-0.5.20150702gitce27a10
- rebuild against php 7.0.0beta2

* Wed Jul  8 2015 Remi Collet <remi@fedoraproject.org> - 0.5.7-0.4.20150702gitce27a10
- new snapshot, rebuild against php 7.0.0beta1

* Wed Jun 24 2015 Remi Collet <remi@fedoraproject.org> - 0.5.7-0.3.20150612git95c8dc3
- allow build against rh-php56 (as more-php56)
- rebuild for "rh_layout" (php70)

* Fri Jun 12 2015 Remi Collet <remi@fedoraproject.org> - 0.5.7-0.1.20150612git95c8dc3
- update to 0.5.7dev for PHP 7
- sources from github

* Mon Apr 27 2015 Remi Collet <remi@fedoraproject.org> - 0.5.6-1
- Update to 0.5.6
- drop runtime dependency on pear, new scriptlets

* Wed Dec 24 2014 Remi Collet <remi@fedoraproject.org> - 0.5.5-8.1
- Fedora 21 SCL mass rebuild

* Sun Aug 24 2014 Remi Collet <remi@fedoraproject.org> - 0.5.5-8
- improve SCL stuff

* Wed Apr  9 2014 Remi Collet <remi@fedoraproject.org> - 0.5.5-7
- add numerical prefix to extension configuration file

* Wed Mar 19 2014 Remi Collet <rcollet@redhat.com> - 0.5.5-6
- allow SCL build

* Fri Feb 28 2014 Remi Collet <remi@fedoraproject.org> - 0.5.5-5
- cleanups
- move doc in pecl_docdir
- move tests in pecl_testdir (devel)

* Thu Jul 18 2013 Remi Collet <remi@fedoraproject.org> - 0.5.5-4
- bump release

* Thu Apr 18 2013 Remi Collet <remi@fedoraproject.org> - 0.5.5-4
- ExcludeArch: ppc64 (as msgpack)

* Tue Apr  2 2013 Remi Collet <remi@fedoraproject.org> - 0.5.5-3
- use system msgpack library headers

* Tue Mar 26 2013 Remi Collet <remi@fedoraproject.org> - 0.5.5-2
- cleanups

* Wed Feb 20 2013 Remi Collet <remi@fedoraproject.org> - 0.5.5-1
- Update to 0.5.5

* Fri Nov 30 2012 Remi Collet <remi@fedoraproject.org> - 0.5.3-1.1
- also provides php-msgpack

* Thu Oct 18 2012 Remi Collet <remi@fedoraproject.org> - 0.5.3-1
- update to 0.5.3 (beta)

* Sat Sep 15 2012 Remi Collet <remi@fedoraproject.org> - 0.5.2-1
- initial package, version 0.5.2 (beta)

