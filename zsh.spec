%define _disable_ld_no_undefined 1
%define _disable_lto 1

# The version flow of zsh: N - N-dev-1 - ... - (N+1)-pre-1 ... (N+1)
#define dev 0
#define pre 0

%if %{?dev:1}%{!?dev:0} && %{?pre:1}%{!?pre:0}
%{error:Both %%pre and %%dev defined}
%endif

%if %{?dev:1}%{!?dev:0} || %{?pre:1}%{!?pre:0}
%define devdir development/
%endif

%define srcversion %{version}%{?pre:-pre-%{pre}}%{?dev:-dev-%{dev}}

Summary:	A shell with lots of features
Name:		zsh
Version:	5.9
Release:	5
License:	BSD-like
Group:		Shells
Url:		http://www.zsh.org
Source0:	http://www.zsh.org/pub/%{?devdir}%name-%{srcversion}.tar.xz
Source1:	http://www.zsh.org/pub/%{?devdir}%name-%{srcversion}-doc.tar.xz
Source2:	zcfg-omv.tar.bz2
Source3:	http://zsh.sourceforge.net/Guide/zshguide.tar.gz
Source4:	zsh.urpmi_comp
Source5:	zsh.rpmlintrc

# FIXME this makes it build, but needs more patches to restore
# some formatting. Is the guide even still useful, given it dates
# back to the days of yodl 1.0?
Patch0:		zsh-doc-5.7.1-yodl-4.0.patch
Patch1:		https://869539.bugs.gentoo.org/attachment.cgi?id=804520&action=diff&format=raw&headers=1#/zsh-clang15.patch
Patch2:		0004-zsh-enable-PCRE-locale-switching.patch
Patch3:		0005-zsh-port-to-pcre2.patch

# Upstream patches (none at the moment)
# https://sourceforge.net/p/zsh/code/ci/c6a85163619ed1cee89ab047a0d98108ed46828d/

Requires(postun):	rpm-helper
Requires(post):		rpm-helper
BuildRequires:		pkgconfig(ncurses)
#BuildRequires:	termcap-devel >= 2.0
BuildRequires:		texinfo
BuildRequires:		yodl
BuildRequires:		pkgconfig(libpcre2-posix)
BuildRequires:		rpm-helper >= 0.18.5
BuildRequires:		gdbm-devel
BuildRequires:		groff
Provides:		/bin/zsh
Provides:		/usr/bin/zsh

%description
Zsh is a UNIX command interpreter (shell) usable as an
interactive login shell and as a shell script command
processor. Of the standard shells, zsh most closely resembles
ksh but includes many enhancements. Zsh has command-line editing,
built-in spelling correction, programmable command completion,
shell functions (with autoloading), a history mechanism, and a
lots of other features

Install the zsh package if you'd like to try out a different shell.

%package doc
Summary: The doc package of zsh
Group: Books/Computer books

%description doc
Zsh is a UNIX command interpreter (shell) usable as an
interactive login shell and as a shell script command
processor. Of the standard shells, zsh most closely resembles
ksh but includes many enhancements. Zsh has command-line editing,
built-in spelling correction, programmable command completion,
shell functions (with autoloading), a history mechanism, and a
lots of other features

This package include doc guid examples and manual for zsh.

%prep
%setup -q -a 2 -a 1 -n %name-%srcversion
rm -rf docroot
mkdir -p docroot/{Info_html,Examples,Documentation,Zsh_Guide}/
tar xzf %SOURCE3 -C docroot/Zsh_Guide
sed -i -e 's,itemize(,itemization(,g;s,enumerate(,enumeration(,g;s,startdit(),description(,g;s,enddit(),),g;s,startit(),itemization(,g;s,endit(),),g;s,starteit(),enumeration(,g;s,endeit(),),g' docroot/Zsh_Guide/zshguide/*.yo
%autopatch -p1

mv %name-%{srcversion}/Doc/* Doc/
install -m 0644 %{SOURCE4}  Completion/Mandriva/Command/_urpmi

# remove temporary files
find | grep '~$' | xargs rm -f
perl -pi -e 's|/usr/local/bin/|%_bindir/|' Functions/Misc/{run-help,checkmail,zcalc}

autoreconf -fiv

%build

# check for tcsetpgrp fails with "configure: error: no controlling tty" when
# building by bot; force tcsetpgrp
%configure \
	--enable-etcdir=%_sysconfdir \
	--enable-function-subdirs \
%ifarch sparc
	--disable-lfs \
%endif
	--enable-pcre \
	--with-tcsetpgrp
%make_build all

%install
make install DESTDIR=%buildroot
make install.info DESTDIR=%buildroot

# copy Mandriva Configuration files.
mkdir -p %{buildroot}/{bin,etc}
cp -a zcfg/etc/z* %{buildroot}%_sysconfdir
cp -a zcfg/share/zshrc_default %buildroot%_datadir/zsh/%srcversion/zshrc_default

# this prevents RPM helper from adding dependency on /usr/bin/zsh
find %buildroot%_datadir/zsh/%srcversion -type f -exec chmod 0644 '{}' \;

# zshall.1 includes all other man pages which does not work with compressed
# files. Generate full contents here
pushd %{buildroot}%_mandir && {
	/usr/bin/soelim man1/zshall.1 > zshall-full
	mv zshall-full man1/zshall.1
	popd
}

rm -f %{buildroot}%_bindir/zsh-%srcversion

# Copy documentation.
cp -a README docroot/
cp -a Functions/Misc/* Misc/* Util/* docroot/Examples/
cp -a ChangeLog* docroot/Documentation 
cp -a StartupFiles docroot/
cp -a Etc/* docroot/Documentation
cp -a Doc/*html docroot/Info_html/

# Building Latex docs seems broken for the moment
( cd docroot/Zsh_Guide/zshguide/ ; make zshguide.html )  
mv docroot/Zsh_Guide/zshguide/*html docroot/Zsh_Guide/
rm -Rf docroot/Zsh_Guide/zshguide/

# Doc
rm -f docroot/{StartupFiles/.distfiles,Examples/{Makefile*,*.yo},Documentation/{Makefile*,*.yo}}
find docroot/ -name 'Makefile*' -o -name '.yo'|xargs rm -f
find docroot/ -type f|xargs perl -pi -e 's@^#!%_prefix/local/bin/(perl|zsh)@#!%_bindir/\1@'
mv docroot/Examples/compctl-examples docroot/StartupFiles

%post
%_post_shelladd %{_bindir}/zsh

%preun
%_preun_shelldel %{_bindir}/zsh

%files
%defattr(-,root,root,0755)
%doc docroot/README NEWS
%config(noreplace) %_sysconfdir/z*
%{_bindir}/%name
%_mandir/man1/*.1*
%_infodir/*.info*
%dir %_datadir/zsh
%dir %_datadir/zsh/%{srcversion}/
%_datadir/zsh/%{srcversion}/functions
%_datadir/zsh/%{srcversion}/help
%_datadir/zsh/%{srcversion}/scripts
%_datadir/zsh/%{srcversion}/zshrc_default
%dir %_libdir/zsh
%_libdir/zsh/%{srcversion}/
%_datadir/zsh/site-functions/

%files doc
%doc docroot/Documentation/ docroot/Examples/ docroot/Info_html/
%doc docroot/StartupFiles/ docroot/Zsh_Guide ChangeLog* LICENCE
