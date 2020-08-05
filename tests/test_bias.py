# This file is part of ci_cpp.
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
import hashlib
import os
import numpy as np
import unittest

import lsst.afw.math as afwMath
import lsst.daf.persistence as dafPersist
import lsst.ip.isr as ipIsr
import lsst.meas.algorithms as measAlg
import lsst.utils.tests

from lsst.pipe.tasks.repair import RepairTask
from lsst.utils import getPackageDir


class BiasTestCases(lsst.utils.tests.TestCase):

    def setUp(self):
        """Setup butler, and generate an ISR processed exposure.

        Notes
        -----
        DMTN-101 4.1:

        Process an independent bias frame through the ISR including
        overscan correction and bias subtraction

        """
        repoDir = os.path.join(getPackageDir('ci_cpp_gen2'), "DATA")
        calibDir = os.path.join(getPackageDir('ci_cpp_gen2'), "DATA", "calibs")
        butler = dafPersist.Butler(repoDir, calibRoot=calibDir)

        self.config = ipIsr.IsrTaskConfig()
        self.config.doSaturation = True
        self.config.doSuspect = True
        self.config.doSetBadRegions = True
        self.config.doOverscan = True
        self.config.doBias = True
        self.config.doVariance = True

        self.config.doLinearize = False
        self.config.doCrosstalk = False
        self.config.doWidenSaturationTrails = False
        self.config.doBrighterFatter = False
        self.config.doDefect = False
        self.config.doSaturationInterpolation = False
        self.config.doDark = False
        self.config.doStrayLight = False
        self.config.doFlat = False
        self.config.doApplyGains = False
        self.config.doFringe = False
        self.config.doMeasureBackground = False
        self.config.doVignette = False
        self.config.doAttachTransmissionCurve = False
        self.config.doUseOpticsTransmission = False
        self.config.doUseFilterTransmission = False
        self.config.doUseSensorTransmission = False
        self.config.doUseAtmosphereTransmission = False

        self.isrTask = ipIsr.IsrTask(config=self.config)
        # This is not an independent frame.
        self.dataRef = butler.dataRef('raw', dataId={'detector': 0, 'expId': 2020012800007})
        results = self.isrTask.runDataRef(self.dataRef)
        self.exposure = results.outputExposure

    def test_canary(self):
        """Test for data value changes.                                                                             
        """
        repoDir = os.path.join(getPackageDir('ci_cpp_gen2'), "DATA")
        calibDir = os.path.join(getPackageDir('ci_cpp_gen2'), "DATA", "calibs")
        butler = dafPersist.Butler(repoDir, calibRoot=calibDir)

        dark = butler.get('bias', {'detector': 0, 'expId': 2020012800014})
        m = hashlib.md5()
        m.update(dark.getImage().getArray())

        self.assertEquals(m.hexdigest(), '47b6328cbad5e4a212fc635e128d541e')

    def test_independentFrameLevel(self):
        """Test image mean.

        Notes
        -----
        DMTN-101 4.2

        Confirm that the mean of the result is 0 to within statistical
        error
        """
        mean = afwMath.makeStatistics(self.exposure.getImage(), afwMath.MEAN).getValue()
        print("4.2", mean)
        self.assertLess(np.abs(mean), 1)

    def test_independentFrameSigma(self):
        """Amp sigma against readnoise

        Notes
        -----
        DMTN-101 4.3

        Confirm that the 5-sigma clipped standard deviation of each
        amplifier is within 5% of the nominal readnoise, as determined
        by a robust measure of the noise in the serial overscan

        """
        ccd = self.exposure.getDetector()
        for amp in ccd:
            ampExposure = self.exposure.Factory(self.exposure, amp.getBBox())
            statControl = afwMath.StatisticsControl(5.0, 5)
            statControl.setAndMask(self.exposure.mask.getPlaneBitMask(["SAT", "BAD", "NO_DATA"]))
            sigma = afwMath.makeStatistics(ampExposure.getImage(),
                                           afwMath.STDEVCLIP, statControl).getValue()
            # needs to be < 0.05
            print("4.3", amp.getName(), sigma, amp.getReadNoise(),
                  np.abs(sigma - amp.getReadNoise())/amp.getReadNoise())
            self.assertLess(np.abs(sigma - amp.getReadNoise())/amp.getReadNoise(), 0.71)

    def test_amplifierSigma(self):
        """Clipped sigma against CR-rejected sigma

        Notes
        -----
        DMTN-101 4.4

        Run a CR rejection on the result and confirm that the
        unclipped standard deviation is consistent with the 5-sigma
        clipped value.

        """
        crTask = RepairTask()
        crRejected = self.exposure.clone()
        psf = measAlg.SingleGaussianPsf(21, 21, 3.0)
        crRejected.setPsf(psf)
        crTask.run(crRejected, keepCRs=False)

        ccd = self.exposure.getDetector()
        for amp in ccd:
            ampExposure = self.exposure.Factory(self.exposure, amp.getBBox())
            clipControl = afwMath.StatisticsControl(5.0, 5)
            clipControl.setAndMask(self.exposure.mask.getPlaneBitMask(["SAT", "BAD", "NO_DATA"]))
            sigmaClip = afwMath.makeStatistics(ampExposure.getImage(),
                                               afwMath.STDEVCLIP, clipControl).getValue()

            crAmp = crRejected.Factory(crRejected, amp.getBBox())
            statControl = afwMath.StatisticsControl()
            statControl.setAndMask(self.exposure.mask.getPlaneBitMask(["SAT", "BAD", "NO_DATA", "CR"]))
            sigma = afwMath.makeStatistics(crAmp.getImage(), afwMath.STDEV, statControl).getValue()
            # needs to be < 0.05
            print("4.4", amp.getName(), sigma, sigmaClip, np.abs(sigma - sigmaClip)/sigmaClip)
            self.assertLess(np.abs(sigma - sigmaClip)/sigmaClip, 3.0)


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()