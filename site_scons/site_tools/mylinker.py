"""
All library versioning is keyed off of $SHLIBVERSION being set
So if SONAME, SOVERSION, etc are set but SHLIBVERSION is not, they will be ignored.
"""

import SCons.Action
from SCons.Tool.linkCommon import CreateLibSymlinks, EmitLibSymlinks, StringizeLibSymlinks
from SCons.Tool import ProgramScanner



def LibSymlinksActionFunction(target, source, env):
    for tgt in target:
        symlinks = getattr(getattr(tgt, 'attributes', None), 'shliblinks', None)
        if symlinks:
            CreateLibSymlinks(env, symlinks)
    return 0


def LibSymlinksStrFun(target, source, env, *args):
    cmd = None
    for tgt in target:
        symlinks = getattr(getattr(tgt, 'attributes', None), 'shliblinks', None)
        if symlinks:
            if cmd is None: cmd = ""
            if cmd: cmd += "\n"
            cmd += "Create symlinks for: %r" % tgt.get_path()
            try:
                linkstr = ', '.join(["%r->%r" % (k, v) for k, v in StringizeLibSymlinks(symlinks)])
            except (KeyError, ValueError):
                pass
            else:
                cmd += ": %s" % linkstr
    return cmd


ShLinkAction = SCons.Action.Action("$SHLINKCOM", "$SHLINKCOMSTR")
LibSymlinksAction = SCons.Action.Action(LibSymlinksActionFunction, LibSymlinksStrFun)


def lib_emitter(target, source, env, **kw):
    Verbose = True
    if Verbose:
        print("_lib_emitter: target[0]={!r}".format(target[0].get_path()))
    for tgt in target:
        if SCons.Util.is_String(tgt):
            tgt = env.File(tgt)
        tgt.attributes.shared = 1

    return target, source


def shlib_symlink_emitter(target, source, env, **kw):
    Verbose = True

    shlibversion = env.subst('$SHLIBVERSION')
    if shlibversion:
        if Verbose:
            print("shlib_symlink_emitter: SHLIBVERSION=%s"%shlibversion)

        libnode = target[0]
        shlib_soname_symlink = env.subst('$SHLIB_SONAME_SYMLINK', target=target, source=source)
        shlib_noversion_symlink = env.subst('$SHLIB_NOVERSION_SYMLINK', target=target, source=source)

        symlinks = [(env.File(shlib_soname_symlink), libnode),
                    (env.File(shlib_noversion_symlink), libnode)]

        if Verbose:
            print("_lib_emitter: symlinks={!r}".format(', '.join(["%r->%r" % (k, v) for k, v in StringizeLibSymlinks(symlinks)])
))

        if symlinks:
            # This does the actual symlinking
            EmitLibSymlinks(env, symlinks, target[0])

            # This saves the information so if the versioned shared library is installed
            # it can faithfully reproduce the correct symlinks
            target[0].attributes.shliblinks = symlinks

    return target, source


def createSharedLibBuilder(env):
    """This is a utility function that creates the SharedLibrary
    Builder in an Environment if it is not there already.

    If it is already there, we return the existing one.
    """

    try:
        shared_lib = env['BUILDERS']['SharedLibrary']
    except KeyError:
        import SCons.Defaults
        action_list = [ShLinkAction,
                       LibSymlinksAction]
        shared_lib = SCons.Builder.Builder(action=action_list,
                                           emitter="$SHLIBEMITTER",
                                           prefix='lib',
                                           suffix='$_SHLIBUFFIX',
                                           target_scanner=ProgramScanner,
                                           src_suffix='$_SHOBJSUFFIX',
                                           # src_builder='SharedObject'
                                           )
        env['BUILDERS']['SharedLibrary'] = shared_lib

    return shared_lib


def _soversion(target, source, env, for_signature):
    "Function to determine what to use for SOVERSION"

    if 'SOVERSION' in env:
        return '.$SOVERSION'
    elif 'SHLIBVERSION' in env:
        shlibversion = env.subst('$SHLIBVERSION')
        # We use only the most significant digit of SHLIBVERSION
        return '.' + shlibversion.split('.')[0]
    else:
        return ''


def _get_shlib_stem(target, source, env, for_signature):
    """
    Get the basename for a library (so for libxyz.so, return xyz)
    :param target:
    :param source:
    :param env:
    :param for_signature:
    :return:
    """
    target_name = str(target)
    shlibprefix = env.subst('$SHLIBPREFIX')
    shlibsuffix = env.subst("$_SHLIBUFFIX")

    if target_name.startswith(shlibprefix):
        target_name = target_name[len(shlibprefix):]

    if target_name.endswith(shlibsuffix):
        target_name = target_name[:-len(shlibsuffix)]

    return target_name


def generate(env):
    createSharedLibBuilder(env)

    env['_get_shlib_stem'] = _get_shlib_stem
    env['_SOVERSION'] = _soversion

    env['SHLIBNAME'] = '${SHLIBPREFIX}$_get_shlib_stem${_SHLIBVERSION}${_SHLIBUFFIX}'

    # This is the non versioned shlib filename
    # If SHLIBVERSION is defined then this will symlink to $SHLIBNAME
    env['SHLIB_NOVERSION_SYMLINK'] = '${SHLIBPREFIX}$_get_shlib_stem${SHLIBSUFFIX}'

    # This is the sonamed file name
    # If SHLIBVERSION is defined then this will symlink to $SHLIBNAME
    env['SHLIB_SONAME_SYMLINK'] = '${SHLIBPREFIX}$_get_shlib_stem${_SOVERSION}${SHLIBSUFFIX}'

    # Note this is gnu style
    env['SHLIBSONAMEFLAGS'] = '-Wl,-soname=$SHLIB_SONAME_SYMLINK'

    env['_SHLIBVERSION'] = "${SHLIBVERSION and '.'+SHLIBVERSION or ''}"

    env['SHLIBEMITTER'] = [lib_emitter, shlib_symlink_emitter]

    env['SHLIBPREFIX'] = 'lib'
    env['_SHLIBUFFIX'] = '${_SHLIBVERSION}${SHLIBSUFFIX}'
    env['SHLIBSUFFIX'] = '.so'

    env['SHLINKCOM'] = 'touch $TARGET'
    env['SHLINKCOMSTR'] = 'touch $TARGET'


def exists(env):
    return True
