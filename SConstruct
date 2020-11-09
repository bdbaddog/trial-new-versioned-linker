env = Environment(tools=['mylinker', 'g++', 'gcc'], LIBNAME='MY_SHLIB_NAME')

# Syntax to bake soname into shared library for gnu linkers
# -Wl,-soname,your_soname

# For apple link we have to command lines
# "-Wl,-current_version,%s"
# and
# "-Wl,-compatibility_version,%s"


to_subst = ['SHLIBNAME', 'SHLIB_SYMLINK1', 'SHLIB_SYMLINK2','LDMODULENAME']


def eval_shlib_filenames(env):
    "Dump out the vales"
    for s in to_subst:
        print("%20s -> %s" % (s, env.subst("$%s" % s)))


env1 = env.Clone(SHLIBVERSION='1.2.3')
env2 = env.Clone(SHLIBVERSION='1.2.3', SOVERSION='4')

print("======ENV==========")
eval_shlib_filenames(env)
print("======ENV1==========")
eval_shlib_filenames(env1)
print("======ENV2==========")
eval_shlib_filenames(env2)

# import pdb; pdb.set_trace()

# TODO
# 1. Only create shlibversion symlink file names and store if there is a shlink version
# 2. Handle validating version numbers and throw proper exception
# 3. Handle converting soname -> soversion if needed.?


env.SharedLibrary('a', 'a.c', SHLIBVERSION='1.2.3')
# env.SharedLibrary('a_soversion', 'a.c', SHLIBVERSION='1.2.3', SOVERSION='3')
# env.SharedLibrary('a_soname', 'a.c', SHLIBVERSION='1.2.3', SONAME='liba_soname.9.so')
# env.SharedLibrary('a_nosymlink', 'a.c', SHLIBVERSION='1.2.3', SHLIBNOVERSIONSYMLINKS=True)
#
# env.SharedLibrary('b', 'b.c')

env.LoadableModule('loadable_a', 'a.c', LDMODULEVERSION='1.2.3')


# env.Command('libabc.so', 'a.c', '@echo for TARGET:$TARGET SHLIBVERSION=$SHLIBVERSION SONAME=${SONAME}',
#             # SOVERSION='1'
#             SHLIBVERSION='1.2.3'
#             )
#
# env.Command('libabc.so', 'a.c',
#             ['echo ln -s $TARGET $SHLIB_BASENAME',
#              'echo ln -s $TARGET $SHLIB_SONAME'],
#             SHLIBVERSION='1.2.3')
