%define _disable_ld_no_undefined 1

#define dev 0
#define pre 0
%define zshversion 4.3.10

%if %{?dev:1}%{!?dev:0} && %{?pre:1}%{!?pre:0}
%{error:Both %%pre and %%dev defined}
%endif

%define srcversion %{zshversion}%{?pre:-pre-%{pre}}%{!?pre:%{?dev:-dev-%dev}}

Summary: A shell with lots of features
Name:    zsh
Version: %zshversion
Release: %mkrel 2
Url: http://www.zsh.org
License: BSD-like
Group: Shells
Source0: http://www.zsh.org/pub/%name-%{srcversion}.tar.bz2
Source1: http://www.zsh.org/pub/%name-%{srcversion}-doc.tar.bz2
Source2: zcfg-mdk.tar.bz2
Source3: http://zsh.dotsrc.org/Guide/zshguide.tar.gz
Source4: zsh.urpmi_comp

# Upstream patches
# patch100: support lzma suffix in man pages
Patch100: zsh-4.3.10-man_lzma.patch

Requires(postun): rpm-helper
Requires(post): rpm-helper
Epoch: 1
BuildRequires: ncurses-devel libtermcap-devel >= 2.0, texinfo yodl pcre-devel
BuildRequires: rpm-helper >= 0.18.5
BuildRequires: gdbm-devel
BuildRequires: groff

BuildRoot: %_tmppath/%name-buildroot

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
%patch100 -p0 -b .man_lzma

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
rm -rf $RPM_BUILD_ROOT

make install DESTDIR=%buildroot
make install.info DESTDIR=%buildroot

# copy Mandriva Configuration files.
mkdir -p $RPM_BUILD_ROOT/{bin,etc}
cp -a zcfg/etc/z* $RPM_BUILD_ROOT%_sysconfdir
cp -a zcfg/share/zshrc_default %buildroot%_datadir/zsh/%srcversion/zshrc_default

# this prevents RPM helper from adding dependency on /usr/bin/zsh
find %buildroot%_datadir/zsh/%srcversion -type f -exec chmod 0644 '{}' \;

# Backward compatibilie should be removed in the others times.
pushd $RPM_BUILD_ROOT/bin && {
    mv ..%_bindir/zsh ./zsh
} && popd

# zshall.1 includes all other man pages which does not work with compressed
# files. Generate full contents here
pushd $RPM_BUILD_ROOT%_mandir && {
	/usr/bin/soelim man1/zshall.1 > zshall-full
	mv zshall-full man1/zshall.1
	popd
}

rm -f $RPM_BUILD_ROOT%_bindir/zsh-%srcversion

# Copy documentation.
rm -rf docroot
mkdir -p docroot/{Info_html,Examples,Documentation}/

cp -a README docroot/
cp -a Functions/Misc/* Misc/* Util/* docroot/Examples/
cp -a INSTALL ChangeLog* docroot/Documentation 
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

%clean
rm -rf $RPM_BUILD_ROOT

%post
%_post_shelladd /bin/zsh
%_install_info %name.info

%preun
%_remove_install_info %name.info
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
%_datadir/zsh/%{srcversion}/scripts
%_datadir/zsh/%{srcversion}/zshrc_default
%dir %_libdir/zsh
%_libdir/zsh/%{srcversion}/
%_datadir/zsh/site-functions/

%files doc
%defattr(-,root,root)
%doc docroot/Documentation/ docroot/Examples/ docroot/Info_html/
%doc docroot/StartupFiles/ docroot/Zsh_Guide ChangeLog* LICENCE
