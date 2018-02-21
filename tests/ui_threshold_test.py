#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from nose.plugins.attrib import attr
import imtools
import imtools.sample_data
import imtools.uiThreshold
import imtools.thresholding_functions
import matplotlib.pyplot as plt
import sys
from PyQt4.QtGui import QApplication, QDialog, QGridLayout, QPushButton
import numpy as np

class MyTestCase(unittest.TestCase):
    @attr('interactive')
    def test_something(self):
        self.assertEqual(True, False)

    def test_threshold(self):
        datap = imtools.sample_data.generate()
        uit = imtools.uiThreshold.uiThreshold(datap['data3d'], datap['voxelsize_mm'], interactivity=False, threshold=100)
        uit.run()

    def test_threshold_with_seed(self):
        datap = imtools.sample_data.generate()
        uit = imtools.uiThreshold.uiThreshold(datap['data3d'], datap['voxelsize_mm'], interactivity=False, seeds=datap["seeds_porta"])
        uit.run()

    @attr('interactive')
    def test_ui_threshold(self):
        datap = imtools.sample_data.generate()
        uit = imtools.uiThreshold.uiThreshold(datap['data3d'], datap['voxelsize_mm'], interactivity=True, threshold=100)
        uit.run()
        plt.show()

    def test_gui_constructor(self):
        datap = imtools.sample_data.generate()
        uit = imtools.uiThreshold.uiThreshold(datap['data3d'], datap['voxelsize_mm'], interactivity=True, threshold=100)


    @attr('interactive')
    def test_ui_threshold_qt(self):
        app = QApplication(sys.argv)
        datap = imtools.sample_data.generate()
        uit = imtools.uiThreshold.uiThresholdQt(datap['data3d'], datap['voxelsize_mm'], interactivity=True, threshold=100)

        uit.run()
        # plt.show()

    def test_getPriorityObject(self):
        import skimage.morphology
        nobj = 2
        datap = imtools.sample_data.generate()
        thresholded = datap["data3d"] > 80
        selection = imtools.thresholding_functions.getPriorityObjects(thresholded, nObj=nobj, seeds_multi_index=None)

        lab = skimage.morphology.label(selection)
        output_nobj = np.unique(lab)

        self.assertEqual(nobj, nobj)

    def test_getPriorityObjectSeeds(self):
        import skimage.morphology

        nobj = 1
        datap = imtools.sample_data.generate()
        thresholded = datap["data3d"] > 80
        seeds_multi_index = np.nonzero(datap['seeds'] == 1)

        selection = imtools.thresholding_functions.getPriorityObjects(thresholded, nObj=nobj, seeds_multi_index=seeds_multi_index)

        lab = skimage.morphology.label(selection)
        output_nobj = len(np.unique(lab))

        self.assertEqual(output_nobj, nobj + 1)  # one is for background label

    @unittest.skip("not completed")
    def test_thresholding(self):
        import skimage.morphology
        datap = imtools.sample_data.generate()

        max_threshold = None
        selection = imtools.thresholding_functions.thresholding(
            datap['data3d'],
            min_threshold=80,
            max_threshold=max_threshold,
            use_min_threshold=True,
            use_max_threshold=max_threshold is None
        )
        lab = skimage.morphology.label(selection)
        output_nobj = len(np.unique(lab))

        self.assertEqual(output_nobj, 1)

if __name__ == '__main__':
    unittest.main()
