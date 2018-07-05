#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
Module is used for visualization of segmentation stored in pkl file.
"""

import os.path
import os.path as op
import sys

path_to_script = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(path_to_script, "../extern/dicom2fem/src"))
import logging
logger = logging.getLogger(__name__)

# from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication
import argparse


import numpy as np
# import dicom2fem
# import dicom2fem.seg2fem
# from dicom2fem import seg2fem
from dicom2fem.seg2fem import gen_mesh_from_voxels_mc, smooth_mesh
from .image_manipulation import select_labels
from . import image_manipulation as imma

# import misc
# import viewer

def _auto_segmentation(segmentation, label=None):
    if label is None:
        ma = np.max(segmentation)
        mi = np.min(segmentation)
        mn = (ma + mi) * 0.5

        segmentation = segmentation > mn
    return segmentation


class SegmentationToVTK():

    def __init__(self,
                       segmentation=None,
                       voxelsize_mm=None,
                       slab=None):
        """
        set_input_data
        set_resize_parameters
        prepare_vtk_file
        """
        if voxelsize_mm is None:
            voxelsize_mm = np.ones([3, 1])
        self.segmentation = segmentation
        self.voxelsize_mm = voxelsize_mm
        if slab is None:
            slab = create_slab_from_segmentation(segmentation)
        self.slab = slab

    def set_resize_parameters(
            self,
            degrad=6,
            labels=None,
            resize_mm=None,
            resize_voxel_number=None,

    ):
        """
        set_input_data() should be called before
        :param degrad:
        :param labels:
        :param resize_mm:
        :param resize_voxel_number:
        :return:
        """
        # from . import show_segmentation

        logger.debug("set_resize_parameters(\ndegrad={}, \nlabels={}\nresize_mm={}\nresize_voxel_number={}".format(
            degrad, labels, resize_mm, resize_voxel_number
        ))
        degrad = int(degrad)

        # import ipdb; ipdb.set_trace()
        # return voxelsize_mm, degrad
        self.degrad = degrad
        self.labels = labels
        if self.slab is not None and labels is not None:
            segmentation = select_labels(self.segmentation, labels, slab=self.slab)
            # segmentation = show_segmentation.select_labels(self.segmentation, labels, slab=self.slab)
        else:
            segmentation = self.segmentation
        if segmentation.max() == False:
            logger.info("Nothing found for labels " + str(labels))
            return

        if resize_voxel_number is not None:
            nvoxels = np.sum(segmentation > 0)
            volume = nvoxels * np.prod(self.voxelsize_mm)
            voxel_volume = volume / float(resize_voxel_number)
            resize_mm = voxel_volume ** (1.0 / 3.0)
        # self.working_voxelsize_mm = voxelsize_mm
        # self.working_segmentation = segmentation
        self.resize_mm = resize_mm

    def set_labels(self, labels=None):
        """

        :param labels:
        :return:
        """
        if labels is None:
            self.labels = list(self.slab)
        else:
            self.labels = labels

    def _select_labels(self, labels=None):
        logger.debug("select_labels() started with labels={}".format(labels))
        if self.slab is not None and labels is not None:
            segmentation = select_labels(self.segmentation, labels, slab=self.slab)
        else:
            segmentation = (self.segmentation > 0).astype(self.segmentation.dtype)
        self.binar_segmentation = segmentation

    def _resize_selected_labels(self):
        """
        self.select_labels sould be called first
        :return:
        """
        orig_dtype = self.binar_segmentation.dtype

        if orig_dtype == np.bool:
            segmentation = self.binar_segmentation.astype(np.int8)
        else:
            segmentation = self.binar_segmentation


        segmentation = segmentation[::self.degrad, ::self.degrad, ::self.degrad]
        voxelsize_mm = self.voxelsize_mm * self.degrad

        if self.resize_mm is not None:
            logger.debug("resize begin")
            new_voxelsize_mm = np.asarray([self.resize_mm, self.resize_mm, self.resize_mm])
            import imtools
            prev_shape = segmentation.shape
            segmentation = imtools.image_manipulation.resize_to_mm(segmentation, voxelsize_mm=voxelsize_mm, new_voxelsize_mm=new_voxelsize_mm,order=0)
            voxelsize_mm = new_voxelsize_mm
            logger.debug("resize finished, old shape = {}, new shape = {}".format(str(prev_shape), str(segmentation.shape)))
            logger.debug("segmentation min={}, max={}".format(np.min(segmentation), np.max(segmentation)))
        self.resized_segmentation = segmentation
        self.resized_voxelsize_mm = voxelsize_mm

    def set_output(
            self,
            filename=None,
            smoothing=True,
            pvsm_file=None
    ):

        if filename is None:
            # vtk_file = "mesh_geom.vtk"
            filename = "mesh_{}.vtk"
        self.vtk_file = os.path.expanduser(filename)
        self.smoothing = smoothing
        self.pvsm_file = pvsm_file




    def prepare_stl_file(self):
        pass

    def make_vtk_file(self):
        self._prepare_vtk_file(labels=self.labels)  # , smoothing=self.smoothing, vtk_file=self.vtk_file)

    def _prepare_vtk_file(
            self,
            labels,
            ):
        """

        :param segmentation:
        :param voxelsize_mm:
        :param degrad:
        :param label:
        :param smoothing:
        :param vtk_file:
        :param qt_app:
        :param show:
        :param resize_mm: resize to defined size of voxel
        :param resize_voxel_number: resize to defined voxel number (aproximatly)

        :return:

        Funkce vrací trojrozměrné porobné jako data['segmentation']
        v data['slab'] je popsáno, co která hodnota znamená
        """


        # if vtk_file is None:
        #     vtk_file = "mesh_geom.vtk"
        # vtk_file = os.path.expanduser(vtk_file)
        strlabel = imma.get_nlabels(slab=self.slab, labels=labels, return_mode="str")
        logger.debug(strlabel)
        vtk_filename = self.vtk_file.format(strlabel)
        logger.debug(vtk_filename)

        self._select_labels(labels)
        # import sed3
        # sed3.show_slices(self.binar_segmentation)

        self._resize_selected_labels()
        # sed3.show_slices(self.resized_segmentation)

        # _stats(self.segmentation)
        # _stats(self.binar_segmentation)
        _stats(self.resized_segmentation)

        # import pdb; pdb.set_trace()
        logger.debug("gen_mesh_from_voxels_mc() started")
        mesh_data = gen_mesh_from_voxels_mc(self.resized_segmentation, self.resized_voxelsize_mm)
        if self.smoothing:
            mesh_data.coors = smooth_mesh(mesh_data)
            # mesh_data.coors = seg2fem.smooth_mesh(mesh_data)

        else:
            pass
            # mesh_data = gen_mesh_from_voxels_mc(segmentation, voxelsize_mm * 1.0e-2)
            # mesh_data.coors +=
        logger.debug("gen_mesh_from_voxels_mc() finished")
        mesh_data.write(vtk_filename)
        return vtk_filename

    def make_vtk_files(
            self,
            # labels=None,
            # smoothing=True,
            # vtk_file=None,
            # resize_mm=None,
            # resize_voxel_number=None,
            # slab=None,
            # pvsm_file=None
    ):
        vtk_files = []
        for lab in self.labels:
            # labi = slab[lab]
            fn = self._prepare_vtk_file(
                # vtk_file=self.vtk_file,
                labels=lab,
                # slab=slab,
                # smoothing=self.smoothing,
                # resize_mm=resize_mm,
                # resize_voxel_number=resize_voxel_number,
            )
            if fn is not None:
                vtk_files.append(fn)

        pvsm_file = self.pvsm_file
        if pvsm_file is None:
            strlabels = imma.get_nlabels(slab=self.slab, labels=self.labels, return_mode="str")
            labels_in_str = "-".join(strlabels)
            pvsm_file = self.vtk_file.format(labels_in_str)
            pvsm_file, ext = op.splitext(pvsm_file)
            pvsm_file = pvsm_file + ".pvsm"
        create_pvsm_file(vtk_files, pvsm_filename=pvsm_file)
        return vtk_files

def create_slab_from_segmentation(segmentation, slab=None):

    if slab is None:
        slab = {}
        if segmentation is not None:
            labels = np.unique(segmentation)
            for label in labels:
                slab[str(label)] = label
    return slab

def showSegmentation(
            segmentation=None,
            voxelsize_mm=np.ones([3, 1]),
            degrad=6,
            labels=None,
            smoothing=True,
            vtk_file=None,
            qt_app=None,
            show=True,
            resize_mm=None,
            resize_voxel_number=None
):
    """

    :param segmentation:
    :param voxelsize_mm:
    :param degrad:
    :param label:
    :param smoothing:
    :param vtk_file:
    :param qt_app:
    :param show:
    :param resize_mm: resize to defined size of voxel
    :param resize_voxel_number: resize to defined voxel number (aproximatly)

    :return:

    Funkce vrací trojrozměrné porobné jako data['segmentation']
    v data['slab'] je popsáno, co která hodnota znamená
    """

    s2vtk = SegmentationToVTK(segmentation, voxelsize_mm)
    s2vtk.set_resize_parameters(degrad=degrad, resize_mm=resize_mm, resize_voxel_number=resize_voxel_number)
    s2vtk.set_labels(labels)
    s2vtk.set_output(filename=vtk_file, smoothing=smoothing)
    vtk_file = s2vtk.make_vtk_file()
    # vtk_file = prepare_vtk_file(segmentation, voxelsize_mm, degrad, labels, smoothing=smoothing,)
    if show:
        if qt_app is None:
            qt_app = QApplication(sys.argv)
            logger.debug("qapp constructed")

        import vtkviewer
        vtkv = vtkviewer.VTKViewer()
        vtkv.AddFile(vtk_file)
        vtkv.Start()

        # view = viewer.QVTKViewer(vtk_file)
        # print ('show viewer')
        # view.exec_()
    # if orig_dtype is np.bool:
    #     segmentation = segmentation.astype(np.bool)

    return segmentation

def _stats(data):
    print("stats")
    print(str(data.shape))
    un = np.unique(data)
    for lab in un:
        print(lab, " : ", np.sum(data==lab))

def prettify(elem):
    # from xml.etree.ElementTree import Element, SubElement, Comment, tostring
    from xml.etree import ElementTree
    from xml.dom import minidom
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def create_pvsm_file(vtk_files, pvsm_filename, relative_paths=True):
    from xml.etree.ElementTree import Element, SubElement, Comment
    import os.path as op

    top = Element('ParaView')

    comment = Comment('Generated for PyMOTW')
    top.append(comment)

    numberi = 4923
    # vtk_file = "C:\Users\miros\lisa_data\83779720_2_liver.vtk"

    sms = SubElement(top, "ServerManagerState", version="5.4.1")
    file_list = SubElement(sms, "ProxyCollection", name="sources")
    for vtk_file_orig in vtk_files:
        numberi +=1
        dir, vtk_file_head = op.split(vtk_file_orig)
        if relative_paths:
            vtk_file = vtk_file_head
        else:
            vtk_file = vtk_file_orig
        number = str(numberi)
        proxy1 = SubElement(sms, "Proxy", group="sources", type="LegacyVTKFileReader", id=number, servers="1")
        property = SubElement(proxy1, "Property", name="FileNameInfo", id=number + ".FileNameInfo", number_of_elements="1")
        element = SubElement(property, "Element", index="0", value=vtk_file)
        property2 = SubElement(proxy1, "Property", name="FileNames", id=number + ".FileNames", number_of_elements="1")
        pr2s1 = SubElement(property2, "Element", index="0", value=vtk_file)
        pr2s2 = SubElement(property2, "Domain", name="files", id=number + ".FileNames.files")

    #     < Property
    #     name = "Opacity"
    #     id = "8109.Opacity"
    #     number_of_elements = "1" >
    #     < Element
    #     index = "0"
    #     value = "0.28" / >
    #     < Domain
    #     name = "range"
    #     id = "8109.Opacity.range" / >
    # < / Property >

        fn1 = SubElement(file_list, "Item", id=number, name=vtk_file_head)

    xml_str = prettify(top)
    # logger.debug(xml_str)
    with open(op.expanduser(pvsm_filename), "w") as file:
        file.write(xml_str)

    # ElementTree(top).write()



def main():
    logger = logging.getLogger()

    logger.setLevel(logging.WARNING)
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    # logger.debug('input params')

    # input parser
    parser = argparse.ArgumentParser(
        description='\
            3D visualization of segmentation\n\
            \npython show_segmentation.py\n\
            \npython show_segmentation.py -i resection.pkl -l 2 3 4 -d 4')
    parser.add_argument(
        '-i', '--inputfile',
        default="organ.pklz",
        help='input file')
    parser.add_argument(
        '-o', '--outputfile',
        default='~/lisa_data/mesh_geom.vtk',
        help='output file')
    parser.add_argument(
        '-d', '--degrad', type=int,
        default=4,
        help='data degradation, default 4')
    parser.add_argument(
        '-r', '--resize', type=float,
        default=None,
        help='resize voxel to defined size in milimeters, default is None')
    parser.add_argument(
        '-rvn', '--resize-voxel-number', type=float,
        default=None,
        help='resize voxel to defined number of voxels, default is None')
    parser.add_argument(
        '-l', '--label', type=int, metavar='N', nargs='+',
        default=[1],
        help='segmentation labels, default 1')
    args = parser.parse_args()

    # data = misc.obj_from_file(args.inputfile, filetype='pickle')
    # if args.inputfile is None:
    #     ds = None
    #     data = {
    #         "voxelsize_mm": [1, 1, 1]
    #     }
    # else:
    import io3d
    data = io3d.read(args.inputfile, dataplus_format=True)
    # args.label = np.array(eval(args.label))
    # print args.label
    if "segmentation" in data.keys() and np.sum(data["segmentation"] > 0):
        segmentation_key = "segmentation"
    else:
        segmentation_key = "data3d"

    # import pdb; pdb.set_trace()
    _stats(data[segmentation_key])
    ds = select_labels(data[segmentation_key], args.label)
    # ds = ds.astype("uint8")
    # tonzero_voxels_number = np.sum(ds != 0)
    # if nonzero_voxels_number == 0:
    #     ds = data["data3d"] > 0

    outputfile = os.path.expanduser(args.outputfile)

    showSegmentation(ds, degrad=args.degrad, voxelsize_mm=data['voxelsize_mm'], vtk_file=outputfile,
                     resize_mm=args.resize, resize_voxel_number=args.resize_voxel_number)

if __name__ == "__main__":
    main()
