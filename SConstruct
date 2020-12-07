env = Environment(tools=['mylinker', 'g++', 'gcc'], LIBNAME='MY_SHLIB_NAME')

# Syntax to bake soname into shared library for gnu linkers
# -Wl,-soname,your_soname

# For apple link we have to command lines
# "-Wl,-current_version,%s"
# and
# "-Wl,-compatibility_version,%s"

# def dump_my_values(env,)
# to_subst = ['SHLIBNAME', 'SHLIB_SYMLINK1', 'SHLIB_SYMLINK2', '_get_shlib_stem','LDMODULENAME']
#
#
# def eval_shlib_filenames(env):
#     "Dump out the vales"
#     for s in to_subst:
#         print("%20s -> %s" % (s, env.subst("$%s" % s)))
#
#
# env1 = env.Clone(SHLIBVERSION='1.2.3')
# env2 = env.Clone(SHLIBVERSION='1.2.3', SOVERSION='4')
#
# print("======ENV==========")
# eval_shlib_filenames(env)
# print("======ENV1==========")
# eval_shlib_filenames(env1)
# print("======ENV2==========")
# eval_shlib_filenames(env2)

# import pdb; pdb.set_trace()

# TODO
# 1. Only create shlibversion symlink file names and store if there is a shlink version
# 2. Handle validating version numbers and throw proper exception
# 3. Handle converting soname -> soversion if needed.?


shared_obj = env.SharedObject('a.c')
env.SharedLibrary('a', shared_obj, SHLIBVERSION='1.2.3')
env.SharedLibrary('a_soversion', shared_obj, SHLIBVERSION='1.2.3', SOVERSION='3')
env.SharedLibrary('a_soname', shared_obj, SHLIBVERSION='1.2.3', SONAME='liba_soname.9.so')
env.SharedLibrary('a_nosymlink', shared_obj, SHLIBVERSION='1.2.3', SHLIBNOVERSIONSYMLINKS=True)

env.SharedLibrary('b', 'b.c')

env.LoadableModule('loadable_a', shared_obj, LDMODULEVERSION='1.2.3')
env.LoadableModule('loadable_a_soversion', shared_obj, LDMODULEVERSION='1.2.3', SOVERSION='4')
env.LoadableModule('loadable_a_soname', shared_obj, LDMODULEVERSION='1.2.3', SONAME='libloadable_a_soname.99.so')
env.LoadableModule('loadable_a_nosymlink', shared_obj, LDMODULEVERSION='3.4.5', LDMODULENOVERSIONSYMLINKS=True)



# env.Command('libabc.so', shared_obj, '@echo for TARGET:$TARGET SHLIBVERSION=$SHLIBVERSION SONAME=${SONAME}',
#             # SOVERSION='1'
#             SHLIBVERSION='1.2.3'
#             )
#
# env.Command('libabc.so', shared_obj,
#             ['echo ln -s $TARGET $SHLIB_BASENAME',
#              'echo ln -s $TARGET $SHLIB_SONAME'],
#             SHLIBVERSION='1.2.3')
