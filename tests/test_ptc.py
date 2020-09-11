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
class PtcTestCases(lsst.utils.tests.TestCase):

    def setup_independentFrame(self):
        """Ill-defined case.

        Notes
        -----
        DMTN-101 6.1, 6.2:

        Form the function (I$_{\text{1}}$ -
        I$_{\text{2}}$)/(I$_{\text{1}}$ + I$_{\text{2}}$) whose mean
        value is 1/gain.  Note that this is sensitive to
        brighter-fatter so bin (or use BF correction code)

        Measure the gain values for each amplifier that minimises
        discontinuities at amp boundaries.
        """
        pass


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
