#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from nose.plugins.attrib import attr

import sys
import os
import PyQt4
from PyQt4.QtGui import QApplication, QFileDialog
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt

import imtools.sample_data

class MyTestCase(unittest.TestCase):
    def setUp(self):
        from PyQt4.QtGui import QApplication, QFileDialog
        # self.qapp = QApplication(sys.argv)

    @attr('interactive')
    def test_something(self):
        self.assertEqual(True, False)

    @attr('interactive')
    def test_visualization(self):

        import PyQt4
        from PyQt4.QtGui import QApplication, QFileDialog
        # from teigen.dictwidgetqt import DictWidget
        # from teigen.gui import TeigenWidget
        import imtools.show_segmentation_qt
        app = QApplication(sys.argv)
        cfg = {"bool": True, "int":5, 'str': 'strdrr', 'vs':[1.0, 2.5, 7]}
        captions = {"int": "toto je int"}
        cw = imtools.show_segmentation_qt.ShowSegmentationWidget(None)
        cw.show()
        app.exec_()

    @attr('interactive')
    def test_showsegmentation_andclose(self):

        import PyQt4
        from PyQt4.QtGui import QApplication, QFileDialog
        # from teigen.dictwidgetqt import DictWidget
        # from teigen.gui import TeigenWidget
        import imtools.show_segmentation_qt
        app = QApplication(sys.argv)
        cfg = {"bool": True, "int":5, 'str': 'strdrr', 'vs':[1.0, 2.5, 7]}
        captions = {"int": "toto je int"}
        cw = imtools.show_segmentation_qt.ShowSegmentationWidget(None)

        cw.show()
        cw.close()
        # app.exec_()

    @attr('interactive')
    def test_show_segmentation_qt_widget(self):
        # from teigen.dictwidgetqt import DictWidget
        # from teigen.generators.cylindersqt import CylindersWidget
        import imtools.show_segmentation_qt as ssqt
        app = QApplication(sys.argv)
        sw = ssqt.ShowSegmentationWidget(None)
        sw.show()
        app.exec_()


    # @attr('interactive')
    def test_show_segmentation_qt_widget_hidden_buttons(self):
        # = np.zeros([10, 10, 10])
        import imtools
        import imtools.sample_data
        # imtools.sam
        # imtools.sample_data.get_sample_data("sliver_training_001")
        # from teigen.dictwidgetqt import DictWidget
        # from teigen.generators.cylindersqt import CylindersWidget
        import imtools.show_segmentation_qt as ssqt
        app = QApplication(sys.argv)
        # app = QApplication([])

        # if "TRAVIS" in os.environ:
        #     app.setGraphicsSystem("openvg")
        # sw = ssqt.ShowSegmentationWidget(None, show_buttons=False)
        sw = ssqt.ShowSegmentationWidget(None, show_load_interface=True)
        self.assertIn("add_data_file", sw.ui_buttons.keys())
        sw.show()
        # app.exec_()
        sw.close()
        sw.deleteLater()
        sw = None
        app.quit()
        app.deleteLater()
        # app.quit()
        # app.exit()

    # @attr('interactive')
    def test_add_data_and_show(self):
        """
        creates VTK file from input data
        :return:
        """
        datap = imtools.sample_data.donut()

        segmentation = datap['segmentation']
        voxelsize_mm = datap['voxelsize_mm']

        import imtools.show_segmentation_qt as ssqt
        import gc
        app = QApplication(sys.argv)
        # app.setGraphicsSystem("openvg")
        sw = ssqt.ShowSegmentationWidget(None, show_load_button=True)
        sw.smoothing = False
        sw.add_data(segmentation, voxelsize_mm=voxelsize_mm)
        QTest.mouseClick(sw.ui_buttons['Show volume'], Qt.LeftButton)
        # sw.add_vtk_file("~/projects/imtools/mesh.vtk")
        sw.show()
        # app.exec_(exec_)
        sw.close()
        sw.deleteLater()

        sw = None
        app.quit()
        app.deleteLater()
        # self.qapp.quit()
        # self.qapp.deleteLater()
        # gc.collect()

        # app = QApplication(sys.argv)
        # app.quit()
        # self.qapp.exit()
        # app.exec_()


if __name__ == '__main__':
    unittest.main()
