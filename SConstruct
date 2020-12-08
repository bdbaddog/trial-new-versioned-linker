env = Environment(tools=['mylinker', 'g++', 'gcc'], LIBNAME='MY_SHLIB_NAME')
apple_env = Environment(tools=['myapplelink', 'g++', 'gcc'], LIBNAME='MY_SHLIB_NAME')
apple_env['APPLE_TESTS'] = True

cyg_env = Environment(tools=['mycyglink', 'g++', 'gcc'], LIBNAME='MY_SHLIB_NAME')
cyg_env['CYGWIN_TESTS'] = True


# Syntax to bake soname into shared library for gnu linkers
# -Wl,-soname,your_soname

# For apple link we have to command lines
# "-Wl,-current_version,%s"
# and
# "-Wl,-compatibility_version,%s"


# TODO
# 1. Only create shlibversion symlink file names and store if there is a shlink version
# 2. Handle validating version numbers and throw proper exception
# 3. Handle converting soname -> soversion if needed.?

SConscript('src/SConscript', exports={'env': env}, variant_dir='build/vanilla')
SConscript('src/SConscript', exports={'env': apple_env}, variant_dir='build/apple')
SConscript('src/SConscript', exports={'env': cyg_env}, variant_dir='build/cygwin')
