from collections import OrderedDict

from corner import Corner
from segment import Segment
from eppy import modeleditor
from eppy.modeleditor import IDF


class Prism_Building():

    def __init__(self):
        self.corners = {}
        self.exterior_walls = {}
        self.interior_walls = {}
        self.plan_zones = {}
        self.occupancy_types = OrderedDict()
        self.hvac_types = OrderedDict()

        self.number_of_above_grade_stories = 1
        self.has_basement = True
        self.typical_window_width = 3
        self.typical_window_height = 5
        self.window_wall_ratio = 0.2
        self.floor_to_floor_height = 5

        self.plan_zone_wrapped_strings = {}
        self.zone_names = []

    def __str__(self):
        return(str(self.corners))

    def add_corner(self, name, x, y):
        self.corners[name] = Corner(x, y)

    def make_name_sorted_order(self, start_name, end_name):
        if start_name > end_name:
            name = "{}_{}".format(end_name, start_name)
        else:
            name = "{}_{}".format(start_name, end_name)
        return name

    def add_exterior_wall(self,start_name, end_name):
        name = self.make_name_sorted_order(start_name, end_name)
        self.exterior_walls[name] = Segment(self.corners[start_name], self.corners[end_name])

    def add_interior_wall(self,start_name,end_name):
        name = self.make_name_sorted_order(start_name, end_name)
        self.interior_walls[name] = Segment(self.corners[start_name], self.corners[end_name])

    def add_plan_zone(self, list_of_corners_cw):
        name = "_".join(list_of_corners_cw)
        self.plan_zones[name] = list_of_corners_cw

    def add_occupancy_types(self,zone_pattern_string, lighting_density, lighting_sch_name, plug_power_density, plug_power_sch_name, occupant_density, occupant_sch_name):
        # if zone_pattern_string is "default" than it acts as the default
        self.occupancy_types[zone_pattern_string] = (lighting_density, lighting_sch_name, plug_power_density, plug_power_sch_name, occupant_density, occupant_sch_name)

    def add_hvac_types(self,zone_pattern_string, hvac_type, cooling_COP, heating_efficiency):
        # if zone_pattern_string is "default" than it acts as the default
        # note the only hvac_type supported currently is Furnace_DX
        self.hvac_types[zone_pattern_string] = (hvac_type, cooling_COP, heating_efficiency)

    def plan_zone_adjacent_to_wall(self, name_of_wall):
        reversed_name = self.reverse_name_of_wall(name_of_wall)
        for name_of_zone, corners in self.plan_zones.items():
            wrapped_zone_string = self.plan_zone_wrapped_strings[name_of_zone]
            if name_of_wall in wrapped_zone_string:
                return name_of_zone
            if reversed_name in wrapped_zone_string:
                return name_of_zone
        return ""

    def list_plan_zones_adjacent_to_wall(self,name_of_wall):
        list_of_plan_zones = []
        # first find the zone with the name in normal order (the primary zone)
        for name_of_zone, corners in self.plan_zones.items():
            wrapped_zone_string = self.plan_zone_wrapped_strings[name_of_zone]
            if name_of_wall in wrapped_zone_string:
                list_of_plan_zones.append(name_of_zone)
        # second find the zone with the name in reversed order (the secondary zone)
        reversed_name = self.reverse_name_of_wall(name_of_wall)
        for name_of_zone, corners in self.plan_zones.items():
            wrapped_zone_string = self.plan_zone_wrapped_strings[name_of_zone]
            if reversed_name in wrapped_zone_string:
                list_of_plan_zones.append(name_of_zone)
        return list_of_plan_zones

    def create_wrapped_plan_zone_strings(self):
        for name_of_zone, corners in self.plan_zones.items():
            self.plan_zone_wrapped_strings[name_of_zone] = name_of_zone + "_" + corners[0]

    def reverse_name_of_wall(self, orig):
        first, second = orig.split('_')
        return "{}_{}".format(second, first)

    def create_idf(self, file_name):

        # iddfile = "C:/EnergyPlusV8-9-0/Energy+.idd"
        # smallfile = "C:/eppy0-5-48/eppy/resources/idffiles/V8_9/smallfile.idf"

        iddfile = "C:/EnergyPlusV9-1-0/Energy+.idd"
        smallfile = "./startfile.idf"

        self.create_wrapped_plan_zone_strings()
        IDF.setiddname(iddfile)

        idf = IDF(smallfile)
        # idf.printidf()

        idf_zones = idf.idfobjects['Zone'.upper()]
        idf_surfaces = idf.idfobjects['BuildingSurface:Detailed'.upper()]

        # basement
        if self.has_basement:
            for name, corners in self.plan_zones.items():
                idf.newidfobject('Zone'.upper())
                idf_zones[-1].Name = "Basement_Zone_" + name
                self.zone_names.append( idf_zones[-1].Name )
            self.write_idf_ext_surfaces_for_level(idf, 'Basement_',
                                                      0, -self.floor_to_floor_height)
            self.write_idf_int_surfaces_for_level(idf, 'Basement_',
                                                      0, -self.floor_to_floor_height)
            self.write_idf_interior_ceiling(idf,'Basement_', 0)
            self.write_idf_foundation(idf,'Basement_', -self.floor_to_floor_height)

        # always do the lower floor
        for name, corners in self.plan_zones.items():
            idf.newidfobject('Zone'.upper())
            idf_zones[-1].Name = "Lower_Zone_" + name
            self.zone_names.append(idf_zones[-1].Name)
        self.write_idf_ext_surfaces_for_level(idf, 'Lower_',
                                              self.floor_to_floor_height, 0)
        self.write_idf_int_surfaces_for_level(idf, 'Lower_',
                                              self.floor_to_floor_height, 0)
        if self.number_of_above_grade_stories == 1:
            self.write_idf_roof(idf,'Lower_', self.floor_to_floor_height)
        else:
            self.write_idf_interior_ceiling(idf,'Lower_', self.floor_to_floor_height)
        if self.has_basement:
            self.write_idf_interior_floor(idf, 'Lower_', 0)
        else:
            self.write_idf_foundation(idf,'Lower_', 0)

        # middle floors
        if self.number_of_above_grade_stories >= 3:
            for name, corners in self.plan_zones.items():
                idf.newidfobject('Zone'.upper())
                idf_zones[-1].Name = "Middle_Zone_" + name
                self.zone_names.append( idf_zones[-1].Name )
                idf_zones[-1].Multiplier = self.number_of_above_grade_stories - 2
            height_of_ceiling = 0.5 * self.floor_to_floor_height * self.number_of_above_grade_stories + 0.5 * self.floor_to_floor_height
            height_of_floor = 0.5 * self.floor_to_floor_height * self.number_of_above_grade_stories - 0.5 * self.floor_to_floor_height
            self.write_idf_ext_surfaces_for_level(idf, 'Middle_', height_of_ceiling, height_of_floor)
            self.write_idf_int_surfaces_for_level(idf, 'Middle_', height_of_ceiling, height_of_floor)
            self.write_idf_interior_ceiling(idf,'Middle_', height_of_ceiling)
            self.write_idf_interior_floor(idf, 'Middle_', height_of_floor)

        # top floor
        if self.number_of_above_grade_stories >= 2:
            for name, corners in self.plan_zones.items():
                idf.newidfobject('Zone'.upper())
                idf_zones[-1].Name = "Top_Zone_" + name
                self.zone_names.append(idf_zones[-1].Name)
            height_of_ceiling = self.floor_to_floor_height * self.number_of_above_grade_stories
            height_of_floor = self.floor_to_floor_height * (self.number_of_above_grade_stories - 1)
            self.write_idf_ext_surfaces_for_level(idf, 'Top_', height_of_ceiling, height_of_floor)
            self.write_idf_int_surfaces_for_level(idf, 'Top_',  height_of_ceiling, height_of_floor)
            self.write_idf_roof(idf,'Top_', height_of_ceiling)
            self.write_idf_interior_floor(idf, 'Top_', height_of_floor)

#        print(idf_surfaces[0].fieldnames)
        self.apply_occupany_types(idf)
        self.apply_hvac_types(idf)

        idf.saveas(file_name)

    def write_idf_vert_surface(self, idf, name, type, cons, zone_name, out_boundary, out_boundary_object, sun_exposure, wind_exposure, wall_segment, z_top, z_bottom):
        idf_surfaces = idf.idfobjects['BuildingSurface:Detailed'.upper()]
        idf.newidfobject('BuildingSurface:Detailed'.upper())
        idf_surfaces[-1].Name =  name
        idf_surfaces[-1].Surface_Type = type
        idf_surfaces[-1].Construction_Name = cons
        idf_surfaces[-1].Zone_Name = zone_name
        idf_surfaces[-1].Outside_Boundary_Condition = out_boundary
        idf_surfaces[-1].Outside_Boundary_Condition_Object = out_boundary_object
        idf_surfaces[-1].Sun_Exposure = sun_exposure
        idf_surfaces[-1].Wind_Exposure = wind_exposure
        idf_surfaces[-1].Vertex_1_Xcoordinate = wall_segment.end.x
        idf_surfaces[-1].Vertex_1_Ycoordinate = wall_segment.end.y
        idf_surfaces[-1].Vertex_1_Zcoordinate = z_top
        idf_surfaces[-1].Vertex_2_Xcoordinate = wall_segment.end.x
        idf_surfaces[-1].Vertex_2_Ycoordinate = wall_segment.end.y
        idf_surfaces[-1].Vertex_2_Zcoordinate = z_bottom
        idf_surfaces[-1].Vertex_3_Xcoordinate = wall_segment.start.x
        idf_surfaces[-1].Vertex_3_Ycoordinate = wall_segment.start.y
        idf_surfaces[-1].Vertex_3_Zcoordinate = z_bottom
        idf_surfaces[-1].Vertex_4_Xcoordinate = wall_segment.start.x
        idf_surfaces[-1].Vertex_4_Ycoordinate = wall_segment.start.y
        idf_surfaces[-1].Vertex_4_Zcoordinate = z_top

    def write_idf_horiz_surface(self, idf, name, type, cons, zone_name, out_boundary, out_boundary_object, sun_exposure, wind_exposure, list_of_corners_cw, make_ccw, z_height):
        idf_surfaces = idf.idfobjects['BuildingSurface:Detailed'.upper()]
        idf.newidfobject('BuildingSurface:Detailed'.upper())
        reordered_corner_names = list_of_corners_cw.copy()
        if make_ccw:
            reordered_corner_names.reverse()
        idf_surfaces[-1].Name =  name
        idf_surfaces[-1].Surface_Type = type
        idf_surfaces[-1].Construction_Name = cons
        idf_surfaces[-1].Zone_Name = zone_name
        idf_surfaces[-1].Outside_Boundary_Condition = out_boundary
        idf_surfaces[-1].Outside_Boundary_Condition_Object = out_boundary_object
        idf_surfaces[-1].Sun_Exposure = sun_exposure
        idf_surfaces[-1].Wind_Exposure = wind_exposure
        idf_surfaces[-1].Vertex_1_Xcoordinate = self.corners[reordered_corner_names[0]].x
        idf_surfaces[-1].Vertex_1_Ycoordinate = self.corners[reordered_corner_names[0]].y
        idf_surfaces[-1].Vertex_1_Zcoordinate = z_height
        idf_surfaces[-1].Vertex_2_Xcoordinate = self.corners[reordered_corner_names[1]].x
        idf_surfaces[-1].Vertex_2_Ycoordinate = self.corners[reordered_corner_names[1]].y
        idf_surfaces[-1].Vertex_2_Zcoordinate = z_height
        idf_surfaces[-1].Vertex_3_Xcoordinate = self.corners[reordered_corner_names[2]].x
        idf_surfaces[-1].Vertex_3_Ycoordinate = self.corners[reordered_corner_names[2]].y
        idf_surfaces[-1].Vertex_3_Zcoordinate = z_height
        idf_surfaces[-1].Vertex_4_Xcoordinate = self.corners[reordered_corner_names[3]].x
        idf_surfaces[-1].Vertex_4_Ycoordinate = self.corners[reordered_corner_names[3]].y
        idf_surfaces[-1].Vertex_4_Zcoordinate = z_height
        if len(reordered_corner_names) > 4:
            idf_surfaces[-1].Vertex_5_Xcoordinate = self.corners[reordered_corner_names[4]].x
            idf_surfaces[-1].Vertex_5_Ycoordinate = self.corners[reordered_corner_names[4]].y
            idf_surfaces[-1].Vertex_5_Zcoordinate = z_height
        if len(reordered_corner_names) > 5:
            idf_surfaces[-1].Vertex_6_Xcoordinate = self.corners[reordered_corner_names[5]].x
            idf_surfaces[-1].Vertex_6_Ycoordinate = self.corners[reordered_corner_names[5]].y
            idf_surfaces[-1].Vertex_6_Zcoordinate = z_height

    def write_idf_ext_surfaces_for_level(self, idf, vertical_position_name, z_top, z_bottom):
        for name, wall_segment in self.exterior_walls.items():
            associated_zone_name = self.plan_zone_adjacent_to_wall(name)
            if vertical_position_name == 'Basement_':
                cons = 'vert-concrete'
                out_boundary = 'Ground'
                sun_exposure =  'NoSun'
                wind_exposure = 'NoWind'
            else:
                cons = "Steel Frame Non-res Ext Wall"
                out_boundary = 'Outdoors'
                sun_exposure = 'SunExposed'
                wind_exposure = 'WindExposed'
            self.write_idf_vert_surface(idf, vertical_position_name + "Ext_Wall_" + name, "Wall", cons,
                                   vertical_position_name + "Zone_" + associated_zone_name, out_boundary, "",
                                   sun_exposure, wind_exposure, wall_segment, z_top, z_bottom)

    def write_idf_int_surfaces_for_level(self, idf, vertical_position_name, z_top, z_bottom):
        cons = 'int-walls'
        out_boundary = 'Zone'
        sun_exposure = 'NoSun'
        wind_exposure = 'NoWind'
        for name, wall_segment in self.interior_walls.items():
            adjacent_zone_names = self.list_plan_zones_adjacent_to_wall(name)
            if len(adjacent_zone_names) == 2:
                self.write_idf_vert_surface(idf, vertical_position_name + "Int_Wall_" + name, "Wall", cons,
                                       vertical_position_name + "Zone_" + adjacent_zone_names[0],
                                       out_boundary, vertical_position_name + "Zone_" + adjacent_zone_names[1],
                                       sun_exposure, wind_exposure, wall_segment, z_top, z_bottom)
            elif len(adjacent_zone_names) <= 1 or len(adjacent_zone_names) > 2:
                print('unexpected number {} of adjacent zones for wall {} including: '.format(len(adjacent_zone_names), name))
                print(adjacent_zone_names)


    def write_idf_roof(self, idf, vertical_position_name, z_height):
        for name, corners in self.plan_zones.items():
            self.write_idf_horiz_surface(idf, vertical_position_name + 'Roof_' + name, "Roof", "IEAD Non-res Roof",
                                         vertical_position_name + "Zone_" + name, "Outdoors", "", 'SunExposed',
                                         'WindExposed', corners, True, z_height)

    def write_idf_foundation(self, idf, vertical_position_name, z_height):
        for name, corners in self.plan_zones.items():
            self.write_idf_horiz_surface(idf, vertical_position_name + 'Foundation_' + name, "Floor", "ext-slab",
                                         vertical_position_name + "Zone_" + name, "Ground", "", 'NoSun',
                                         'NoWind', corners, False, z_height)

    def write_idf_interior_floor(self, idf, vertical_position_name, z_height):
        for name, corners in self.plan_zones.items():
            self.write_idf_horiz_surface(idf, vertical_position_name + 'IntFloor_' + name, "Floor", "int-floor",
                                         vertical_position_name + "Zone_" + name, "Adiabatic", "", 'NoSun',
                                         'NoWind', corners, False, z_height)

    def write_idf_interior_ceiling(self, idf, vertical_position_name, z_height):
        for name, corners in self.plan_zones.items():
            self.write_idf_horiz_surface(idf, vertical_position_name + 'IntCeil_' + name, "Ceiling", "int-floor",
                                         vertical_position_name + "Zone_" + name, "Adiabatic", "", 'NoSun',
                                         'NoWind', corners, True, z_height)

    def apply_occupany_types(self, idf):
        if "default" in self.occupancy_types:
            lighting_density, lighting_sch_name, plug_power_density, plug_power_sch_name, occupant_density, occupant_sch_name = self.occupancy_types["default"]
        elif "" in self.occupancy_types:
            lighting_density, lighting_sch_name, plug_power_density, plug_power_sch_name, occupant_density, occupant_sch_name = self.occupancy_types[""]
        else:
            print("no default found for occupancy type")
        for zone_name in self.zone_names:
            found, matching_occupancy = self.first_dictionary_substring_match(self.occupancy_types, zone_name)
            if found:
                lighting_density, lighting_sch_name, plug_power_density, plug_power_sch_name, occupant_density, occupant_sch_name = self.occupancy_types[matching_occupancy]
            self.write_idf_lighting(idf, zone_name, lighting_density, lighting_sch_name)
            self.write_idf_electric_equipment(idf, zone_name, plug_power_density, plug_power_sch_name)
            self.write_idf_people(idf, zone_name, occupant_density, occupant_sch_name)
            # print(zone_name)

    def first_dictionary_substring_match(self,dictionary,search_string):
        for key in dictionary:
            if search_string.lower() in key.lower():
                return True,key
        else:
            return False,""


    def write_idf_lighting(self, idf, zone_name, density, schedule_name):
        idf_lights = idf.idfobjects['Lights'.upper()]
        idf.newidfobject('Lights'.upper())
        # print(idf_lights[-1].fieldnames)
        idf_lights[-1].Name = zone_name + "_Lights"
        idf_lights[-1].Zone_or_ZoneList_Name = zone_name
        idf_lights[-1].Schedule_Name = schedule_name
        idf_lights[-1].Design_Level_Calculation_Method = 'Watts/Area'
        idf_lights[-1].Lighting_Level = ''
        idf_lights[-1].Watts_per_Zone_Floor_Area = density
        idf_lights[-1].Watts_per_Person = ''
        idf_lights[-1].Return_Air_Fraction = 0
        idf_lights[-1].Fraction_Radiant = 0.7
        idf_lights[-1].Fraction_Visible = 0.2
        idf_lights[-1].Fraction_Replaceable = 1
        idf_lights[-1].EndUse_Subcategory = 'GeneralLighting'
        idf_lights[-1].Return_Air_Fraction_Calculated_from_Plenum_Temperature = 'No'

    def write_idf_electric_equipment(self, idf, zone_name, density, schedule_name):
        idf_elec_eq = idf.idfobjects['ElectricEquipment'.upper()]
        idf.newidfobject('ElectricEquipment'.upper())
        # print(idf_elec_eq[-1].fieldnames)
        idf_elec_eq[-1].Name = zone_name + "_Equip"
        idf_elec_eq[-1].Zone_or_ZoneList_Name = zone_name
        idf_elec_eq[-1].Schedule_Name = schedule_name
        idf_elec_eq[-1].Design_Level_Calculation_Method = 'Watts/Area'
        idf_elec_eq[-1].Design_Level = ''
        idf_elec_eq[-1].Watts_per_Zone_Floor_Area = density
        idf_elec_eq[-1].Watts_per_Person = ''
        idf_elec_eq[-1].Fraction_Latent = 0
        idf_elec_eq[-1].Fraction_Radiant = 0.5
        idf_elec_eq[-1].Fraction_Lost = 0
        idf_elec_eq[-1].EndUse_Subcategory = 'MiscPlug'

    def write_idf_people(self, idf, zone_name, density, schedule_name):
        idf_people = idf.idfobjects['People'.upper()]
        idf.newidfobject('People'.upper())
        # print(idf_people[-1].fieldnames)
        idf_people[-1].Name = zone_name + "_People"
        idf_people[-1].Zone_or_ZoneList_Name = zone_name
        idf_people[-1].Number_of_People_Schedule_Name = schedule_name
        idf_people[-1].Number_of_People_Calculation_Method = 'Area/Person'
        idf_people[-1].Number_of_People = ''
        idf_people[-1].People_per_Zone_Floor_Area = ''
        idf_people[-1].Zone_Floor_Area_per_Person = density
        idf_people[-1].Fraction_Radiant = 0.3
        idf_people[-1].Sensible_Heat_Fraction = 'AUTOCALCULATE'
        idf_people[-1].Activity_Level_Schedule_Name = 'ACTIVITY_SCH'

    def apply_hvac_types(self, idf):
        if "default" in self.hvac_types:
            hvac_type, cooling_COP, heating_efficiency = self.hvac_types["default"]
        elif "" in self.hvac_types:
            hvac_type, cooling_COP, heating_efficiency = self.hvac_types[""]
        else:
            print("no default found for HVAC type")
        for zone_name in self.zone_names:
            found, matching_occupancy = self.first_dictionary_substring_match(self.hvac_types, zone_name)
            if found:
                hvac_type, cooling_COP, heating_efficiency = self.occupancy_types[matching_occupancy]
            if hvac_type == 'Furnace_DX':
                self.write_idf_zone_unitary(idf, zone_name)
                self.write_idf_system_unitary(idf, zone_name, cooling_COP, heating_efficiency)
            elif hvac_type == 'IdealLoadsAirSystem':
                self.write_idf_zone_ideal_air(idf, zone_name)

    def write_idf_zone_unitary(self, idf, zone_name):
        idf_zone_unitary = idf.idfobjects['HVACTemplate:Zone:Unitary'.upper()]
        idf.newidfobject('HVACTemplate:Zone:Unitary'.upper())
        # print(idf_zone_unitary[-1].fieldnames)
        idf_zone_unitary[-1].Zone_Name = zone_name
        idf_zone_unitary[-1].Template_Unitary_System_Name = zone_name + "_SystemUnitary"
        idf_zone_unitary[-1].Template_Thermostat_Name = 'All Zones'
        idf_zone_unitary[-1].Supply_Air_Maximum_Flow_Rate = 'autosize'
        idf_zone_unitary[-1].Zone_Heating_Sizing_Factor = ''
        idf_zone_unitary[-1].Zone_Cooling_Sizing_Factor = ''
        idf_zone_unitary[-1].Outdoor_Air_Method = 'flow/person'
        idf_zone_unitary[-1].Outdoor_Air_Flow_Rate_per_Person = 0.00944
        idf_zone_unitary[-1].Outdoor_Air_Flow_Rate_per_Zone_Floor_Area = 0
        idf_zone_unitary[-1].Outdoor_Air_Flow_Rate_per_Zone = 0
        idf_zone_unitary[-1].Supply_Plenum_Name = ''
        idf_zone_unitary[-1].Return_Plenum_Name = ''
        idf_zone_unitary[-1].Baseboard_Heating_Type = 'None'
        idf_zone_unitary[-1].Baseboard_Heating_Availability_Schedule_Name = ''
        idf_zone_unitary[-1].Baseboard_Heating_Capacity = ''
        idf_zone_unitary[-1].Zone_Cooling_Design_Supply_Air_Temperature_Input_Method = 'SystemSupplyAirTemperature'
        idf_zone_unitary[-1].Zone_Cooling_Design_Supply_Air_Temperature = ''
        idf_zone_unitary[-1].Zone_Cooling_Design_Supply_Air_Temperature_Difference = ''
        idf_zone_unitary[-1].Zone_Heating_Design_Supply_Air_Temperature_Input_Method = 'SystemSupplyAirTemperature'
        idf_zone_unitary[-1].Zone_Heating_Design_Supply_Air_Temperature = ''
        idf_zone_unitary[-1].Zone_Heating_Design_Supply_Air_Temperature_Difference = ''

    def write_idf_system_unitary(self, idf, zone_name, cooling_COP, heating_efficiency):
        idf_sys_unitary = idf.idfobjects['HVACTemplate:System:Unitary'.upper()]
        idf.newidfobject('HVACTemplate:System:Unitary'.upper())
        #print(idf_sys_unitary[-1].fieldnames)
        idf_sys_unitary[-1].Name = zone_name + "_SystemUnitary"
        idf_sys_unitary[-1].System_Availability_Schedule_Name = 'AlwaysOn'
        idf_sys_unitary[-1].Control_Zone_or_Thermostat_Location_Name = zone_name
        idf_sys_unitary[-1].Supply_Fan_Maximum_Flow_Rate = 'autosize'
        idf_sys_unitary[-1].Supply_Fan_Operating_Mode_Schedule_Name = 'FanAvailSched'
        idf_sys_unitary[-1].Supply_Fan_Total_Efficiency = 0.7
        idf_sys_unitary[-1].Supply_Fan_Delta_Pressure = 600
        idf_sys_unitary[-1].Supply_Fan_Motor_Efficiency = 0.9
        idf_sys_unitary[-1].Supply_Fan_Motor_in_Air_Stream_Fraction = 1
        idf_sys_unitary[-1].Cooling_Coil_Type = 'SingleSpeedDX'
        idf_sys_unitary[-1].Cooling_Coil_Availability_Schedule_Name = ''
        idf_sys_unitary[-1].Cooling_Design_Supply_Air_Temperature = 14
        idf_sys_unitary[-1].Cooling_Coil_Gross_Rated_Total_Capacity = 'autosize'
        idf_sys_unitary[-1].Cooling_Coil_Gross_Rated_Sensible_Heat_Ratio = 'autosize'
        idf_sys_unitary[-1].Cooling_Coil_Gross_Rated_COP = cooling_COP
        idf_sys_unitary[-1].Heating_Coil_Type = 'Gas'
        idf_sys_unitary[-1].Heating_Coil_Availability_Schedule_Name = ''
        idf_sys_unitary[-1].Heating_Design_Supply_Air_Temperature = 50
        idf_sys_unitary[-1].Heating_Coil_Capacity = 'autosize'
        idf_sys_unitary[-1].Gas_Heating_Coil_Efficiency = heating_efficiency
        idf_sys_unitary[-1].Gas_Heating_Coil_Parasitic_Electric_Load = 0
        idf_sys_unitary[-1].Maximum_Outdoor_Air_Flow_Rate = 'autosize'
        idf_sys_unitary[-1].Minimum_Outdoor_Air_Flow_Rate = 'autosize'
        idf_sys_unitary[-1].Minimum_Outdoor_Air_Schedule_Name = 'Min OA Sched'
        idf_sys_unitary[-1].Economizer_Type = 'DifferentialDryBulb'
        idf_sys_unitary[-1].Economizer_Lockout = 'NoLockout'
        idf_sys_unitary[-1].Economizer_Upper_Temperature_Limit = 19
        idf_sys_unitary[-1].Economizer_Lower_Temperature_Limit = ''
        idf_sys_unitary[-1].Economizer_Upper_Enthalpy_Limit = ''
        idf_sys_unitary[-1].Economizer_Maximum_Limit_Dewpoint_Temperature = ''
        idf_sys_unitary[-1].Supply_Plenum_Name = ''
        idf_sys_unitary[-1].Return_Plenum_Name = ''
        idf_sys_unitary[-1].Supply_Fan_Placement = 'BlowThrough'
        idf_sys_unitary[-1].Night_Cycle_Control = 'StayOff'
        idf_sys_unitary[-1].Night_Cycle_Control_Zone_Name = ''
        idf_sys_unitary[-1].Heat_Recovery_Type = 'None'
        idf_sys_unitary[-1].Sensible_Heat_Recovery_Effectiveness = ''
        idf_sys_unitary[-1].Latent_Heat_Recovery_Effectiveness = ''
        idf_sys_unitary[-1].Dehumidification_Control_Type = 'None'
        idf_sys_unitary[-1].Dehumidification_Setpoint = ''
        idf_sys_unitary[-1].Humidifier_Type = 'None'
        idf_sys_unitary[-1].Humidifier_Availability_Schedule_Name = ''
        idf_sys_unitary[-1].Humidifier_Rated_Capacity = ''
        idf_sys_unitary[-1].Humidifier_Rated_Electric_Power = ''
        idf_sys_unitary[-1].Humidifier_Control_Zone_Name = ''
        idf_sys_unitary[-1].Humidifier_Setpoint = ''
        idf_sys_unitary[-1].Return_Fan = ''
        idf_sys_unitary[-1].Return_Fan_Total_Efficiency = ''
        idf_sys_unitary[-1].Return_Fan_Delta_Pressure = ''
        idf_sys_unitary[-1].Return_Fan_Motor_Efficiency = ''
        idf_sys_unitary[-1].Return_Fan_Motor_in_Air_Stream_Fraction = ''

    def write_idf_zone_ideal_air(self, idf, zone_name):
        obj = idf.newidfobject('HVACTemplate:Zone:IdealLoadsAirSystem'.upper())
        #self.print_field_names(obj)
        obj.Zone_Name = zone_name
        obj.Template_Thermostat_Name = 'All Zones'
        obj.System_Availability_Schedule_Name = ''
        obj.Maximum_Heating_Supply_Air_Temperature = 50.0
        obj.Minimum_Cooling_Supply_Air_Temperature = 13.0
        obj.Maximum_Heating_Supply_Air_Humidity_Ratio = 0.0156
        obj.Minimum_Cooling_Supply_Air_Humidity_Ratio = 0.0077
        obj.Heating_Limit = 'NoLimit'
        obj.Maximum_Heating_Air_Flow_Rate = ''
        obj.Maximum_Sensible_Heating_Capacity = ''
        obj.Cooling_Limit = 'NoLimit'
        obj.Maximum_Cooling_Air_Flow_Rate = ''
        obj.Maximum_Total_Cooling_Capacity = ''
        obj.Heating_Availability_Schedule_Name = ''
        obj.Cooling_Availability_Schedule_Name = ''
        obj.Dehumidification_Control_Type = ''
        obj.Cooling_Sensible_Heat_Ratio = 0.7
        obj.Dehumidification_Setpoint = ''
        obj.Humidification_Control_Type = 'None'
        obj.Humidification_Setpoint = ''
        obj.Outdoor_Air_Method = 'None'
        obj.Outdoor_Air_Flow_Rate_per_Person = 0.00944
        obj.Outdoor_Air_Flow_Rate_per_Zone_Floor_Area = ''
        obj.Outdoor_Air_Flow_Rate_per_Zone = ''
        obj.Design_Specification_Outdoor_Air_Object_Name = ''
        obj.Demand_Controlled_Ventilation_Type = 'None'
        obj.Outdoor_Air_Economizer_Type = 'NoEconomizer'
        obj.Heat_Recovery_Type = 'None'
        obj.Sensible_Heat_Recovery_Effectiveness = 0.7
        obj.Latent_Heat_Recovery_Effectiveness = 0.65


    def print_field_names(self, ep_obj):
        print()
        for fld in ep_obj.fieldnames:
            if fld == 'key':
                print(ep_obj[fld])
            else:
                if self.is_number(ep_obj[fld]):
                    print("    obj.{} = {} ".format(fld, ep_obj[fld]))
                else:
                    print("    obj.{} = '' ".format(fld))

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False



    def test_object_order(self):
        iddfile = "C:/EnergyPlusV9-1-0/Energy+.idd"
        origfile = "C:/EnergyPlusV9-1-0/test/RefBldgMidriseApartmentNew2004_Chicago.idf"
        savefile = "C:/EnergyPlusV9-1-0/test/RefBldgMidriseApartmentNew2004_Chicago-posteppy.idf"
        save2file = "C:/EnergyPlusV9-1-0/test/RefBldgMidriseApartmentNew2004_Chicago-posteppy2.idf"

        IDF.setiddname(iddfile)

        idf = IDF(origfile)
        objs = idf.idfobjects['ElectricEquipment'.upper()]
        self.print_field_names(objs[0])

        idf.saveas(savefile)

        for obj in objs:
            obj.EndUse_Subcategory = 'PluggedInDevices'
        idf.saveas(save2file)
