#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import vtk
import numpy as nm
import yaml
import argparse
import sys
import numpy as np


# new interface

class VTKTreeGenerator:
    """
    This generator is called by generateTree() function as a general form.
    Other similar generator is used for generating LAR outputs.
    """
    def __init__(self, gtree):
        self.shape = gtree.shape
        self.data3d = np.zeros(gtree.shape, dtype=np.int)
        self.voxelsize_mm = gtree.voxelsize_mm
        self.gtree = gtree

    def add_cylinder(self, p1m, p2m, rad, id):
        """
        Funkce na vykresleni jednoho segmentu do 3D dat
        """
        pass

    def get_output(self):
        self.polyData = gen_tree(self.gtree)
        return self.polyData

    def save(self, outputfile):

        writer = vtk.vtkPolyDataWriter()
        writer.SetFileName(outputfile)
        writer.SetInput(self.polyData)
        writer.Write()

    def show(self):
        logger.info("there is no show implemented")
# old interface


def get_cylinder(upper, height, radius,
                 direction,
                 resolution=10):

    src = vtk.vtkCylinderSource()
    src.SetCenter((0, height/2, 0))
    src.SetHeight(height + radius/2.0)
    src.SetRadius(radius)
    src.SetResolution(resolution)

    rot1 = vtk.vtkTransform()
    fi = nm.arccos(direction[1])

    rot1.RotateWXYZ(-nm.rad2deg(fi), 0.0, 0.0, 1.0)
    u = nm.abs(nm.sin(fi))
    rot2 = vtk.vtkTransform()
    if u > 1.0e-6:

        # sometimes d[0]/u little bit is over 1
        d0_over_u = direction[0] / u
        if d0_over_u > 1:
            psi = 0
        elif d0_over_u < -1:
            psi = 2 * nm.pi
        else:
            psi = nm.arccos(direction[0] / u)

        logger.debug('d0 '+str(direction[0])+'  u '+str(u)+' psi '+str(psi))
        if direction[2] < 0:
            psi = 2 * nm.pi - psi

        rot2.RotateWXYZ(-nm.rad2deg(psi), 0.0, 1.0, 0.0)

    tl = vtk.vtkTransform()
    tl.Translate(upper)

    tr1a = vtk.vtkTransformFilter()
    tr1a.SetInput(src.GetOutput())
    tr1a.SetTransform(rot1)

    tr1b = vtk.vtkTransformFilter()
    tr1b.SetInput(tr1a.GetOutput())
    tr1b.SetTransform(rot2)

    tr2 = vtk.vtkTransformFilter()
    tr2.SetInput(tr1b.GetOutput())
    tr2.SetTransform(tl)

    tr2.Update()

    return tr2.GetOutput()


def gen_tree(tree_data):

    points = vtk.vtkPoints()
    polyData = vtk.vtkPolyData()
    polyData.Allocate(1000, 1)
    polyData.SetPoints(points)
    poffset = 0

    for br in tree_data:
        cyl = get_cylinder(br['upperVertex'],
                           br['length'],
                           br['radius'],
                           br['direction'],
                           resolution=16)

        for ii in xrange(cyl.GetNumberOfPoints()):
            points.InsertPoint(poffset + ii, cyl.GetPoint(ii))

        for ii in xrange(cyl.GetNumberOfCells()):
            cell = cyl.GetCell(ii)
            cellIds = cell.GetPointIds()
            for jj in xrange(cellIds.GetNumberOfIds()):
                oldId = cellIds.GetId(jj)
                cellIds.SetId(jj, oldId + poffset)

            polyData.InsertNextCell(cell.GetCellType(),
                                    cell.GetPointIds())

        poffset += cyl.GetNumberOfPoints()

    return polyData


def compatibility_processing(indata):
    scale = 1e-3
    scale = 1

    outdata = []
    for key in indata:
        ii = indata[key]
        logger.debug(ii)
        br = {}
        try:
            # old version of yaml tree
            vA = ii['upperVertexXYZmm']
            vB = ii['lowerVertexXYZmm']
            radi = ii['radius']
            lengthEstimation = ii['length']
        except:
            # new version of yaml
            try:
                vA = ii['nodeA_ZYX_mm']
                vB = ii['nodeB_ZYX_mm']
                radi = ii['radius_mm']
                lengthEstimation = ii['lengthEstimation']
            except:
                continue

        br['upperVertex'] = nm.array(vA) * scale
        br['radius'] = radi * scale
        br['real_length'] = lengthEstimation * scale

        vv = nm.array(vB) * scale - br['upperVertex']
        br['direction'] = vv / nm.linalg.norm(vv)
        br['length'] = nm.linalg.norm(vv)
        outdata.append(br)

    return outdata

def fix_tree_structure(tree_raw_data):
    if 'graph' in tree_raw_data:
        trees = tree_raw_data['graph']
    else:
        trees = tree_raw_data['Graph']
    return trees

def vt_file_2_vtk_file(infile, outfile, text_label=None):
    """
    From vessel_tree.yaml to output.vtk

    :param vessel_tree:  vt structure
    :param outfile: filename with .vtk extension
    :param text_label: text label like 'porta' or 'hepatic_veins'
    :return:

    """
    yaml_file = open(infile, 'r')
    tree_raw_data = yaml.load(yaml_file)
    vt2vtk_file(tree_raw_data, outfile, text_label)



def vt2vtk_file(vessel_tree, outfile, text_label=None):
    """
    vessel_tree structure
    :param vessel_tree:  vt structure
    :param outfile: filename with .vtk extension
    :param text_label: text label like 'porta' or 'hepatic_veins'
    :return:
    """
    trees = fix_tree_structure(vessel_tree)

    tkeys = trees.keys()
    if text_label is None:
        text_label = tkeys[0]

    tree_data = compatibility_processing(trees[text_label])
    polyData = gen_tree(tree_data)

    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(outfile)
    writer.SetInput(polyData)
    writer.Write()


def main():
    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    # create file handler which logs even debug messages
    # fh = logging.FileHandler('log.txt')
    # fh.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(
    #     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # fh.setFormatter(formatter)
    # logger.addHandler(fh)
    # logger.debug('start')

    # input parser
    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        'inputfile',
        default=None,
        help='input file'
    )
    parser.add_argument(
        'outputfile',
        default='output.vtk',
        nargs='?',
        help='output file'
    )
    parser.add_argument(
        '-l','--label',
        default=None,
        help='text label of vessel tree. f.e. "porta" or "hepatic_veins". \
        First label is used if it is set to None'
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Debug mode')
    args = parser.parse_args()

    if args.debug:
        ch.setLevel(logging.DEBUG)

    vt_file_2_vtk_file(args.inputfile, args.outputfile, args.label)


if __name__ == "__main__":
    main()
