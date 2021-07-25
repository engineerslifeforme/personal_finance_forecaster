""" Tests of forecast """

import unittest

from app.forecast import (
    compute_start_and_end
)

class TestForecast(unittest.TestCase):
    """ Tests of forecast """

    def test_compute_start_and_end(self):
        self.assertEqual(
            compute_start_and_end(25, 26, 0, 0,),
            12
        )
