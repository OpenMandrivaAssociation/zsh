
Summary: A shell with lots of features
Name:    zsh
Version: 4.3.4
Release: %mkrel 1
Url: http://www.zsh.org
Source0: http://www.zsh.org/pub//%name-%{version}.tar.bz2
Source1: http://www.zsh.org/pub//%name-%{version}-doc.tar.bz2
Source2: zcfg-mdk.tar.bz2
Source3: http://zsh.sunsite.dk/Guide/zshguide.tar.bz2
Source4: zsh.urpmi_comp
Patch1: zsh-3.1.6-dev-22-path.patch
Patch2: zsh-4.0.1-pre-3-rpmnewopt.patch
Patch101: zsh-serial.patch
Patch102: zsh-4.1.0-dev-7-rebootin.patch
License: GPL
Group: Shells
Requires(postun): rpm-helper
Requires(post): rpm-helper
Epoch: 1
BuildRequires: ncurses-devel libtermcap-devel >= 2.0, texinfo yodl pcre-devel
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
%setup -q -a 2 -a 1 -n %name-%version
mv %name-%{version}/Doc/* Doc/
%patch1 -p1
%patch2 -p1
%patch101 -p1
%patch102 -p1
install -m 0644 %{SOURCE4}  Completion/Mandriva/Command/_urpmi

# remove temporary files
find | grep '~$' | xargs rm -f
perl -pi -e 's|/usr/local/bin/|%_bindir/|' Functions/Misc/{run-help,checkmail,zcalc}

%build
%ifarch sparc
EXTRA_CONFIGURE_ARGS="--disable-lfs"
%endif
%configure2_5x \
	--enable-etcdir=%_sysconfdir \
	--enable-function-subdirs \
	--disable-debug $EXTRA_CONFIGURE_FLAGS \
	--disable-max-jobtable-size \
	--enable-pcre
	#--with-curses-terminfo
make all

%install
rm -rf $RPM_BUILD_ROOT

make install-strip DESTDIR=%buildroot
make install.info DESTDIR=%buildroot

# copy Mandriva Configuration files.
mkdir -p $RPM_BUILD_ROOT/{bin,etc}
cp -a zcfg/etc/z* $RPM_BUILD_ROOT%_sysconfdir
cp -a zcfg/share/zshrc_default %buildroot%_datadir/zsh/%version/zshrc_default

# Backward compatibilie should be removed in the others times.
pushd $RPM_BUILD_ROOT/bin && {
    mv ..%_bindir/zsh ./zsh
} && popd

rm -f $RPM_BUILD_ROOT%_bindir/zsh-%version

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
tar xjf %SOURCE3 -C docroot/Zsh_Guide
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
/usr/share/rpm-helper/add-shell %name $1 /bin/zsh
%_install_info %name.info

%postun
/usr/share/rpm-helper/del-shell %name $1 /bin/zsh
%_remove_install_info %name.info

%files
%defattr(-,root,root,0755)
%doc docroot/README NEWS
%config(noreplace) %_sysconfdir/z*
/bin/%name
%_mandir/man1/*.1*
%_infodir/*.info*
%dir %_datadir/zsh
%dir %_datadir/zsh/%{version}/
%_datadir/zsh/%{version}/functions
%_datadir/zsh/%{version}/scripts
%_datadir/zsh/%{version}/zshrc_default
%dir %_libdir/zsh
%_libdir/zsh/%{version}/
%_datadir/zsh/site-functions/

%files doc
%defattr(-,root,root)
%doc docroot/Documentation/ docroot/Examples/ docroot/Info_html/ docroot/StartupFiles/
%doc docroot/Zsh_Guide ChangeLog*
