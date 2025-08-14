%global package_speccommit b4fd426e89c4b7c45ca9a2f807501acf67f671aa
%global usver 2.64
%global xsver 15
%global xsrel %{xsver}%{?xscount}%{?xshash}
Name:		ssmtp
Version:	2.64
Release: %{?xsrel}%{?dist}
Summary:	Extremely simple MTA to get mail off the system to a Mailhub
License:	GPLv2+
URL:		http://packages.debian.org/stable/mail/ssmtp
Source0: ssmtp-2.64.tar.bz2
Patch0: ssmtp-md5auth-non-rsa.patch
Patch1: ssmtp-garbage_writes.patch
Patch2: ssmtp-authpass.patch
Patch3: ssmtp-aliases.patch
Patch4: ssmtp-remote-addr.patch
Patch5: ssmtp-validate-TLS-server-cert.patch
Patch6: ssmtp-defaultvalues.patch
Patch7: ssmtp-configure-c99.patch
## Source0:	ftp://ftp.debian.org/debian/pool/main/s/%%{name}/%%{name}_%%{version}.orig.tar.bz2
Source1: mailq.8
Source2: newaliases.8

#hack around wrong requires for mutt and mdadm
%if 0%{?rhel}
Provides:	MTA smtpdaemon
%endif
%if 0%{?fedora} < 8
Provides:	MTA smtpdaemon
%endif
#Provides:	%%{_sbindir}/sendmail
#Provides:	%%{_bindir}/mailq
Requires(post):	%{_sbindir}/alternatives
Requires(preun):	%{_sbindir}/alternatives
BuildRequires: make
BuildRequires:  gcc
BuildRequires:	openssl-devel



%description
A secure, effective and simple way of getting mail off a system to your mail
hub. It contains no suid-binaries or other dangerous things - no mail spool
to poke around in, and no daemons running in the background. Mail is simply
forwarded to the configured mailhost. Extremely easy configuration.

WARNING: the above is all it does; it does not receive mail, expand aliases
or manage a queue. That belongs on a mail hub with a system administrator.


%prep
%autosetup -p1



%build
%configure --enable-ssl --enable-md5auth --enable-inet6
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
install -p -D -m 2750 %{name} %{buildroot}%{_sbindir}/%{name}
#install -p -D -m 755 generate_config_alt %{buildroot}%{_bindir}/generate_config_alt
mkdir %{buildroot}%{_bindir}/
install -p -D -m 644 revaliases %{buildroot}%{_sysconfdir}/ssmtp/revaliases
install -p -m 640 ssmtp.conf %{buildroot}%{_sysconfdir}/ssmtp/ssmtp.conf
install -p -D -m 644 ssmtp.8 %{buildroot}%{_mandir}/man8/ssmtp.8
install -m 644 %{SOURCE1} %{buildroot}%{_mandir}/man8/mailq.ssmtp.8
install -m 644 %{SOURCE2} %{buildroot}%{_mandir}/man8/newaliases.ssmtp.8
install -p -D -m 644 ssmtp.conf.5 %{buildroot}%{_mandir}/man5/ssmtp.conf.5
ln -s %{_sbindir}/%{name} %{buildroot}%{_sbindir}/sendmail.ssmtp
ln -s %{_sbindir}/%{name} %{buildroot}%{_bindir}/newaliases.ssmtp
ln -s %{_sbindir}/%{name} %{buildroot}%{_bindir}/mailq.ssmtp
touch %{buildroot}%{_sbindir}/sendmail
touch %{buildroot}%{_bindir}/mailq
touch %{buildroot}%{_bindir}/newaliases
touch %{buildroot}%{_mandir}/man8/mailq.8.gz
touch %{buildroot}%{_mandir}/man8/newaliases.8.gz
touch %{buildroot}%{_mandir}/man8/sendmail.8.gz

%post
%{_sbindir}/alternatives  --install %{_sbindir}/sendmail mta %{_sbindir}/sendmail.ssmtp 30 \
	--slave %{_bindir}/mailq mta-mailq %{_bindir}/mailq.ssmtp \
	--slave %{_bindir}/newaliases mta-newaliases %{_bindir}/newaliases.ssmtp \
	--slave %{_mandir}/man1/mailq.1.gz mta-mailqman %{_mandir}/man8/mailq.ssmtp.8.gz \
	--slave %{_mandir}/man1/newaliases.1.gz mta-newaliasesman %{_mandir}/man8/newaliases.ssmtp.8.gz \
	--slave %{_mandir}/man8/sendmail.8.gz mta-sendmailman %{_mandir}/man8/ssmtp.8.gz


%preun
#only remove in case of erase (but not at upgrade)
if [ $1 -eq 0 ] ; then
	%{_sbindir}/alternatives --remove mta %{_sbindir}/sendmail.ssmtp
fi
exit 0

%postun
if [ "$1" -ge "1" ]; then
	if [ "`readlink %{_sysconfdir}/alternatives/mta`" == "%{_sbindir}/sendmail.ssmtp" ]; then
		%{_sbindir}/alternatives --set mta %{_sbindir}/sendmail.ssmtp
	fi
fi

%files
%doc COPYING INSTALL README TLS CHANGELOG_OLD ChangeLog COPYRIGHT
%{_mandir}/man5/*
%{_mandir}/man8/*
%attr(2755, root, mail) %{_sbindir}/%{name}

%ghost %{_sbindir}/sendmail
%ghost %{_bindir}/mailq
%ghost %{_bindir}/newaliases
%ghost %{_mandir}/man8/mailq.8.gz
%ghost %{_mandir}/man8/newaliases.8.gz
%ghost %{_mandir}/man8/sendmail.8.gz

%{_sbindir}/sendmail.ssmtp
%{_bindir}/newaliases.ssmtp
%{_bindir}/mailq.ssmtp
%attr(2750, root, mail) %dir %{_sysconfdir}/ssmtp/
%config(noreplace) %{_sysconfdir}/ssmtp/revaliases
%attr(640, root, mail) %config(noreplace) %{_sysconfdir}/ssmtp/ssmtp.conf


%changelog
* Mon Oct 28 2024 Deli Zhang <deli.zhang@cloud.com> - 2.64-15
- Bump release to 15

* Wed May 29 2024 Stephen Cheng <stephen.cheng@cloud.com> - 2.64-1
- First imported release

