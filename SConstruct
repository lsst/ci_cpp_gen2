# -*- python -*-
import os
import yaml

from SCons.Script import SConscript, Environment, GetOption, Default
from lsst.sconsUtils.utils import libraryLoaderEnvironment
SConscript(os.path.join(".", "bin.src", "SConscript"))

env = Environment(ENV=os.environ)
env["ENV"]["OMP_NUM_THREADS"] = "1"  # Disable threading; we're parallelising at a higher level

TESTDATA_ROOT = env.ProductDir("testdata_latiss_cpp")
PKG_ROOT = env.ProductDir("ci_cpp_gen2")
REPO_ROOT = os.path.join(PKG_ROOT, "DATA")
CALIB_ROOT = os.path.join(REPO_ROOT, "calibs")
num_process = GetOption('num_jobs')
expVisitKey = 'expId'

# Load exposure lists from testsdata repo, to ensure consistency.
with open(os.path.join(TESTDATA_ROOT, "raw", "manifest.yaml")) as f:
    exposureDict = yaml.safe_load(f)


# Copied from ci_hsc_gen3:
def getExecutableCmd(package, script, *args, directory=None):
    """
    Given the name of a package and a script or other executable which lies
    within the given subdirectory (defaults to "bin"), return an appropriate
    string which can be used to set up an appropriate environment and execute
    the command.
    This includes:
    * Specifying an explict list of paths to be searched by the dynamic linker;
    * Specifying a Python executable to be run (we assume the one on the
      default ${PATH} is appropriate);
    * Specifying the complete path to the script.
    """
    if directory is None:
        directory = "bin"
    cmds = [libraryLoaderEnvironment(), "python", os.path.join(env.ProductDir(package), directory, script)]
    cmds.extend(args)
    return " ".join(cmds)


def runConstructCalib(typeString, priorStage, visitList,
                      sourcePackage='pipe_drivers', sourceScript='CONSTRUCT_CALIBS'):
    if sourceScript == 'CONSTRUCT_CALIBS':
        sourceScript = "construct{}.py".format(typeString.capitalize())
    if sourcePackage == 'pipe_drivers':
        batchOpts = '--batch-type none'
    else:
        batchOpts = ''
    run = env.Command(os.path.join(REPO_ROOT, "{}Gen".format(typeString)), priorStage,
                      [getExecutableCmd(sourcePackage, sourceScript,
                                        REPO_ROOT,
                                        "--calib", "{}".format(CALIB_ROOT),
                                        "--rerun", "{}/{}Gen/".format(REPO_ROOT, typeString),
                                        '--longlog', "-j {}".format(num_process),
                                        batchOpts,
                                        '--id detector=0',
                                        "{}={}".format(expVisitKey, '^'.join(str(visit)
                                                                             for visit in visitList)),
                                        "-C {}/config/constructCalib.py".format(PKG_ROOT)
                                        )])
    env.Alias("{}Gen".format(typeString), run)

    ingest = env.Command(os.path.join(CALIB_ROOT, typeString), "{}Gen".format(typeString),
                         [getExecutableCmd('pipe_tasks', 'ingestCalibs.py',
                                           REPO_ROOT,
                                           "{}/{}Gen/{}/2020-01-28/*.fits".format(REPO_ROOT,
                                                                                  typeString, typeString),
                                           "{}/{}Gen/{}/2020-01-28/*/*.fits".format(REPO_ROOT,
                                                                                    typeString, typeString),
                                           "{}/{}Gen/{}/*/2020-01-28/*.fits".format(REPO_ROOT,
                                                                                    typeString, typeString),
                                           '--validity 9999',
                                           '--calib {}'.format(CALIB_ROOT),
                                           '--mode=link')])
    env.Alias(typeString, ingest)

    return(run, ingest)


# Create butler
butler = env.Command(os.path.join(REPO_ROOT, "_mapper"), "bin",
                     ["echo 'lsst.obs.lsst.latiss.LatissMapper' > {}/_mapper".format(REPO_ROOT)])
env.Alias("butler", butler)

# Ingest raws:
# TODO: DM-25903 The sqlite3 command is needed until the detectorName
# is in defect generation.
raws = env.Command(os.path.join(REPO_ROOT, 'raw'), butler,
                   [getExecutableCmd("pipe_tasks", 'ingestImages.py',
                                     REPO_ROOT, "{}/raw/2020-01-28/*.fits".format(TESTDATA_ROOT)),
                    f"sqlite3 {os.path.join(REPO_ROOT, 'registry.sqlite3')} "
                    f" \"UPDATE raw SET detectorName = 'RXX_S00' WHERE detectorName = 'S00';\""])

env.Alias("raws", raws)

# Latiss curated calibs:
latissSourceDir = env.ProductDir('obs_lsst_data')
calibs = env.Command(os.path.join(CALIB_ROOT, 'calibRegistry.sqlite3'), raws,
                     [f"echo 'lsst.obs.lsst.latiss.LatissMapper' > {CALIB_ROOT}/_mapper",
                      getExecutableCmd("pipe_tasks", "ingestCuratedCalibs.py",
                                       CALIB_ROOT,
                                       f"{latissSourceDir}/latiss/defects",
                                       "--calib", CALIB_ROOT,
                                       "--config clobber=True")])

env.Alias("calibs", calibs)

# Bias
biasGen, bias = runConstructCalib('bias', 'calibs', exposureDict['biasExposures'])

# Dark
darkGen, dark = runConstructCalib('dark', 'bias', exposureDict['darkExposures'])

# Flat
flatGen, flat = runConstructCalib('flat', 'dark', exposureDict['flatExposures'])

# Science: Only depend on the flat to be finished.
#          This also uses visits due to gen2.
sciExposure = "^".join([str(vv) for vv in exposureDict['scienceVisits']])
science = env.Command(os.path.join(REPO_ROOT, 'sciTest'), flat,
                      [getExecutableCmd('ip_isr', 'runIsr.py',
                                        REPO_ROOT,
                                        "--calib {}".format(CALIB_ROOT),
                                        "--rerun", "{}/sciTest".format(REPO_ROOT),
                                        "--id detector=0 visit={}".format(sciExposure))])

env.Alias("science", science)

# Crosstalk: Use the science exposures.
cpPipeSourceDir = env.ProductDir('cp_pipe')
crosstalkIsr = env.Command(os.path.join(REPO_ROOT, 'crosstalkIsr'), flat,
                           [getExecutableCmd('ip_isr', 'runIsr.py',
                                             REPO_ROOT, f"--calib {CALIB_ROOT}",
                                             "--rerun", f"{REPO_ROOT}/crosstalkIsr",
                                             "--id detector=0",
                                             "visit={}".format(sciExposure),
                                             f"-C {cpPipeSourceDir}/config/crosstalkIsr.py",
                                             "-c isr.doLinearize=False")])
env.Alias("crosstalkIsr", crosstalkIsr)

crosstalkGen = env.Command(os.path.join(REPO_ROOT, "crosstalkGen"), crosstalkIsr,
                           [getExecutableCmd('cp_pipe', "measureCrosstalk.py",
                                             f"{REPO_ROOT}/crosstalkIsr",
                                             "--rerun", f"{REPO_ROOT}/crosstalkGen",
                                             "--id detector=0",
                                             "visit={}".format(sciExposure))])
env.Alias("crosstalk", crosstalkGen)

# Defects
defectExposure = "^".join([str(vv) for vv in
                           exposureDict['flatExposures'] + exposureDict['darkExposures']])
defectsGen = env.Command(os.path.join(REPO_ROOT, 'defectGen'), flat,
                         [getExecutableCmd('cp_pipe', 'findDefects.py',
                                           REPO_ROOT,
                                           f"--calib {CALIB_ROOT}",
                                           "--rerun", f"{REPO_ROOT}/defectGen",
                                           "--id detector=0",
                                           "--visitList {}".format(defectExposure),
                                           "-c assertSameRun=False",  # This is wrong in obs_lsst/config/
                                           "-c isrForDarks.doFlat=False",
                                           "-c isrForFlats.doFlat=False",
                                           "-c writeAs=BOTH")])
env.Alias('defectsGen', defectsGen)

# PTC
ptcExposurePairs = " ".join([str(vv) for vv in exposureDict['ptcExposurePairs']])
ptcIsrExposures = ptcExposurePairs.replace(" ", "^").replace(",", "^")
obsLsstDir = env.ProductDir('obs_lsst')
ptcGenIsr = env.Command(os.path.join(REPO_ROOT, 'ptcGenIsr'), flat,
                        [getExecutableCmd('ip_isr', 'runIsr.py',
                                          REPO_ROOT, f"--calib {CALIB_ROOT}",
                                          "--rerun", f"{REPO_ROOT}/ptcGenIsr",
                                          "--id detector=0",
                                          "expId={}".format(ptcIsrExposures),
                                          f"-C {obsLsstDir}/config/latiss/ptcIsr.py",
                                          '-j', str(num_process))])
env.Alias('ptcIsr', ptcGenIsr)

ptcGen = env.Command(os.path.join(REPO_ROOT, 'ptcGen'), ptcGenIsr,
                     [getExecutableCmd('cp_pipe', 'measurePhotonTransferCurve.py',
                                       f"{REPO_ROOT}/ptcGenIsr",
                                       "--rerun", f"{REPO_ROOT}/ptcGen",
                                       "--id detector=0",
                                       "-c ptcFitType=POLYNOMIAL polynomialFitDegree=3",
                                       "--visit-pairs {}".format(ptcExposurePairs),
                                       "-j", str(num_process))])
env.Alias('ptcGen', ptcGen)

# Brighter-Fatter Kernel.
#    This still does ISR processing, so clip exposure list to speed processing.
bfkExposurePairs = " ".join([str(vv) for vv in exposureDict['ptcExposurePairs'][::2]])
bfkGen = env.Command(os.path.join(REPO_ROOT, 'bfkGen'), flat,
                     [getExecutableCmd('cp_pipe', 'makeBrighterFatterKernel.py',
                                       REPO_ROOT,
                                       "--calib {CALIB_ROOT}",
                                       "--rerun", f"{REPO_ROOT}/bfkGen",
                                       "--id detector=0",
                                       "--visit-pairs {}".format(bfkExposurePairs),
                                       "-j", str(num_process))])
env.Alias('bfkGen', bfkGen)

# Tests and bookkeeping.
everything = [butler, calibs]
everything.extend([bias, dark, flat])
everything.extend([bfkGen, ptcGen, defectsGen, crosstalkGen, science])

tests = [env.Command(f"test_{name}", ['DATA/flatGen'],
                     getExecutableCmd('ci_cpp_gen2', f"test_{name}.py", directory="tests"))
         for name in ('flat', 'bias', 'dark', 'ptc', 'defects', 'crosstalk', 'brighterFatter', 'linearity')]
env.Alias("tests", tests)
everything.extend([tests])

env.Alias("install", "SConstruct")

env.Alias("all", everything)
Default(everything)

env.Clean(everything, [y for x in everything for y in x] + ['DATA'])
