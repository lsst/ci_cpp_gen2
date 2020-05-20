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
num_process = GetOption('num_jobs')

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
                                        "--calib", "{}".format(REPO_ROOT),
                                        "--rerun", "{}/{}Gen/".format(REPO_ROOT, typeString),
                                        '--longlog', "-j {}".format(num_process),
                                        batchOpts,
                                        '-c isr.doDefect=False',
                                        '--id detector=0',
                                        "expId={}".format('^'.join(str(visit) for visit in visitList))
                                        )])
    env.Alias("{}Gen".format(typeString), run)

    ingest = env.Command(os.path.join(REPO_ROOT, typeString), "{}Gen".format(typeString),
                         [getExecutableCmd('pipe_tasks', 'ingestCalibs.py',
                                           REPO_ROOT,
                                           "{}/{}Gen/{}/2020-01-28/*.fits".format(REPO_ROOT,
                                                                                  typeString, typeString),
                                           "{}/{}Gen/{}/2020-01-28/*/*.fits".format(REPO_ROOT,
                                                                                    typeString, typeString),
                                           "{}/{}Gen/{}/*/2020-01-28/*.fits".format(REPO_ROOT,
                                                                                    typeString, typeString),
                                           '--validity 9999',
                                           '--calib {}'.format(REPO_ROOT),
                                           '--mode=link')])
    env.Alias(typeString, ingest)

    return(run, ingest)

# Create butler
butler = env.Command([os.path.join(REPO_ROOT, "_mapper")], "bin",
                     ["echo 'lsst.obs.lsst.auxTel.AuxTelMapper' > {}/_mapper".format(REPO_ROOT)])
env.Alias("butler", butler)
Clean(butler, 'DATA/')
Clean(butler, 'bin/')


# Ingest raws:
raws = env.Command(os.path.join(REPO_ROOT, 'raw'), butler,
                   [getExecutableCmd("pipe_tasks", 'ingestImages.py',
                                     REPO_ROOT, "{}/raw/2020-01-28/*.fits".format(TESTDATA_ROOT),
                   )])
env.Alias("raws", raws)

# Bias
# biasVisits = [6877619261923411114, 5822802147131397314, 1456513991713053314, 2598332774380057514]
biasExposures = [2020012800007, 2020012800008, 2020012800009, 2020012800010]
biasVisits = biasExposures
biasGen, bias = runConstructCalib('bias', 'raws', biasExposures)

# Defects
# defectVisits = biasVisits
# defects, defectIng = runConstructCalib('defects', 'bias', defectVisits,
#                                       sourcePackage='cp_pipe',
#                                       sourceScript='findDefects.py')


# Dark
# Actually exposures
darkVisits = [2020012800014, 2020012800015, 2020012800016, 2020012800019, 2020012800020,
              2020012800021, 2020012800024, 2020012800025, 2020012800026]
darkGen, dark = runConstructCalib('dark', 'bias', darkVisits)

# Flat
flatVisits = [4678019585650377609, 66830773686737709, 221538474616287909, 2354553903266624309]
flatVisits = [2020012800028, 2020012800029, 2020012800030, 2020012800031,
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

flatVisits = [2020012800028, 2020012800032, 2020012800036, 2020012800040,
              2020012800044, 2020012800048, 2020012800052, 2020012800056,
              2020012800060, 2020012800064, 2020012800068, 2020012800072,
              2020012800076, 2020012800080, 2020012800084, ]  # 2020012800088,
#              2020012800092, 2020012800096, 2020012800100, 2020012800104]

flatGen, flat = runConstructCalib('flat', 'dark', flatVisits)

# This might fail due to bad inputs?  footprint/thresholding needs to try/except for bad sigma values (or something)
# defectsGen = env.Command(os.path.join(REPO_ROOT, 'defectGen'), flat,
#                          [getExecutableCmd('cp_pipe', 'findDefects.py',
#                                            REPO_ROOT,
#                                            "--calib {}".format(REPO_ROOT),
#                                            "--rerun", "{}/defectGen".format(REPO_ROOT),
#                                            "--id detector=0",
#                                            "--visitList {}".format('^'.join(str(visit) for visit in flatVisits + darkVisits)),
#                                            "-c assertSameRun=False",  # This is wrong in obs_lsst/config/
#                                            "-c isrForDarks.doFlat=False",
#                                            "-c isrForFlats.doFlat=False",
#                                            "-c writeAs=BOTH",
#                          )])
# env.Alias('defectsGen', defectsGen)
# defects = env.Command(os.path.join(REPO_ROOT, 'defects'), defectsGen,
#                       [getExecutableCmd('pipe_tasks', 'ingestCuratedCalibs.py',
#                                         REPO_ROOT,
#                                         "{}/defectGen/calibrations/defects/LATISS/defects/".format(REPO_ROOT),
#                                         "--calib {}".format(REPO_ROOT),
#                                         "--rerun", "{}/defects".format(REPO_ROOT),
#                                         )])
# env.Alias('defects', defects)



# Science
scienceVisits = [1601960058820000, 1601964522480000, 1601964937800000, 1601968088430000]

science = env.Command(os.path.join(REPO_ROOT, 'sciTest'), flat,
                      [getExecutableCmd('ip_isr', 'runIsr.py',
                                        REPO_ROOT,
                                        "--calib {}".format(REPO_ROOT),
                                        "--rerun", "{}/sciTest".format(REPO_ROOT),
                                        "--id detector=0 visit={}".format(str(scienceVisits[0])),
                                        "-c isr.doDefect=False",
                      )])



# BFK
# bfkVisits = scienceVisits
# bfk, bfkIng = runConstructCalib('bfk', 'biasIng', bfkVisits,
#                                 sourcePackage='cp_pipe',
#                                 sourceScript='makeBrighterFatterKernel.py')

# # PTC
# ptcVisits = flatVisits
# ptc, ptcIng = runConstructCalib('ptc', 'biasIng', ptcVisits,
#                                 sourcePackage='cp_pipe',
#                                 sourceScript='measurePhotonTransferCurve.py')

env.Alias('science', science)
