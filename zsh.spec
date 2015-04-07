%define _disable_ld_no_undefined 1

# The version flow of zsh: N - N-dev-1 - ... - (N+1)-pre-1 ... (N+1)
#define dev 0
#define pre 0
%define zshversion 5.0.7

%if %{?dev:1}%{!?dev:0} && %{?pre:1}%{!?pre:0}
%{error:Both %%pre and %%dev defined}
%endif

%if %{?dev:1}%{!?dev:0} || %{?pre:1}%{!?pre:0}
%define devdir development/
%endif

%define srcversion %{zshversion}%{?pre:-pre-%{pre}}%{?dev:-dev-%{dev}}

Summary: A shell with lots of features
Name:    zsh
Version: %zshversion%{?dev:.dev%{dev}}
Release: %{?pre:0.pre%{pre}.}1
Epoch: 1
License: BSD-like
Group: Shells
Url: http://www.zsh.org
Source0: http://www.zsh.org/pub/%{?devdir}%name-%{srcversion}.tar.bz2
Source1: http://www.zsh.org/pub/%{?devdir}%name-%{srcversion}-doc.tar.bz2
Source2: zcfg-mdk.tar.bz2
Source3: http://zsh.dotsrc.org/Guide/zshguide.tar.gz
Source4: zsh.urpmi_comp
Source5: zsh.rpmlintrc

# Upstream patches (none at the moment)

Requires(postun): rpm-helper
Requires(post): rpm-helper
BuildRequires:	pkgconfig(ncurses)
#BuildRequires:	termcap-devel >= 2.0
BuildRequires:	texinfo
BuildRequires:	yodl
BuildRequires:	pcre-devel
BuildRequires: rpm-helper >= 0.18.5
BuildRequires: gdbm-devel
BuildRequires: groff
Provides:	/bin/zsh
Provides:	/usr/bin/zsh

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
%apply_patches

mv %name-%{srcversion}/Doc/* Doc/
install -m 0644 %{SOURCE4}  Completion/Mandriva/Command/_urpmi

# remove temporary files
find | grep '~$' | xargs rm -f
perl -pi -e 's|/usr/local/bin/|%_bindir/|' Functions/Misc/{run-help,checkmail,zcalc}

%build

# check for tcsetpgrp fails with "configure: error: no controlling tty" when
# building by bot; force tcsetpgrp
%configure2_5x \
	--enable-etcdir=%_sysconfdir \
	--enable-function-subdirs \
%ifarch sparc
	--disable-lfs \
%endif
	--enable-pcre \
	--with-tcsetpgrp
make all

%install
make install DESTDIR=%buildroot
make install.info DESTDIR=%buildroot

# copy Mandriva Configuration files.
mkdir -p %{buildroot}/{bin,etc}
cp -a zcfg/etc/z* %{buildroot}%_sysconfdir
cp -a zcfg/share/zshrc_default %buildroot%_datadir/zsh/%srcversion/zshrc_default

# this prevents RPM helper from adding dependency on /usr/bin/zsh
find %buildroot%_datadir/zsh/%srcversion -type f -exec chmod 0644 '{}' \;

# Backward compatibilie should be removed in the others times.
pushd %{buildroot}/bin && {
    mv ..%_bindir/zsh ./zsh
} && popd

# zshall.1 includes all other man pages which does not work with compressed
# files. Generate full contents here
pushd %{buildroot}%_mandir && {
	/usr/bin/soelim man1/zshall.1 > zshall-full
	mv zshall-full man1/zshall.1
	popd
}

rm -f %{buildroot}%_bindir/zsh-%srcversion

# Copy documentation.
rm -rf docroot
mkdir -p docroot/{Info_html,Examples,Documentation}/

cp -a README docroot/
cp -a Functions/Misc/* Misc/* Util/* docroot/Examples/
cp -a ChangeLog* docroot/Documentation 
cp -a StartupFiles docroot/
cp -a Etc/* docroot/Documentation
cp -a Doc/*html docroot/Info_html/

mkdir -p docroot/Zsh_Guide
tar xzf %SOURCE3 -C docroot/Zsh_Guide
( cd docroot/Zsh_Guide/zshguide/ ; make )  
mv docroot/Zsh_Guide/zshguide/*html docroot/Zsh_Guide/
rm -Rf docroot/Zsh_Guide/zshguide/

# Doc
rm -f docroot/{StartupFiles/.distfiles,Examples/{Makefile*,*.yo},Documentation/{Makefile*,*.yo}}
find docroot/ -name 'Makefile*' -o -name '.yo'|xargs rm -f
find docroot/ -type f|xargs perl -pi -e 's@^#!%_prefix/local/bin/(perl|zsh)@#!%_bindir/\1@'
mv docroot/Examples/compctl-examples docroot/StartupFiles

%post
%_post_shelladd /bin/zsh

%preun
%_preun_shelldel /bin/zsh

%files
%defattr(-,root,root,0755)
%doc docroot/README NEWS
%config(noreplace) %_sysconfdir/z*
/bin/%name
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
