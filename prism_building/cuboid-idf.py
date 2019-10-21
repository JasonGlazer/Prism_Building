import sys
import json
import pprint
import os

from prism_building import Prism_Building
from present import Present


def main():
    #box_perimeter_core("../cuboid-idf-test/box_perimeter_core_100_200_15.idf", 100, 200, 15, 5, True)
    #L_shaped_perimeter_core("../cuboid-idf-test/L_perimeter_core_100_200_15.idf", 100, 200, 45, 45, 15, 5, True)
    #box_simple("../cuboid-idf-test/box_simple_20_40.idf", 20, 40, 1, False)
    #E_shaped("../cuboid-idf-test/E_building.idf", 250, 150, 40, 100, 20, 2, False)
    #Wedge_shaped("../cuboid-idf-test/Wedge.idf", 70, 100, 15, 60, 40, 30, 2, True)

    # some testing related to json files for osw manipulation
    #json_osw_test(0.1)
    #json_osw_test(0.2)
    #json_osw_test(0.3)

    present = Present()
    #present.test_pptx()
    present.test_pptx02()
    present.test_pptx03()

    #prism = Prism_Building()
    #prism.test_object_order()

def box_perimeter_core(file_name, width, depth, zone_depth, number_above_ground_stories, has_basement):
    # the form of the box with perimeter and core zones
    #
    #      b---------c     /\
    #      |\       /|     |
    #      | f-----g |     |
    #      | |     | |    depth
    #      | e-----h |     |
    #      |/       \|     |
    #      a---------d     \/
    #
    #      <--width-->

    if (width - 2 * zone_depth < 1) or (depth - 2 * zone_depth < 1):
        print("width {}, depth {} and zone_depth {} are not consistent.".format(width, depth, zone_depth))

    prism = Prism_Building()

    # exterior wall corners
    prism.add_corner("a", 0, 0)
    prism.add_corner("b", 0, depth)
    prism.add_corner("c", width, depth)
    prism.add_corner("d", width, 0)

    # interior wall corners
    prism.add_corner("e", zone_depth, zone_depth)
    prism.add_corner("f", zone_depth, depth - zone_depth)
    prism.add_corner("g", width - zone_depth, depth - zone_depth)
    prism.add_corner("h", width - zone_depth, zone_depth)

    # exterior walls
    prism.add_exterior_wall("a", "b")
    prism.add_exterior_wall("b", "c")
    prism.add_exterior_wall("c", "d")
    prism.add_exterior_wall("d", "a")

    # interior walls
    prism.add_interior_wall("e", "f")
    prism.add_interior_wall("f", "g")
    prism.add_interior_wall("g", "h")
    prism.add_interior_wall("h", "e")

    prism.add_interior_wall("a", "e")
    prism.add_interior_wall("b", "f")
    prism.add_interior_wall("c", "g")
    prism.add_interior_wall("d", "h")

    # plan zones
    prism.add_plan_zone(["a", "b", "f", "e"])
    prism.add_plan_zone(["b", "c", "g", "f"])
    prism.add_plan_zone(["c", "d", "h", "g"])
    prism.add_plan_zone(["d", "a", "e", "h"])
    prism.add_plan_zone(["e", "f", "g", "h"])

    prism.number_of_above_grade_stories = number_above_ground_stories
    prism.has_basement = has_basement

    prism.add_occupancy_types("default",10.76,"BLDG_LIGHT_SCH",10.76,"BLDG_EQUIP_SCH",18.58,"BLDG_OCC_SCH")
    prism.add_hvac_types("default",'Furnace_DX',3.0,0.8)

    prism.create_idf(file_name)

def L_shaped_perimeter_core(file_name, width, depth, end1, end2, zone_depth, number_above_ground_stories, has_basement):

    #      <----end1---->
    #
    #      b------------c                 /\
    #      |\          /|                  |
    #      | g--------h |                  |
    #      | |        | |                  |
    #      | |        | |                  |
    #      | |        | d---------e  /\   depth
    #      | |        |/         /|   |    |
    #      | |        i---------j |   |    |
    #      | |    /              | |  end2  |
    #      | l------------------k |   |    |
    #      |/                    \|   |    |
    #      a----------------------f   \/   \/
    #
    #      <---------width-------->

    if (width - end1 < 1) or (depth - end2 < 1):
        print("width {}, depth {}, end1 {}, and end2 {} are not consistant".format(width, depth, end1, end2))
    if (end1 - 2 * zone_depth < 1) or (end2 - 2 * zone_depth < 1):
        print("end1 {}, end2 {} and zone_depth {} are not consistant".format(end1, end2, zone_depth))

    prism = Prism_Building()

    prism.add_corner("a", 0, 0)
    prism.add_corner("b", 0, depth)
    prism.add_corner("c", end1, depth)
    prism.add_corner("d", end1, end2)
    prism.add_corner("e", width, end2)
    prism.add_corner("f", width, 0)
    prism.add_corner("g", zone_depth, depth - zone_depth)
    prism.add_corner("h", end1 - zone_depth, depth - zone_depth)
    prism.add_corner("i", end1 - zone_depth, end2 - zone_depth)
    prism.add_corner("j", width - zone_depth, end2 - zone_depth)
    prism.add_corner("k", width - zone_depth, zone_depth)
    prism.add_corner("l", zone_depth, zone_depth)

    prism.add_exterior_wall("a", "b")
    prism.add_exterior_wall("b", "c")
    prism.add_exterior_wall("c", "d")
    prism.add_exterior_wall("d", "e")
    prism.add_exterior_wall("e", "f")
    prism.add_exterior_wall("f", "a")

    prism.add_interior_wall("g", "h")
    prism.add_interior_wall("h", "i")
    prism.add_interior_wall("i", "j")
    prism.add_interior_wall("j", "k")
    prism.add_interior_wall("k", "l")
    prism.add_interior_wall("l", "g")

    prism.add_interior_wall("a", "l")
    prism.add_interior_wall("b", "g")
    prism.add_interior_wall("c", "h")
    prism.add_interior_wall("d", "i")
    prism.add_interior_wall("e", "j")
    prism.add_interior_wall("f", "k")

    prism.add_interior_wall("i", "l") #subdivide the interior so convex

    prism.add_plan_zone(["a", "b", "g", "l"])
    prism.add_plan_zone(["b", "c", "h", "g"])
    prism.add_plan_zone(["c", "d", "i", "h"])
    prism.add_plan_zone(["d", "e", "j", "i"])
    prism.add_plan_zone(["e", "f", "k", "j"])
    prism.add_plan_zone(["l", "k", "f", "a"])

    # interior zone is split in two so they are convex
    prism.add_plan_zone(["l", "g", "h", "i"])
    prism.add_plan_zone(["i", "j", "k", "l"])

    prism.number_of_above_grade_stories = number_above_ground_stories
    prism.has_basement = has_basement

    prism.add_occupancy_types("default",10.76,"BLDG_LIGHT_SCH",10.76,"BLDG_EQUIP_SCH",18.58,"BLDG_OCC_SCH")
    prism.add_hvac_types("default",'IdealLoadsAirSystem', 1, 1)

    prism.create_idf(file_name)

def box_simple(file_name, width, depth, number_above_ground_stories, has_basement):

    #
    #      b---------c     /\
    #      |         |     |
    #      |         |     |
    #      |         |    depth
    #      |         |     |
    #      |         |     |
    #      a---------d     \/
    #
    #      <--width-->
    #
    prism = Prism_Building()

    prism.add_corner("a", 0, 0)
    prism.add_corner("b", 0, depth)
    prism.add_corner("c", width, depth)
    prism.add_corner("d", width, 0)

    prism.add_exterior_wall("a", "b")
    prism.add_exterior_wall("b", "c")
    prism.add_exterior_wall("c", "d")
    prism.add_exterior_wall("d", "a")

    prism.add_plan_zone(["a", "b", "c", "d"])

    prism.number_of_above_grade_stories = number_above_ground_stories
    prism.has_basement = has_basement

    prism.add_occupancy_types("default",10.76,"BLDG_LIGHT_SCH",10.76,"BLDG_EQUIP_SCH",18.58,"BLDG_OCC_SCH")
    prism.add_hvac_types("default",'Furnace_DX',3.0,0.8)

    prism.create_idf(file_name)

def E_shaped(file_name, width, depth, end, wing, last, number_above_ground_stories, has_basement):

    #    <--end-->       <--end-->       <--end-->
    #
    #    a5--b5--c5      d5--e5--f5      g5--h5--i5    /\    /\    /\
    #    |   | X |       |   | X |       |   | X |     |     |     |
    #    |   |   |       |   |   |       |   |   |     last  |     |
    #    a4--b4--c4      d4--e4--f4      g4--h4--i4    \/    |     |
    #    |   |   |       |   |   |       |   |   |          wing   |
    #    |   |   |       |   |   |       |   |   |           |     |
    #    |   | X |       |   | X |       |   | X |           |     |
    #    |   |   |       |   |   |       |   |   |           |    depth
    #    |   |   |       |   |   |       |   |   |           |     |
    #    a3--b3--c3------d3--e3--f3------g3--h3--i3          \/    |
    #    |       |           |           |    X  |                 |
    #    |       |           |           |       |                 |
    #    a2------c2----------e2----------g2------i2                |
    #    |       |           |           |   X   |                 |
    #    |       |           |           |       |                 |
    #    a1------c1----------e1----------g1------i1                \/
    #
    #    <-------------width------------------->
    #

    prism = Prism_Building()

    prism.add_corner("a1", 0, 0)
    prism.add_corner("a2", 0, (depth - wing) / 2)
    prism.add_corner("a3", 0, depth - wing)
    prism.add_corner("a4", 0, depth - last)
    prism.add_corner("a5", 0, depth)

    prism.add_corner("b3", end / 2, depth - wing)
    prism.add_corner("b4", end / 2, depth - last)
    prism.add_corner("b5", end / 2, depth)

    prism.add_corner("c1", end, 0)
    prism.add_corner("c2", end, (depth - wing) / 2)
    prism.add_corner("c3", end, depth - wing)
    prism.add_corner("c4", end, depth - last)
    prism.add_corner("c5", end, depth)

    prism.add_corner("d3", width / 2 - end / 2, depth - wing)
    prism.add_corner("d4", width / 2 - end / 2, depth - last)
    prism.add_corner("d5", width / 2 - end / 2, depth)

    prism.add_corner("e1", width / 2, 0)
    prism.add_corner("e2", width / 2, (depth - wing) / 2)
    prism.add_corner("e3", width / 2, depth - wing)
    prism.add_corner("e4", width / 2, depth - last)
    prism.add_corner("e5", width / 2, depth)

    prism.add_corner("f3", width / 2 + end / 2, depth - wing)
    prism.add_corner("f4", width / 2 + end / 2, depth - last)
    prism.add_corner("f5", width / 2 + end / 2, depth)

    prism.add_corner("g1", width - end, 0)
    prism.add_corner("g2", width - end, (depth - wing) / 2)
    prism.add_corner("g3", width - end, depth - wing)
    prism.add_corner("g4", width - end, depth - last)
    prism.add_corner("g5", width - end, depth)

    prism.add_corner("h3", width - end / 2, depth - wing)
    prism.add_corner("h4", width - end / 2, depth - last)
    prism.add_corner("h5", width - end / 2, depth)

    prism.add_corner("i1", width, 0)
    prism.add_corner("i2", width, (depth - wing) / 2)
    prism.add_corner("i3", width, depth - wing)
    prism.add_corner("i4", width, depth - last)
    prism.add_corner("i5", width, depth)


    prism.add_exterior_wall("a1", "a2")
    prism.add_exterior_wall("a2", "a3")
    prism.add_exterior_wall("a3", "a4")
    prism.add_exterior_wall("a4", "a5")

    prism.add_exterior_wall("a5", "b5")
    prism.add_exterior_wall("b5", "c5")

    prism.add_exterior_wall("c5", "c4")
    prism.add_exterior_wall("c4", "c3")

    prism.add_exterior_wall("c3", "d3")

    prism.add_exterior_wall("d3", "d4")
    prism.add_exterior_wall("d4", "d5")

    prism.add_exterior_wall("d5", "e5")
    prism.add_exterior_wall("e5", "f5")

    prism.add_exterior_wall("f5", "f4")
    prism.add_exterior_wall("f4", "f3")

    prism.add_exterior_wall("f3", "g3")

    prism.add_exterior_wall("g3", "g4")
    prism.add_exterior_wall("g4", "g5")

    prism.add_exterior_wall("g5", "h5")
    prism.add_exterior_wall("h5", "i5")

    prism.add_exterior_wall("i5", "i4")
    prism.add_exterior_wall("i4", "i3")
    prism.add_exterior_wall("i3", "i2")
    prism.add_exterior_wall("i2", "i1")
    prism.add_exterior_wall("i1", "g1")

    prism.add_exterior_wall("g1", "e1")
    prism.add_exterior_wall("e1", "c1")
    prism.add_exterior_wall("c1", "a1")


    prism.add_interior_wall("a2", "c2")
    prism.add_interior_wall("c2", "e2")
    prism.add_interior_wall("e2", "g2")
    prism.add_interior_wall("g2", "i2")

    prism.add_interior_wall("a3", "b3")
    prism.add_interior_wall("b3", "c3")
    prism.add_interior_wall("d3", "e3")
    prism.add_interior_wall("e3", "f3")
    prism.add_interior_wall("g3", "h3")
    prism.add_interior_wall("h3", "i3")

    prism.add_interior_wall("a4", "b4")
    prism.add_interior_wall("b4", "c4")
    prism.add_interior_wall("d4", "e4")
    prism.add_interior_wall("e4", "f4")
    prism.add_interior_wall("g4", "h4")
    prism.add_interior_wall("h4", "i4")

    prism.add_interior_wall("b3", "b4")
    prism.add_interior_wall("b4", "b5")

    prism.add_interior_wall("c1", "c2")
    prism.add_interior_wall("c2", "c3")

    prism.add_interior_wall("e1", "e2")
    prism.add_interior_wall("e2", "e3")
    prism.add_interior_wall("e3", "e4")
    prism.add_interior_wall("e4", "e5")

    prism.add_interior_wall("g1", "g2")
    prism.add_interior_wall("g2", "g3")

    prism.add_interior_wall("h3", "h4")
    prism.add_interior_wall("h4", "h5")

    prism.add_plan_zone(["a1", "a2", "c2", "c1"])
    prism.add_plan_zone(["c1", "c2", "e2", "e1"])
    prism.add_plan_zone(["e1", "e2", "g2", "g1"])
    prism.add_plan_zone(["g1", "g2", "i2", "i1"])

    prism.add_plan_zone(["a2", "a3", "b3", "c3", "c2"])
    prism.add_plan_zone(["c2", "c3", "d3", "e3", "e2"])
    prism.add_plan_zone(["e2", "e3", "f3", "g3", "g2"])
    prism.add_plan_zone(["g2", "g3", "h3", "i3", "i2"])

    prism.add_plan_zone(["a3", "a4", "b4", "b3"])
    prism.add_plan_zone(["b3", "b4", "c4", "c3"])
    prism.add_plan_zone(["d3", "d4", "e4", "e3"])
    prism.add_plan_zone(["e3", "e4", "f4", "f3"])
    prism.add_plan_zone(["g3", "g4", "h4", "h3"])
    prism.add_plan_zone(["h3", "h4", "i4", "i3"])

    prism.add_plan_zone(["a4", "a5", "b5", "b4"])
    prism.add_plan_zone(["b4", "b5", "c5", "c4"])
    prism.add_plan_zone(["d4", "d5", "e5", "e4"])
    prism.add_plan_zone(["e4", "e5", "f5", "f4"])
    prism.add_plan_zone(["g4", "g5", "h5", "h4"])
    prism.add_plan_zone(["h4", "h5", "i5", "i4"])

    prism.number_of_above_grade_stories = number_above_ground_stories
    prism.has_basement = has_basement

    prism.add_occupancy_types("default",10.76,"BLDG_LIGHT_SCH",10.76,"BLDG_EQUIP_SCH",18.58,"BLDG_OCC_SCH")
    # prism.add_hvac_types("default",'Furnace_DX',3.0,0.8)
    prism.add_hvac_types("default",'IdealLoadsAirSystem',1,1)

    prism.create_idf(file_name)

def Wedge_shaped(file_name, width, depth, zone_depth, lfdep, rtdep, offset, number_above_ground_stories, has_basement):

    #
    #     <offset>
    #            c                     /\
    #           /|\                    |
    #          / | \                   |
    #         /  |  \                  |
    #        /   h   \                 |
    #       /   / \   \                |
    #  /\  b   /   \   \             depth
    #  |   |\ /     \   \              |
    #  |   | g       \   d      /\     |
    #  |   | |        i/ |      |      |
    # lfdep| |        |  |    rtdep    |
    #  |   | |        |  |      |      |
    #  |   | f--------j  |      |      |
    #  |   |/          \ |      |      |
    #  \/  a-------------e      \/     \/
    #
    #      <----width---->
    #

    prism = Prism_Building()

    prism.add_corner("a", 0, 0)
    prism.add_corner("b", 0, lfdep)
    prism.add_corner("c", offset, depth)
    prism.add_corner("d", width, rtdep)
    prism.add_corner("e", width, 0)
    prism.add_corner("f", zone_depth, zone_depth)
    prism.add_corner("g", zone_depth, lfdep - zone_depth / 2)
    prism.add_corner("h", offset, depth - zone_depth)
    prism.add_corner("i", width - zone_depth, rtdep - zone_depth / 2)
    prism.add_corner("j", width - zone_depth, zone_depth)

    prism.add_exterior_wall("a", "b")
    prism.add_exterior_wall("b", "c")
    prism.add_exterior_wall("c", "d")
    prism.add_exterior_wall("d", "e")
    prism.add_exterior_wall("e", "a")

    prism.add_interior_wall("f", "g")
    prism.add_interior_wall("g", "h")
    prism.add_interior_wall("h", "i")
    prism.add_interior_wall("i", "j")
    prism.add_interior_wall("j", "f")
    prism.add_interior_wall("a", "f")
    prism.add_interior_wall("b", "g")
    prism.add_interior_wall("c", "h")
    prism.add_interior_wall("d", "i")
    prism.add_interior_wall("e", "j")

    prism.add_plan_zone(["a", "b", "g", "f"])
    prism.add_plan_zone(["b", "c", "h", "g"])
    prism.add_plan_zone(["c", "d", "i", "h"])
    prism.add_plan_zone(["d", "e", "j", "i"])
    prism.add_plan_zone(["j", "e", "a", "f"])
    prism.add_plan_zone(["f", "g", "h", "i", "j"])

    prism.number_of_above_grade_stories = number_above_ground_stories
    prism.has_basement = has_basement

    prism.add_occupancy_types("default",10.76,"BLDG_LIGHT_SCH",10.76,"BLDG_EQUIP_SCH",18.58,"BLDG_OCC_SCH")
    prism.add_hvac_types("default",'Furnace_DX',3.0,0.8)

    prism.create_idf(file_name)

def json_osw_test(wwr):
    pp = pprint.PrettyPrinter(indent=4)
    with open('D:/projects/SBIR SimArchImag/5 SimpleBox/os-test/emptyCLI/workflow-min.osw') as f:
        data = json.load(f)
        #print(data)
        #pp.pprint(data)
        steps = data['steps']
        for step in steps:
            if step['measure_dir_name'] == "AddRemoveOrReplaceWindowsCopy":
                #print(step)
                arguments = step['arguments']
                #print(arguments['wwr'])
                arguments['wwr']  = wwr
        try:
            os.mkdir('D:/projects/SBIR SimArchImag/5 SimpleBox/os-test/emptyCLI/{}'.format(wwr))
        except FileExistsError:
            print('directory already exists')
        with open('D:/projects/SBIR SimArchImag/5 SimpleBox/os-test/emptyCLI/{}/workflow-min-{}.osw'.format(wwr, wwr),'w') as o:
            json.dump(data, o, indent=3, sort_keys=True)



if __name__ == '__main__':
    sys.exit(main())
