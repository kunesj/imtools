#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from nose.plugins.attrib import attr
import imtools.sample_data
import imtools.uiThreshold
import matplotlib.pyplot as plt


class MyTestCase(unittest.TestCase):
    @attr('interactive')
    def test_something(self):
        self.assertEqual(True, False)

    def test_threshold(self):
        datap = imtools.sample_data.generate()
        uit = imtools.uiThreshold.uiThreshold(datap['data3d'], datap['voxelsize_mm'], interactivity=False, threshold=100)
        uit.run()

    def test_ui_threshold(self):
        datap = imtools.sample_data.generate()
        uit = imtools.uiThreshold.uiThreshold(datap['data3d'], datap['voxelsize_mm'], interactivity=True, threshold=100)
        uit.run()
        plt.show()


    def test_ui_threshold_qt(self):
        datap = imtools.sample_data.generate()
        uit = imtools.uiThreshold.uiThreshold(datap['data3d'], datap['voxelsize_mm'], interactivity=True, threshold=100)
        uit.run()
        plt.show()
if __name__ == '__main__':
    unittest.main()
