"""
New cyglink module.

See cygwin's docs for dll
https://cygwin.com/cygwin-ug-net/dll.html
"""

import mylinker
from SCons.Util import CLVar, is_String
from SCons.Tool.linkCommon import EmitLibSymlinks, StringizeLibSymlinks


def cyglink_lib_emitter(target, source, env, **kw):
    verbose = True

    if 'variable_prefix' in kw:
        var_prefix = kw['variable_prefix']
    else:
        var_prefix = 'SHLIB'

    no_import_lib = env.get('no_import_lib', False)

    if verbose:
        print("cyglink_lib_emitter: target[0]={!r}".format(target[0].get_path()))

    if not no_import_lib:
        # Specify import lib and add to targets

        import_lib = env.subst('$%s_IMPLIBNAME'%var_prefix, target=target, source=source)
        import_lib_target = env.fs.File(import_lib)
        import_lib_target.attributes.shared = 1
        target.append(import_lib_target)

        if verbose:
            print("cyglink_lib_emitter: import_lib={}".format(import_lib))
            print("cyglink_lib_emitter: target=%s" % target)

    for tgt in target:
        if is_String(tgt):
            tgt = env.File(tgt)
        tgt.attributes.shared = 1

    return target, source


def cyglink_ldmodule_emitter(target,source,env, **kw):
    return cyglink_lib_emitter(target, source, env, variable_prefix='LDMODULE')


def cyglink_shlib_symlink_emitter(target, source, env, **kw):
    """
    On cygwin, we only create a symlink from the non-versioned implib to the versioned implib.
    We don't version the shared library itself.
    :param target:
    :param source:
    :param env:
    :param kw:
    :return:
    """
    verbose = True

    if 'variable_prefix' in kw:
        var_prefix = kw['variable_prefix']
    else:
        var_prefix = 'SHLIB'

    do_symlinks = env.subst('$%sNOVERSIONSYMLINKS' % var_prefix)
    if do_symlinks in ['1', 'True', 'true', True]:
        return target, source

    shlibversion = env.subst('$%sVERSION' % var_prefix)
    if shlibversion:
        if verbose:
            print("cyglink_shlib_symlink_emitter: %sVERSION=%s" % (var_prefix, shlibversion))

        # The implib (added by the cyglink_lib_emitter)
        imp_lib_node = target[1]
        shlib_noversion_symlink = env.subst('$%s_NOVERSION_SYMLINK' % var_prefix, target=target[0], source=source)

        if verbose:
            print("cyglink_shlib_symlink_emitter: shlib_noversion_symlink :%s" % shlib_noversion_symlink)
            print("cyglink_shlib_symlink_emitter: imp_lib_node            :%s" % imp_lib_node)

        symlinks = [(env.File(shlib_noversion_symlink), imp_lib_node)]

        if verbose:
            print("cyglink_shlib_symlink_emitter: symlinks={!r}".format(
                ', '.join(["%r->%r" % (k, v) for k, v in StringizeLibSymlinks(symlinks)])
            ))

        if symlinks:
            # This does the actual symlinking
            EmitLibSymlinks(env, symlinks, target[0])

            # This saves the information so if the versioned shared library is installed
            # it can faithfully reproduce the correct symlinks
            target[0].attributes.shliblinks = symlinks

    return target, source


def cyglink_ldmod_symlink_emitter(target, source, env, **kw):
    return cyglink_shlib_symlink_emitter(target, source, env, variable_prefix='LDMODULE')


def cyglink_shlibversion(target, source, env, for_signature):
    var_prefix = 'SHLIB'
    var = '%sVERSION'%var_prefix
    if var not in env:
        return ''

    version = env.subst("$%s"%var, target=target, source=source)
    version = version.replace('.', '-')
    return "." + version


def cyglink_ldmodule_version(target, source, env, for_signature):
    var_prefix = 'LDMODULE'
    var = '%sVERSION'%var_prefix
    if var not in env:
        return ''

    version = env.subst("$%s"%var, target=target, source=source)
    version = version.replace('.', '-')
    return "." + version


def generate(env):
    mylinker.generate(env)
    env['LINKFLAGS'] = CLVar('-Wl,-no-undefined')

    env['SHLIBPREFIX'] = 'cyg'
    env['SHLIBSUFFIX'] = '.dll'

    env['IMPLIBPREFIX'] = 'lib'
    env['IMPLIBSUFFIX'] = '.dll.a'

    # Variables used by versioned shared libraries
    # SHLIBVERSIONFLAGS and LDMODULEVERSIONFLAGS are same as in gnulink...
    env['_SHLIBVERSIONFLAGS'] = '$SHLIBVERSIONFLAGS'
    env['_LDMODULEVERSIONFLAGS'] = '$LDMODULEVERSIONFLAGS'

    # Remove variables set by default initialization which aren't needed/used by cyglink
    # these variables were set by gnulink but are not used in cyglink
    for rv in ['_SHLIBSONAME', '_LDMODULESONAME']:
        if rv in env:
            del env[rv]

    # Overwrite emitters. Cyglink does things differently when creating symlinks
    env['SHLIBEMITTER'] = [cyglink_lib_emitter, cyglink_shlib_symlink_emitter]
    env['LDMODULEEMITTER'] = [cyglink_ldmodule_emitter, cyglink_ldmod_symlink_emitter]

    # This is the non versioned shlib filename
    # If SHLIBVERSION is defined then this will symlink to $SHLIBNAME
    env['SHLIB_NOVERSION_SYMLINK'] = '${IMPLIBPREFIX}$_get_shlib_stem${IMPLIBSUFFIX}'
    env['LDMODULE_NOVERSION_SYMLINK'] = '${IMPLIBPREFIX}$_get_ldmodule_stem${IMPLIBSUFFIX}'

    env['SHLIB_IMPLIBNAME'] = '${IMPLIBPREFIX}$_get_shlib_stem${_SHLIB_IMPLIBSUFFIX}'
    env['LDMODULE_IMPLIBNAME'] = '${IMPLIBPREFIX}$_get_ldmodule_stem${_LDMODULE_IMPLIBSUFFIX}'

    env['_cyglink_shlibversion'] = cyglink_shlibversion
    env['_SHLIB_IMPLIBSUFFIX'] = '${_cyglink_shlibversion}${IMPLIBSUFFIX}'
    env['_SHLIBSUFFIX'] = '${_cyglink_shlibversion}${SHLIBSUFFIX}'

    env['_cyglink_ldmodule_version'] = cyglink_ldmodule_version

    env['_LDMODULESUFFIX'] = '${_cyglink_ldmodule_version}${LDMODULESUFFIX}'
    env['_LDMODULE_IMPLIBSUFFIX'] = '${_cyglink_ldmodule_version}${IMPLIBSUFFIX}'



def exists(env):
    return True
