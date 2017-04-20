#! /usr/local/bin/python
# -*- coding: utf-8 -*-

import Part
import copy
from math import *

def main():

    chamber_spc = readChamberSpec()
    chamber_obj = ChamberObj( chamber_spc )

    chamber_obj.subtruct()
    chamber_obj.draw()

#---------------------------------------------------
# subtruct function
#---------------------------------------------------
def subtructPipe( chamber ):

    for node in chamber.get_node_list():
        for branch in node.get_branch_list():
            pipe = branch.get_pipe()
            o_c  = pipe.get_outer_cylinder()
            subtructed_o_c = subtructedOuterCylinder( o_c, chamber )
            pipe.set_outer_cylinder( subtructed_o_c )

    return chamber

def subtructedOuterCylinder( o_c, chamber ):

    for node_i in chamber.get_node_list():
        for branch_i in node_i.get_branch_list():
            pipe = branch_i.get_pipe()
            i_c  = pipe.get_inner_cylinder()
            o_c  = o_c.cut(i_c)

    return o_c

#---------------------------------------------------
# draw function
#---------------------------------------------------
def drawChamber( chamber ):

    for node in chamber.get_node_list():
        for branch in node.get_branch_list():
            pipe = branch.get_pipe()
            o_c  = pipe.get_outer_cylinder()

            Part.show(o_c)

#---------------------------------------------------
# read functions
#---------------------------------------------------
def readChamberSpec():
    icf70  = ICF(  70, 12.7 )
    icf114 = ICF( 114, 17.5 )
    icf152 = ICF( 152, 20   )
    icf203 = ICF( 203, 22   )
    icf253 = ICF( 253, 25   )
    icf306 = ICF( 306, 26   )

    p_icf70  = Pipe(  42.7, 1.65 )
    p_icf114 = Pipe(  63.5, 2    )
    p_icf152 = Pipe( 101.6, 2.1  )
    p_icf203 = Pipe( 153  , 3    )
    p_icf253 = Pipe( 203  , 3    )
    p_icf306 = Pipe( 256, 3    )



    #      1  = Branch( icf306, p_icf306,   r, theta,  phi)
    branch_1  = Branch( icf306, p_icf306, 242,     0,   0 )
    branch_2  = Branch( icf306, p_icf306, 258,     0, 180 )
    branch_3  = Branch( icf114, p_icf114, 245,     0,  90 )
    branch_9  = Branch( icf114, p_icf114, 200,   180,  90 )

    branch_6  = Branch( icf70 , p_icf70 , 220,  120, 130 )
    branch_10 = Branch( icf70 , p_icf70 , 170,  120,  90 )

    #branch_4  = Branch( icf70 , p_icf70 , 185,   50,   0 )
    #branch_5  = Branch( icf70 , p_icf70 , 150,   90,   0 )
    #branch_7  = Branch( icf70 , p_icf70 , 130,  120,  30 )
    #branch_8  = Branch( icf70 , p_icf70 , 185,  180,   0 )

    focal_point_A =  [ branch_1, branch_2, branch_3, branch_9]
    focal_point_B =  [ branch_6, branch_10]
    #focal_point_C =  [ branch_4, branch_5, branch_8]
    #focal_point_D =  [ branch_7 ]

    node0 = Node( focal_point_A,   0, 0,     0 )
    node1 = Node( focal_point_B,   0, 0,    -5 )
    #node2 = Node( focal_point_C,   0, 0,  -125 )
    #node3 = Node( focal_point_D, -90, 0,  -125 )

    #node_list = [node0, node1, node2, node3]
    #node_list = [node0]
    node_list = [node0, node1]

    pre_chamber = Chamber( node_list )

    return pre_chamber


#---------------------------------------------------
# chamberObj
#---------------------------------------------------
# pipe_obj_list = [ [o_c, i_c], [o_c, i_c], ... , [o_c, i_c] ]


class ChamberObj:

    def __init__ (self, chamber):
        self.pipe_obj_list   = self.make_pipe_obj_list  ( chamber.get_node_list() )
        self.frange_obj_list = self.make_frange_obj_list( chamber.get_node_list() )

    def make_pipe_obj_list(self, node_list):

        pipe_obj_list = []

        for node in node_list:
            branch_list = node.get_branch_list()

            for branch in branch_list:
                pipe = branch.get_pipe()

                xyz = node.get_xyz()

                r     = branch.get_r()
                theta = branch.get_theta()
                phi   = branch.get_phi()

                origin    = convert_x_y_z_to_FreeCADVector(xyz[0],xyz[1],xyz[2]) #nodeの位置
                direction = convert_r_theta_phi_to_FreeCADVector(r,theta,phi)    #branchの向き

                o_radius = pipe.get_outer_diameter() / 2
                i_radius = pipe.get_inner_diameter() / 2

                length = r #暫定（本当はオフセットがある）

                o_c = Part.makeCylinder( o_radius, length, origin, direction, 360)
                i_c = Part.makeCylinder( i_radius, length+10, origin, direction, 360)

                pipe_obj_list.append( [o_c, i_c] )

        return pipe_obj_list

    def make_frange_obj_list(self, node_list):

        frange_obj_list = []

        for node in node_list:
            branch_list = node.get_branch_list()

            for branch in branch_list:
                frange = branch.get_frange()

                xyz = node.get_xyz()

                r     = branch.get_r()
                theta = branch.get_theta()
                phi   = branch.get_phi()

                origin    = convert_x_y_z_to_FreeCADVector(xyz[0],xyz[1],xyz[2]) #nodeの位置
                direction = convert_r_theta_phi_to_FreeCADVector(r,theta,phi)    #branchの向き

                frange_origin    = origin + direction
                frange_direction = convert_r_theta_phi_to_FreeCADVector(-r,theta,phi)    #branchの向き

                radius = frange.get_diameter() / 2
                length = frange.get_thickness()

                frange_obj = Part.makeCylinder( radius, length, frange_origin, frange_direction, 360)

                frange_obj_list.append( frange_obj )

        return frange_obj_list

    #def subtruct(self):

    #    self.subtructed_pipe_obj_list = []

    #    test = self.pipe

    #    for pipe_obj_o in self.pipe_obj_list:
    #        o_c = pipe_obj_o[0]

    #        for pipe_obj_i in self.pipe_obj_list:
    #            i_c = pipe_obj_i[1]
    #            o_c = o_c.cut(i_c)

    #        self.subtructed_pipe_obj_list.append( o_c )

    def subtruct(self):

        self.subtructed_pipe_obj_list = []

        for i in xrange(len(self.pipe_obj_list)):
            o_c = self.pipe_obj_list[i][0]

            for j in xrange(len(self.pipe_obj_list)):
                i_c  = self.pipe_obj_list[j][1]
                o_c = o_c.cut(i_c)

            self.subtructed_pipe_obj_list.append( o_c )

    def subtruct_2(self):

        for i in xrange(len(self.pipe_obj_list)):
            o_c = self.pipe_obj_list[i][0]

            for j in xrange(len(self.pipe_obj_list)):
                i_c  = self.pipe_obj_list[j][1]
                o_c = o_c.cut(i_c)

            self.pipe_obj_list[i][0] = o_c

    def draw(self):

        #for pipe_obj in self.pipe_obj_list:
        #    Part.show(pipe_obj[0]) #outer cylinderの描画

        #for pipe_obj in self.pipe_obj_list:
        #    Part.show(pipe_obj[1]) #inner cylinderの描画

        for pipe_obj in self.subtructed_pipe_obj_list:
            Part.show(pipe_obj)

        #for frange_obj in self.frange_obj_list:
        #    Part.show(frange_obj)

#---------------------------------------------------
# Utils
#---------------------------------------------------
def convert_r_theta_phi_to_FreeCADVector(r,theta,phi):
    x = 0
    y = 0
    z = 0

    #if (phi == 0):
    #    x =   0
    #    y =   0
    #    z = + r
    #elif (phi == 180):
    #    x =   0
    #    y =   0
    #    z = - r
    #elif (theta == 0):
    #    x = r * sin(radians(phi))
    #    y = 0
    #    z = r * cos(radians(phi))
    #elif (theta == 180):
    #    x = - r * sin(radians(phi))
    #    y = 0
    #    z = r * cos(radians(phi))
    #else:
    #    x = r * sin(radians(phi)) * cos(radians(theta))
    #    y = r * sin(radians(phi)) * sin(radians(theta))
    #    z = r * cos(radians(phi))

    x = r * sin(radians(phi)) * cos(radians(theta))
    y = r * sin(radians(phi)) * sin(radians(theta))
    z = r * cos(radians(phi))

    return FreeCAD.Vector(x,y,z)

def convert_x_y_z_to_FreeCADVector(x,y,z):

    return FreeCAD.Vector(x,y,z)


class ICF:
    def __init__(self, size, thickness):
        self.size      = size
        self.thickness = thickness

    def get_diameter( self ):
        return self.size

    def get_thickness( self ):
        return self.thickness

class Pipe:
    def __init__(self, outer, thickness):
        self.outer     = outer
        self.thickness = thickness

    def get_outer_diameter( self ):
        return self.outer

    def get_inner_diameter( self ):
        return self.outer - 2.0 * self.thickness

class Branch:

    def __init__( self, frange, pipe, r, theta, phi ):
    #def __init__( self, frange, pipe, r, phi, theta ):
        self.frange = frange
        self.pipe   = pipe
        self.r      = r
        self.theta  = theta
        self.phi    = phi

    def get_frange( self ):
        return self.frange

    def get_pipe( self ):
        return self.pipe

    def get_r( self ):
        return self.r

    def get_theta( self ):
        return self.theta

    def get_phi( self ):
        return self.phi

class Node:

    def __init__( self, branch_list, x, y, z ):
        self.branch_list = branch_list
        self.x           = x
        self.y           = y
        self.z           = z

    def get_branch_list( self ):
        return self.branch_list

    def get_xyz( self ):
        return [self.x, self.y, self.z]

class Chamber:

    def __init__( self, node_list ):
        self.node_list = node_list

    def get_node_list( self ):
        return self.node_list

#---------------------------------------------------
# Main
#---------------------------------------------------
if __name__ == "__main__":
    main()
