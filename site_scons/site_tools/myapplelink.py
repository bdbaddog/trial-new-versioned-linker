import mylinker

def generate(env):
    mylinker.generate(env)

    env['FRAMEWORKPATHPREFIX'] = '-F'
    env['_FRAMEWORKPATH'] = '${_concat(FRAMEWORKPATHPREFIX, FRAMEWORKPATH, "", __env__, RDirs)}'

    env['_FRAMEWORKS'] = '${_concat("-framework ", FRAMEWORKS, "", __env__)}'
    env['LINKCOM'] = env['LINKCOM'] + ' $_FRAMEWORKPATH $_FRAMEWORKS $FRAMEWORKSFLAGS'
    env['SHLINKFLAGS'] = SCons.Util.CLVar('$LINKFLAGS -dynamiclib')
    env['SHLINKCOM'] = env['SHLINKCOM'] + ' $_FRAMEWORKPATH $_FRAMEWORKS $FRAMEWORKSFLAGS'

    # see: http://docstore.mik.ua/orelly/unix3/mac/ch05_04.htm  for proper naming
    SCons.Tool.linkCommon._setup_versioned_lib_variables(env, tool='applelink', use_soname=True)
    env['LINKCALLBACKS'] = SCons.Tool.linkCommon._versioned_lib_callbacks()
    env['LINKCALLBACKS']['VersionedShLibSuffix'] = _applelib_versioned_lib_suffix
    env['LINKCALLBACKS']['VersionedShLibSoname'] = _applelib_versioned_shlib_soname

    env['_APPLELINK_CURRENT_VERSION'] = _applelib_currentVersionFromSoVersion
    env['_APPLELINK_COMPATIBILITY_VERSION'] = _applelib_compatVersionFromSoVersion
    env['_SHLIBVERSIONFLAGS'] = '$_APPLELINK_CURRENT_VERSION $_APPLELINK_COMPATIBILITY_VERSION '
    env['_LDMODULEVERSIONFLAGS'] = '$_APPLELINK_CURRENT_VERSION $_APPLELINK_COMPATIBILITY_VERSION '

    # override the default for loadable modules, which are different
    # on OS X than dynamic shared libs.  echoing what XCode does for
    # pre/suffixes:
    env['LDMODULEPREFIX'] = ''
    env['LDMODULESUFFIX'] = ''
    env['LDMODULEFLAGS'] = SCons.Util.CLVar('$LINKFLAGS -bundle')
    env['LDMODULECOM'] = '$LDMODULE -o ${TARGET} $LDMODULEFLAGS $SOURCES $_LIBDIRFLAGS $_LIBFLAGS $_FRAMEWORKPATH $_FRAMEWORKS $FRAMEWORKSFLAGS'

    env['__SHLIBVERSIONFLAGS'] = '${__libversionflags(__env__,"SHLIBVERSION","_SHLIBVERSIONFLAGS")}'



def exists(env):
    return True