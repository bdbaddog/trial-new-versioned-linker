import mylinker
from SCons.Util import CLVar


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


def exists(env):
    return True
