# -*- python -*-
from lsst.sconsUtils import scripts

# Build the DATA directory prior to the default targets.
targetList = ('version', 'shebang', 'DATA',) + scripts.DEFAULT_TARGETS

scripts.BasicSConstruct("ci_cpp_gen2", disableCc=True,
                        defaultTargets=targetList)
