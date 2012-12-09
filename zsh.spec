%define _disable_ld_no_undefined 1

# The version flow of zsh: N - N-dev-1 - ... - (N+1)-pre-1 ... (N+1)
#define dev 0
#define pre 0
%define zshversion 5.0.0

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
Release: %{?pre:0.pre%{pre}.}2
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
BuildRequires:	termcap-devel >= 2.0
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
%if %{mdvver} < 201100
%_install_info %name.info
%endif

%preun
%if %{mdvver} <= 201100
%_remove_install_info %name.info
%endif
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
%doc docroot/Documentation/ docroot/Examples/ docroot/Info_html/
%doc docroot/StartupFiles/ docroot/Zsh_Guide ChangeLog* LICENCE


%changelog
* Wed Jul 25 2012 Dmitry Mikhirev <dmikhirev@mandriva.org> 1:5.0.0-1mdv2012.0
+ Revision: 811004
- 5.0.0 stable release

* Fri Feb 24 2012 Alexander Khrukin <akhrukin@mandriva.org> 1:4.3.17-3
+ Revision: 780111
- version update 4.3.17

* Tue Feb 07 2012 Oden Eriksson <oeriksson@mandriva.com> 1:4.3.15-3
+ Revision: 771607
- bump release

* Wed Dec 21 2011 Dmitry Mikhirev <dmikhirev@mandriva.org> 1:4.3.15-2
+ Revision: 744220
- release bump
- BR fixed

* Sat May 07 2011 Oden Eriksson <oeriksson@mandriva.com> 1:4.3.11-2
+ Revision: 671962
- mass rebuild

* Mon Dec 20 2010 Andrey Borzenkov <arvidjaar@mandriva.org> 1:4.3.11-1mdv2011.0
+ Revision: 623426
- update to final 4.3.11

* Sun Nov 07 2010 Andrey Borzenkov <arvidjaar@mandriva.org> 1:4.3.10.dev2-1mdv2011.0
+ Revision: 594777
- update to 4.3.10-dev-2
  remove upstream patches 100, 101, 102
  updated zshguide to fix build (not sure why it suddenly breaks)

* Wed Mar 17 2010 Oden Eriksson <oeriksson@mandriva.com> 1:4.3.10-4mdv2010.1
+ Revision: 524495
- rebuilt for 2010.1

* Wed Jul 01 2009 Andrey Borzenkov <arvidjaar@mandriva.org> 1:4.3.10-3mdv2010.0
+ Revision: 391312
- patch102: in scrollist keymap allow accept-search to exit but do nothing else (27085)
- patch101: it wasn't possible to exit menu selection cleanly (27080)

* Sun Jun 28 2009 Andrey Borzenkov <arvidjaar@mandriva.org> 1:4.3.10-2mdv2010.0
+ Revision: 390233
- patch100: support lzma compressed man pages

* Mon Jun 01 2009 Andrey Borzenkov <arvidjaar@mandriva.org> 1:4.3.10-1mdv2010.0
+ Revision: 381951
- new version
- clean up specs, remove obsolete patches

* Sat Mar 14 2009 Andrey Borzenkov <arvidjaar@mandriva.org> 1:4.3.9-5mdv2009.1
+ Revision: 354876
- disable patch101 - origin unknown
- new CVS snapshot 1.4614
- generate full contents of zshall.1 during install as suggested by Dan Nelson
  on zsh-workers (bug 47634)
- preun scripts should run in preun not post

* Sun Feb 08 2009 Andrey Borzenkov <arvidjaar@mandriva.org> 1:4.3.9-4mdv2009.1
+ Revision: 338473
- no more buildrequire autoconf
- use 'emulate -R sh -c "source ..."' to source /etc/profile.d scripts in
  sh emulation mode
- update to current SVN (ZSH_PATCHLEVEL 1.4554)
  * remove patch102 (upstream)
  * remove patch500 (upstream)
- disable patch2 - rpm -A does not seem to exist anymore
- disable patch1 - we do not have /usr/X11R6 for a long time

* Thu Jan 08 2009 Andrey Borzenkov <arvidjaar@mandriva.org> 1:4.3.9-3mdv2009.1
+ Revision: 327122
- update source2
  * /etc/zshenv: do not set PATH, it does not belong here (also fixes 22947)
  * /etc/zshrc: set sh emulation while sourcing /etc/profile.d
  * /etc/zshrc: use terminfo for key bindings

* Mon Jan 05 2009 Andrey Borzenkov <arvidjaar@mandriva.org> 1:4.3.9-2mdv2009.1
+ Revision: 325038
- make install, not install-strip, to preserve debugging information
- remove obsolete configure options
- use autoreconf to update configure after patch500
- fix compilation with -Werror=format-security
- rediff patch101 (fuzzy)
- rediff patch2 (fuzzy)

* Tue Nov 04 2008 Andrey Borzenkov <arvidjaar@mandriva.org> 1:4.3.9-1mdv2009.1
+ Revision: 299794
- buildrequires gdbm-devel for db_gdbm module
- disable --no-undefined; currently zsh modules do not build with it
- new version

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild early 2009.0 package (before pixel changes)

* Sat Apr 19 2008 Andrey Borzenkov <arvidjaar@mandriva.org> 1:4.3.6-1mdv2009.0
+ Revision: 195850
- new version

* Sat Feb 02 2008 Andrey Borzenkov <arvidjaar@mandriva.org> 1:4.3.5-1mdv2008.1
+ Revision: 161351
- New version; also
  * remove patch500 (is upstream)
  * Zsh is not under GPL, change licence to BSD-like
  * include LICENCE in doc package

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Thu May 10 2007 Andrey Borzenkov <arvidjaar@mandriva.org> 1:4.3.4-4mdv2008.0
+ Revision: 25968
- patch500: fix prompt display after ^D with both prpomptsp and ignoreeof
  (zsh-workers/23409)

* Wed May 09 2007 Andrey Borzenkov <arvidjaar@mandriva.org> 1:4.3.4-3mdv2008.0
+ Revision: 25700
- revert source3 change; profile.d contains quite a number of scripts that
  expect interactive shell with tty. Actually even bash sources it twice -
  in profile and bashrc

* Wed May 09 2007 Andrey Borzenkov <arvidjaar@mandriva.org> 1:4.3.4-2mdv2008.0
+ Revision: 25423
- use macros to add/del shell now that they work (requires rpm-helper >= 0.18.5)
- update Source3: Move sourcing of /etc/profile.d in /etc/zprofile
  from /etc/zshrc. There is no reason to do it in every interactive shell.
  For GUI profile.d is implicitly sourced by Xsession (by virtue of --login
  option)

* Tue May 01 2007 Andrey Borzenkov <arvidjaar@mandriva.org> 1:4.3.4-1mdv2008.0
+ Revision: 19916
- use --with-tcsetpgrp to avoid build bot failure
- reset executable bit on functions to avoid dependency on /usr/bin/zsh
- updated zshguide and its URL
- rediff patch102 (Zsh is now using Mandriva not Mandrake)
- new version 4.3.4 (fixes #18939)
- uncompress patches; spec cleanup

  + Nicolas Lécureuil <nlecureuil@mandriva.com>
    - Import zsh

