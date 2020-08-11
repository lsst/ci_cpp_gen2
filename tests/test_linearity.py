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
import unittest
import lsst.utils.tests


# TODO: DM-26396
#       Update these tests to validate calibration construction.
class LinearityTestCases(lsst.utils.tests.TestCase):

    def test_setup_independentFrame(self):
        """Ill defined/is the construction step.

        DMTN-101 7.1

        For each flat exposure, divide by the (known) product of
        intensity and exposure time.  For each amplifier calculate the
        median intensity, and fit a suitable functional form to
        measure the non-linearity.
        """
        pass

    def test_independentFrameLevel(self):
        """Ill defined.

        Notes
        -----
        DMTN-101 7.2

        Analyse these non-linear curves to determine the point at
        which the data cannot be reliably linearised.

        """
        pass

    def test_independentFrameSigma(self):
        """Missing data.

        Notes
        -----
        DMTN-101 7.3

        For each "spot" exposure, make a robust measurement
        (e.g. median) of the flux in the flat-topped profile of each
        spot; the exact details of what defines the top of the spot
        are TBD.  Divide these value by the known fluxes delivered to
        the spots (as provided by the CBP's photodiode), and fit a
        suitable functional form to measure the non-linearity.

        """
        pass

    def test_amplifierSigma(self):
        """Missing data.

        Notes
        -----
        DMTN-101 7.4

        Analyse these non-linear curves to determine the point at
        which the data cannot be reliably linearised.

        """
        pass


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
