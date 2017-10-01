#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rc522_assist.helper import RFIDHelper
import unittest


class RunnerTestCase(unittest.TestCase):
    """
    Unit Test case for the class assisting for handling RFID RC522 cards.
    """

    def test_rc522_helper(self):
        """
        Basic test
        :return:
        """
        self.helper = RFIDHelper()
        self.assertIsNotNone(self.helper)

