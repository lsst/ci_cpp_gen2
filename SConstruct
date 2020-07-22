# -*- python -*-
import os
from SCons.Script import SConscript, Environment, GetOption, Default
from lsst.sconsUtils.utils import libraryLoaderEnvironment
SConscript(os.path.join(".", "bin.src", "SConscript"))

env = Environment(ENV=os.environ)
env["ENV"]["OMP_NUM_THREADS"] = "1"  # Disable threading; we're parallelising at a higher level

TESTDATA_ROOT = env.ProductDir("testdata_latiss_cpp")
PKG_ROOT = env.ProductDir("ci_cpp_gen2")
print(PKG_ROOT)
REPO_ROOT = os.path.join(PKG_ROOT, "DATA")
CALIB_ROOT = os.path.join(REPO_ROOT, "calibs")
num_process = GetOption('num_jobs')
expVisitKey = 'expId'

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
# The sqlite3 command is needed until the detectorName is in defect generation: DM-25903
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
# biasVisits = [6877619261923411114, 5822802147131397314, 1456513991713053314, 2598332774380057514]
biasExposures = [2020012800007, 2020012800008, 2020012800009, 2020012800010]
biasGen, bias = runConstructCalib('bias', 'calibs', biasExposures)

# Dark
# Actually exposures
darkExposures = [2020012800014, 2020012800015, 2020012800016, 2020012800019, 2020012800020,
                 2020012800021, 2020012800024, 2020012800025, 2020012800026]
darkGen, dark = runConstructCalib('dark', 'bias', darkExposures)


# Flat
flatExposures = [2020012800028, 2020012800029, 2020012800030, 2020012800031,
                 2020012800032, 2020012800033, 2020012800034, 2020012800035,
                 2020012800036, 2020012800037, 2020012800038, 2020012800039,
                 2020012800040, 2020012800041, 2020012800042, 2020012800043,
                 2020012800044, 2020012800045, 2020012800046, 2020012800047,
                 2020012800048, 2020012800049, 2020012800050, 2020012800051,
                 2020012800052, 2020012800053, 2020012800054, 2020012800055,
                 2020012800056, 2020012800057, 2020012800058, 2020012800059,
                 2020012800060, 2020012800061, 2020012800062, 2020012800063,
                 2020012800064, 2020012800065, 2020012800066, 2020012800067,
                 2020012800068, 2020012800069, 2020012800070, 2020012800071,
                 2020012800072, 2020012800073, 2020012800074, 2020012800075,
                 2020012800076, 2020012800077, 2020012800078, 2020012800079,
                 2020012800080, 2020012800081, 2020012800082, 2020012800083,
                 2020012800084, 2020012800085, 2020012800086, 2020012800087,
                 2020012800088, 2020012800089, 2020012800090, 2020012800091,
                 2020012800092, 2020012800093, 2020012800094, 2020012800095,
                 2020012800096, 2020012800097, 2020012800098, 2020012800099,
                 2020012800100, 2020012800101, 2020012800102, 2020012800103,
                 2020012800104, 2020012800105, 2020012800106, 2020012800107,
                 2020012800108]

flatExposures = [2020012800028, 2020012800032, 2020012800036, 2020012800040,
                 2020012800044, 2020012800048, 2020012800052, 2020012800056,
                 2020012800060, 2020012800064, 2020012800068, 2020012800072,
                 2020012800076, 2020012800080, 2020012800084, ] 

flatGen, flat = runConstructCalib('flat', 'dark', flatExposures)


# Science
scienceExposures = [1601960058820000, 1601964522480000, 1601964937800000, 1601968088430000]
science = env.Command(os.path.join(REPO_ROOT, 'sciTest'), flat,
                      [getExecutableCmd('ip_isr', 'runIsr.py',
                                        REPO_ROOT,
                                        "--calib {}".format(CALIB_ROOT),
                                        "--rerun", "{}/sciTest".format(REPO_ROOT),
                                        "--id detector=0 visit={}".format(str(scienceExposures[0])),
                      )])
env.Alias("science", science)

cpPipeSourceDir = env.ProductDir('cp_pipe')
crosstalkIsr = env.Command(os.path.join(REPO_ROOT, 'crosstalkIsr'), flat,
                        [getExecutableCmd('ip_isr', 'runIsr.py',
                                          REPO_ROOT, f"--calib {CALIB_ROOT}",
                                          "--rerun", f"{REPO_ROOT}/crosstalkIsr",
                                          "--id detector=0",
                                          "visit={}".format("^".join(str(exp) for exp in scienceExposures)),
                                          f"-C {cpPipeSourceDir}/config/crosstalkIsr.py",
                                          "-c isr.doLinearize=False")])
env.Alias("crosstalkIsr", crosstalkIsr)
crosstalkGen = env.Command(os.path.join(REPO_ROOT, "crosstalkGen"), crosstalkIsr,
                           [getExecutableCmd('cp_pipe', "measureCrosstalk.py",
                                             f"{REPO_ROOT}/crosstalkIsr",
                                             "--rerun", f"{REPO_ROOT}/crosstalkGen",
                                             "--id detector=0",
                                             "visit={}".format("^".join(str(exp) for exp in scienceExposures)))])
env.Alias("crosstalk", crosstalkGen)

# This might fail due to bad inputs?  footprint/thresholding needs to try/except for bad sigma values (or something)
defectsGen = env.Command(os.path.join(REPO_ROOT, 'defectGen'), flat,
                         [getExecutableCmd('cp_pipe', 'findDefects.py',
                                           REPO_ROOT,
                                           f"--calib {CALIB_ROOT}",
                                           "--rerun", f"{REPO_ROOT}/defectGen",
                                           "--id detector=0",
                                           "--visitList {}".format('^'.join(str(visit) for visit in flatExposures + darkExposures)),
                                           "-c assertSameRun=False",  # This is wrong in obs_lsst/config/
                                           "-c isrForDarks.doFlat=False",
                                           "-c isrForFlats.doFlat=False",
                                           "-c writeAs=BOTH",
                         )])
env.Alias('defectsGen', defectsGen)

obsLsstDir = env.ProductDir('obs_lsst')
ptcGenIsr = env.Command(os.path.join(REPO_ROOT, 'ptcGenIsr'), flat,
                        [getExecutableCmd('ip_isr', 'runIsr.py',
                                          REPO_ROOT, f"--calib {CALIB_ROOT}",
                                          "--rerun", f"{REPO_ROOT}/ptcGenIsr",
                                          "--id detector=0",
                                          "expId=2020012800028^2020012800029^2020012800030^2020012800031^"
                                          "2020012800032^2020012800033^2020012800034^2020012800035^2020012800036^2020012800037^"
                                          "2020012800038^2020012800039^2020012800040^2020012800041^2020012800042^2020012800043^"
                                          "2020012800044^2020012800045^2020012800046^2020012800047^2020012800048^2020012800049^"
                                          "2020012800050^2020012800051^2020012800052^2020012800053^2020012800054^2020012800055^"
                                          "2020012800056^2020012800057^2020012800058^2020012800059^2020012800060^2020012800061^"
                                          "2020012800062^2020012800063^2020012800064^2020012800065^2020012800066^2020012800067^"
                                          "2020012800068^2020012800069^2020012800070^2020012800071^2020012800072^2020012800073^"
                                          "2020012800074^2020012800075^2020012800076^2020012800077^2020012800078^2020012800079^"
                                          "2020012800080^2020012800081^2020012800082^2020012800083^2020012800084^2020012800085^"
                                          "2020012800086^2020012800087^2020012800088^2020012800089^2020012800090^2020012800091^"
                                          "2020012800092^2020012800093^2020012800094^2020012800095^2020012800096^2020012800097^"
                                          "2020012800098^2020012800099^2020012800100^2020012800101^2020012800102^2020012800103^"
                                          "2020012800104^2020012800105^2020012800106^2020012800107",
                                          f"-C {obsLsstDir}/config/latiss/ptcIsr.py", '-j', str(num_process),
                                      )])
ptcGen = env.Command(os.path.join(REPO_ROOT, 'ptcGen'), ptcGenIsr,
                     [getExecutableCmd('cp_pipe', 'measurePhotonTransferCurve.py',
                                       f"{REPO_ROOT}/ptcGenIsr",
                                       "--rerun", f"{REPO_ROOT}/ptcGen",
                                       "--id detector=0",
                                       "-c ptcFitType=POLYNOMIAL polynomialFitDegree=3",
                                       "--visit-pairs 2020012800028,2020012800029 2020012800030,2020012800031",
                                       "2020012800032,2020012800033 2020012800034,2020012800035 2020012800036,2020012800037",
                                       "2020012800038,2020012800039 2020012800040,2020012800041 2020012800042,2020012800043",
                                       "2020012800044,2020012800045 2020012800046,2020012800047 2020012800048,2020012800049",
                                       "2020012800050,2020012800051 2020012800052,2020012800053 2020012800054,2020012800055",
                                       "2020012800056,2020012800057 2020012800058,2020012800059 2020012800060,2020012800061",
                                       "2020012800062,2020012800063 2020012800064,2020012800065 2020012800066,2020012800067",
                                       "2020012800068,2020012800069 2020012800070,2020012800071 2020012800072,2020012800073",
                                       "2020012800074,2020012800075 2020012800076,2020012800077 2020012800078,2020012800079",
                                       "2020012800080,2020012800081 2020012800082,2020012800083 2020012800084,2020012800085",
                                       "2020012800086,2020012800087 2020012800088,2020012800089 2020012800090,2020012800091",
                                       "2020012800092,2020012800093 2020012800094,2020012800095 2020012800096,2020012800097",
                                       "2020012800098,2020012800099 2020012800100,2020012800101 2020012800102,2020012800103",
                                       "2020012800104,2020012800105 2020012800106,2020012800107",
                                       "-j", str(num_process)
                                   )])
#  makePlots=False
env.Alias('ptcIsr', ptcGenIsr)
env.Alias('ptcGen', ptcGen)

bfkGen = env.Command(os.path.join(REPO_ROOT, 'bfkGen'), flat,
                     [getExecutableCmd('cp_pipe', 'makeBrighterFatterKernel.py',
                                       REPO_ROOT,
                                       "--calib {CALIB_ROOT}",
                                       "--rerun", f"{REPO_ROOT}/bfkGen",
                                       "--id detector=0",
                                       "--visit-pairs 2020012800028,2020012800029 2020012800030,2020012800031",
#                                       "2020012800032,2020012800033 2020012800034,2020012800035 2020012800036,2020012800037",
                                       "2020012800038,2020012800039 2020012800040,2020012800041 2020012800042,2020012800043",
#                                       "2020012800044,2020012800045 2020012800046,2020012800047 2020012800048,2020012800049",
                                       "2020012800050,2020012800051 2020012800052,2020012800053 2020012800054,2020012800055",
#                                       "2020012800056,2020012800057 2020012800058,2020012800059 2020012800060,2020012800061",
                                       "2020012800062,2020012800063 2020012800064,2020012800065 2020012800066,2020012800067",
#                                       "2020012800068,2020012800069 2020012800070,2020012800071 2020012800072,2020012800073",
                                       "2020012800074,2020012800075 2020012800076,2020012800077 2020012800078,2020012800079",
#                                       "2020012800080,2020012800081 2020012800082,2020012800083 2020012800084,2020012800085",
                                       "2020012800086,2020012800087 2020012800088,2020012800089 2020012800090,2020012800091",
#                                       "2020012800092,2020012800093 2020012800094,2020012800095 2020012800096,2020012800097",
                                       "2020012800098,2020012800099 2020012800100,2020012800101 2020012800102,2020012800103",
                                       "2020012800104,2020012800105 2020012800106,2020012800107",
                                       "-j", str(num_process)
                                       )])
env.Alias('bfkGen', bfkGen)
env.Alias('all', [bfkGen, ptcGen, defectsGen, crosstalkGen, science])
