import mylinker

from SCons.Util import CLVar

# User programmatically describes how SHLIBVERSION maps to values for compat/current.
_APPLELIB_MAX_VERSION_VALUES = (65535, 255, 255)


class AppleLinkInvalidCurrentVersionException(Exception):
    pass


class AppleLinkInvalidCompatibilityVersionException(Exception):
    pass


def _applelib_soname(target, source, env, for_signature):
    if 'SONAME' in env:
        return '$SONAME'
    else:
        return "$SHLIBPREFIX$_get_shlib_stem$_SHLIBSOVERSION${SHLIBSUFFIX}"


def _applelib_check_valid_version(version_string):
    """
    Check that the version # is valid.
    X[.Y[.Z]]
    where X 0-65535
    where Y either not specified or 0-255
    where Z either not specified or 0-255
    :param version_string:
    :return:
    """
    parts = version_string.split('.')
    if len(parts) > 3:
        return False, "Version string has too many periods [%s]" % version_string
    if len(parts) <= 0:
        return False, "Version string unspecified [%s]" % version_string

    for (i, p) in enumerate(parts):
        try:
            p_i = int(p)
        except ValueError:
            return False, "Version component %s (from %s) is not a number" % (p, version_string)
        if p_i < 0 or p_i > _APPLELIB_MAX_VERSION_VALUES[i]:
            return False, "Version component %s (from %s) is not valid value should be between 0 and %d" % (
                p, version_string, _APPLELIB_MAX_VERSION_VALUES[i])

    return True, ""


def _applelib_currentVersionFromSoVersion(source, target, env, for_signature):
    """
    A generator function to create the -Wl,-current_version flag if needed.
    If env['APPLELINK_NO_CURRENT_VERSION'] contains a true value no flag will be generated
    Otherwise if APPLELINK_CURRENT_VERSION is not specified, env['SHLIBVERSION']
    will be used.

    :param source:
    :param target:
    :param env:
    :param for_signature:
    :return: A string providing the flag to specify the current_version of the shared library
    """
    if env.get('APPLELINK_NO_CURRENT_VERSION', False):
        return ""
    elif env.get('APPLELINK_CURRENT_VERSION', False):
        version_string = env['APPLELINK_CURRENT_VERSION']
    elif env.get('SHLIBVERSION', False):
        version_string = env['SHLIBVERSION']
    else:
        return ""

    version_string = ".".join(version_string.split('.')[:3])

    valid, reason = _applelib_check_valid_version(version_string)
    if not valid:
        raise AppleLinkInvalidCurrentVersionException(reason)

    return "-Wl,-current_version,%s" % version_string


def _applelib_compatVersionFromSoVersion(source, target, env, for_signature):
    """
    A generator function to create the -Wl,-compatibility_version flag if needed.
    If env['APPLELINK_NO_COMPATIBILITY_VERSION'] contains a true value no flag will be generated
    Otherwise if APPLELINK_COMPATIBILITY_VERSION is not specified
    the first two parts of env['SHLIBVERSION'] will be used with a .0 appended.

    :param source:
    :param target:
    :param env:
    :param for_signature:
    :return: A string providing the flag to specify the compatibility_version of the shared library
    """
    if env.get('APPLELINK_NO_COMPATIBILITY_VERSION', False):
        return ""
    elif env.get('APPLELINK_COMPATIBILITY_VERSION', False):
        version_string = env['APPLELINK_COMPATIBILITY_VERSION']
    elif env.get('SHLIBVERSION', False):
        version_string = ".".join(env['SHLIBVERSION'].split('.')[:2] + ['0'])
    else:
        return ""

    if version_string is None:
        return ""

    valid, reason = _applelib_check_valid_version(version_string)
    if not valid:
        raise AppleLinkInvalidCompatibilityVersionException(reason)

    return "-Wl,-compatibility_version,%s" % version_string


def generate(env):
    mylinker.generate(env)

    env['FRAMEWORKPATHPREFIX'] = '-F'
    env['_FRAMEWORKPATH'] = '${_concat(FRAMEWORKPATHPREFIX, FRAMEWORKPATH, "", __env__, RDirs)}'

    env['_FRAMEWORKS'] = '${_concat("-framework ", FRAMEWORKS, "", __env__)}'
    env['LINKCOM'] = env['LINKCOM'] + ' $_FRAMEWORKPATH $_FRAMEWORKS $FRAMEWORKSFLAGS'
    env['SHLINKFLAGS'] = CLVar('$LINKFLAGS -dynamiclib')
    env['SHLINKCOM'] = env['SHLINKCOM'] + ' $_FRAMEWORKPATH $_FRAMEWORKS $FRAMEWORKSFLAGS'

    env['_APPLELINK_CURRENT_VERSION'] = _applelib_currentVersionFromSoVersion
    env['_APPLELINK_COMPATIBILITY_VERSION'] = _applelib_compatVersionFromSoVersion
    env['_SHLIBVERSIONFLAGS'] = '$_APPLELINK_CURRENT_VERSION $_APPLELINK_COMPATIBILITY_VERSION '
    env['_LDMODULEVERSIONFLAGS'] = '$_APPLELINK_CURRENT_VERSION $_APPLELINK_COMPATIBILITY_VERSION '

    # override the default for loadable modules, which are different
    # on OS X than dynamic shared libs.  echoing what XCode does for
    # pre/suffixes:
    env['LDMODULEPREFIX'] = ''
    env['LDMODULESUFFIX'] = ''
    env['LDMODULEFLAGS'] = CLVar('$LINKFLAGS -bundle')
    env[
        'LDMODULECOM'] = '$LDMODULE -o ${TARGET} $LDMODULEFLAGS $SOURCES $_LIBDIRFLAGS $_LIBFLAGS $_FRAMEWORKPATH $_FRAMEWORKS $FRAMEWORKSFLAGS'

    env['__SHLIBVERSIONFLAGS'] = '${__libversionflags(__env__,"SHLIBVERSION","_SHLIBVERSIONFLAGS")}'

    # New stuff
    env['_SHLIBSONAME'] = _applelib_soname

    env['_SHLIBSUFFIX'] = '${_SHLIBVERSION}${SHLIBSUFFIX}'


def exists(env):
    return True
