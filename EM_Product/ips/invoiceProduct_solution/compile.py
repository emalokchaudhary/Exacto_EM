from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import os

modules = []
for root,_,files in os.walk('.'):
    for module in files:
        if module.endswith('.py'):
            modules.append(os.path.join(root,module))


ext_modules = [
    Extension(os.path.splitext(os.path.basename(module))[0], [module]) for module in modules
]

setup(
    name = 'Exacto_Backend',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)
