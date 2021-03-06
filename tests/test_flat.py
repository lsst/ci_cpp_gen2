# This file is part of ci_cpp_gen2.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import os
import numpy as np
import unittest

import lsst.afw.math as afwMath
import lsst.daf.persistence as dafPersist
import lsst.ip.isr as ipIsr
import lsst.utils.tests
from lsst.utils import getPackageDir


# TODO: DM-26396
#       Update these tests to validate calibration construction.
class FlatTestCases(lsst.utils.tests.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup butler and generate an ISR processed exposure.

        As no flat tests are described in DMTN-101, use similar tests
        to those defined for darks.

        Notes
        -----
        DMTN-101 10.X:

        Process an independent flat frame through the ISR including
        overscan correction, bias subtraction, dark subtraction, flat
        correction

        """
        repoDir = os.path.join(getPackageDir('ci_cpp_gen2'), "DATA")
        calibDir = os.path.join(repoDir, "calibs")
        butler = dafPersist.Butler(repoDir, calibRoot=calibDir)

        config = ipIsr.IsrTaskConfig()
        config.doSaturation = True
        config.doSuspect = True
        config.doSetBadRegions = True
        config.doOverscan = True
        config.doBias = True
        config.doVariance = True
        config.doDark = True
        config.doFlat = True
        config.doDefect = True

        config.doLinearize = False
        config.doCrosstalk = False
        config.doWidenSaturationTrails = False
        config.doBrighterFatter = False
        config.doSaturationInterpolation = False
        config.doStrayLight = False
        config.doApplyGains = False
        config.doFringe = False
        config.doMeasureBackground = False
        config.doVignette = False
        config.doAttachTransmissionCurve = False
        config.doUseOpticsTransmission = False
        config.doUseFilterTransmission = False
        config.doUseSensorTransmission = False
        config.doUseAtmosphereTransmission = False

        isrTask = ipIsr.IsrTask(config=config)
        # TODO: DM-26396
        # This is not an independent frame.
        dataRef = butler.dataRef('raw', dataId={'detector': 0, 'expId': 2020012800028})
        results = isrTask.runDataRef(dataRef)
        cls.exposure = results.outputExposure
        del butler

    def test_independentFrameLevel(self):
        """Test image mean and sigma are plausible.

        Notes
        -----
        DMTN-101 10.X:
        """
        mean = afwMath.makeStatistics(self.exposure.getImage(), afwMath.MEAN).getValue()
        sigma = afwMath.makeStatistics(self.exposure.getImage(), afwMath.STDEV).getValue()
        expectMean = 8750
        expectSigmaMax = 3000
        self.assertLess(np.abs(mean - expectMean), sigma,
                        msg=f"Test 10.X: {mean} {expectMean} {sigma}")
        self.assertLess(sigma, expectSigmaMax,
                        msg=f"Test 10.X2: {sigma} {expectSigmaMax}")


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
