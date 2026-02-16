from ..modules.game_specific.srpc.extract_image import ExtractImage
from ..modules.nn.nn import ReadNn
from ..modules.util import *
from ..modules.game_specific.srpc.read_archive import read_archive


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator


class ExtractSRPC:
    def __init__(self, context, file_path, set_batch):
        self.file = file_path
        self.file_path = bpy.path.abspath(file_path).rstrip(bpy.path.basename(file_path))
        self.set_batch = set_batch
        self.f = None
        self.archive = ()

    def execute(self):
        def check_obj_no_mat():
            f = self.f
            # check to see if materials are used
            f.seek(32 - 4, 1)
            obj_start = f.tell()
            if read_str(f, 4) == "NXOB":  # means there is no material block
                f.seek(read_int_tuple(f, 2)[1] + 4, 1)
                material_count, material_offset = read_int_tuple(f, 2)
                f.seek(obj_start + material_offset)
                material_offset = read_int_tuple(f, material_count * 2)[1::2]

                for material in material_offset:
                    f.seek(obj_start + material + 16)
                    f.seek(obj_start + read_int(f) + 4)
                    if read_int(f):  # if theres a texture count the file uses textures without a texture block
                        return True
            return False

        # noinspection SpellCheckingInspection
        def run_file():
            f = self.f
            archive = read_archive(f, "<")
            arc_types = {
                0: "Player", 8: "oPlayerShadow", 9: "Gear_Shadow", 20: "Animation",
                30: "oTornadoSmall", 31: "oTornado",
                103: "Stage",
                110: "Collision", 113: "Collision", 114: "Collision",
                121: "Stage_Settings", 130: "Sky", 165: "Stage", 166: "Stage", 167: "Stage",
                200: "Splines", 201: "Splines", 202: "Splines", 203: "Splines",
                42010: "Splines", 42011: "Splines",
                42013: "Rendering", 42015: "EvShadow", 42100: "Camera",
                42101: "Scene", 42102: "Scene", 42103: "Scene", 42105: "Scene", 42107: "Scene", 42108: "Scene",
                42109: "Scene", 42110: "Scene", 42120: "Camera",
                210: "Pathfinding", 220: "Pathfinding", 301: "Stage_Settings", 302: "Camera",
                304: "Rendering", 305: "Items_And_Rendering", 306: "Stage_Settings", 1000: "UI",
                1003: "eSunShine",
                1100: "Se",
                2000: "oStGate", 2010: "oItemBox", 2020: "oBomb", 2040: "oSign", 2050: "oType", 2060: "oSignal",
                2070: "oPartition",
                2080: "oPutBreak", 2081: "oPutBreak", 2082: "oPutBreak", 2083: "oPutBreak", 2084: "oPutBreak", 2085: "oPutBreak",
                2090: "oPit", 2091: "oPitSix",
                2100: "oRing", 2110: "oDashPanel", 2120: "oDashRing",
                2131: "oMoveFloor",
                2140: "oRunWall", 2150: "oOmochao", 2160: "oChao3D",
                12550: "oCh5SpaceDoor",
                5000: "oDoor", 5010: "oSkyRoad", 5020: "oRopeWayBase",
                5021: "oRopeWayObj", 5022: "Other", 5033: "Other",
                5030: "oCarLine", 5031: "oCarPath", 5032: "oCarPut", 5034: "oTrailer",
                6500: "oWaterWheel",
                7010: "oKakuRing", 7020: "oTRobot", 7021: "oTRobotPath", 7040: "oLavaWall",
                8000: "oCobweb", 8010: "oCentipedeNest",
                9250: "oArrow", 9251: "oArrowEndPoint", 9252: "oArrowColli",
                9261: "oeDPole", 9262: "oeDBird", 9263: "oeDownPole",
                10001: "oTurObject", 10002: "oAirForce",
                10010: "oFractureTower", 10011: "oFractureRoad",
                11010: "oDemonsGate", 11011: "oDemonsGateEffect", 11012: "oStainedGlass", 11013: "oSpotlight",
                11020: "oDragHand",
                11040: "oBirdsOfHeaven", 11041: "oBirdGimmic",
                11060: "oFaceStone", 11061: "oFaceStoneSwitch",
                12010: "oNightsMoon",
                12060: "oBatteryLaunchColli",
                7410: "oBreakFan", 7420: "oColdEggRobo",
                8500: "oCollapseTree",
                9270: "oSolarEclipse", 9280: "oDebris", 9290: "oEnergyBeam",
                9300: "oEnergyBarrier",
                9500: "oSandChasm", 9501: "oGakeLightData",
                12520: "oOphaopha", 12530: "eFireWorks", 12540: "oStardustRoad",
                12571: "oCCDashB", 12572: "oCCDashR", 12573: "oCCDashY",
                30000: "Effects", 31000: "Effects", 31004: "eLeaf", 31005: "eBubble", 31008: "Effects",
                31009: "oEvent", 31010: "oFlyWind",
                33000: "eParSet", 33001: "eParSet", 33002: "eParSet", 33003: "eParSet", 33004: "eParSet",
                33005: "eParSet", 33006: "eParSet", 33007: "eParSet", 33008: "eParSet", 33009: "eParSet",
                33010: "eParSet", 33011: "eParSet", 33012: "eParSet", 33013: "eParSet", 33014: "eParSet",
                33015: "eParSet", 33016: "eParSet", 33017: "eParSet", 33018: "eParSet", 33019: "eParSet",
                33020: "eParSet", 33021: "eParSet", 33022: "eParSet", 33023: "eParSet", 33024: "eParSet",
                33025: "eParSet", 33026: "eParSet", 33027: "eParSet", 33028: "eParSet", 33029: "eParSet",
                33100: "Stage_Settings", 33103: "Stage_Settings", 33104: "Stage_Settings", 33109: "Stage_Settings",
                44000: "MissionUI", 44100: "oMiJunk", 44110: "oMiTreasure", 44120: "Yazi", 44170: "Yazi2",
                44140: "oMiChkPnt", 44160: "oMiBomb",
                48000: "oSvlBall", 48030: "oSvlGate", 48040: "oSvlWall", 48050: "oSvlItem", 48060: "oSvlTranItem",
                60005: "oFlyJump", 60007: "oDipsTest",
                7400: "oCrane"
            }
            # 20 = anims?

            # when you extract files you check what type it is first
            # and you extract into subfoldres
            folder_path = self.file + "_Extracted"
            offsets = list(archive.sub_file_offsets) + [os.path.getsize(self.file), ]
            obj_need_texture = []

            for sf_count, sf_pos, sf_type in zip(
                    archive.sub_file_counts, archive.sub_file_additive_counts, archive.sub_file_types):
                if sf_type in arc_types:
                    arc_type = arc_types[sf_type]
                else:
                    arc_type = "Unknown"
                sf_path = bpy.path.native_pathsep(
                    folder_path + "\\" + arc_type + "_" + str(sf_type) + "_" + str(sf_pos) + "\\")
                pathlib.Path(sf_path).parent.mkdir(parents=True, exist_ok=True)

                sf_offsets = offsets[sf_pos:sf_pos + sf_count]
                index = 0
                sf_offsets = [x for x in sf_offsets if x != 0] + [offsets[sf_pos + sf_count]]

                for i, j in zip(sf_offsets, sf_offsets[1:]):
                    # we run a check to see what the file is, and we keep a list with textures because riders
                    f.seek(i)
                    if read_str(f, 4) == "NXIF":
                        file_name, index = ReadNn(f, self.file_path, "SonicRiders_X").find_file_name(index)
                        f.seek(i + 4)
                        if check_obj_no_mat():
                            obj_need_texture.append(sf_path + "\\" + file_name + ".texture_names")
                    else:
                        f.seek(i)
                        start_int = read_int(f)
                        f.seek(f.tell() + read_int(f) - 4)
                        if f.tell() < os.path.getsize(self.file) and read_str(f, 4) == "GBIX":
                            f.seek(i)
                            texture_name_list, _, _, type_byte, texture_bytes = \
                                ExtractImage(f, sf_path, "<").execute()
                            if type_byte == 20:
                                for file_name in obj_need_texture:
                                    pathlib.Path(file_name).parent.mkdir(parents=True, exist_ok=True)
                                    fn = open(bpy.path.native_pathsep(file_name), "wb")
                                    write_integer(fn, "<", len(texture_name_list))
                                    fn.write(texture_bytes)
                                    fn.close()
                                    f.seek(i)
                                    ExtractImage(f, file_name, "<").execute()
                                obj_need_texture = []
                            continue
                        elif start_int == 1481589336:
                            file_name = "Unnamed_File_" + str(index) + ".SonicRiders_X.pathfinding"
                            index += 1
                        elif start_int == 1113063936:
                            file_name = "Unnamed_File_" + str(index) + ".SonicRiders_X.splines"
                            index += 1
                        elif start_int == 66048:
                            file_name = "Unnamed_File_" + str(index) + ".SonicRiders_X.collision"
                            index += 1
                        elif start_int >> 24 & 128:
                            file_name = "Unnamed_File_" + str(index) + ".SonicRiders_X.objects"
                            index += 1
                        elif 1 < start_int < 25:  # yeah i have no idea im just guessing what a good range would be
                            file_name = "Unnamed_File_" + str(index) + ".SonicRiders_X.item_render"
                            index += 1
                        elif start_int == 1:  # its not worth making a function for this
                            file_name = "Unnamed_File_" + str(index) + ".SonicRiders_X.scene_render"
                            index += 1
                        else:
                            file_name = "Unnamed_File_" + str(index)
                            index += 1

                    f.seek(i)
                    pathlib.Path(sf_path + file_name).parent.mkdir(parents=True, exist_ok=True)
                    fn = open(bpy.path.native_pathsep(sf_path + file_name), "wb")
                    fn.write(f.read(j - i))
                    fn.close()

        if self.set_batch == "Single":
            self.f = open(self.file, "rb")
            run_file()
            self.f.close()
        else:
            file_list = get_files(self.file, self.set_batch, name_ignore=".")
            for self.file in file_list:
                self.f = open(self.file, "rb")
                run_file()
                self.f.close()
        show_finished("Sonic Riders PC Extractor")
        return {'FINISHED'}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator


class SonicRPCTools(Operator, ImportHelper):
    """Extract files from an uncompressed Sonic Riders PC / XBOX Archive"""
    bl_idname = "srpc.extract"
    bl_label = "Extract Files"
    filename_ext = "*"
    filter_glob: StringProperty(
        default="*",
        options={'HIDDEN'},
        maxlen=255,
    )
    set_batch: EnumProperty(
        name="Batch usage",
        description="What files should be imported",
        items=(
            ('Single', "Single", "Only opens selected file"),
            ('Batch', "Batch", "Opens all of the folders files (non recursive)"),
            ('Recursive', "Recursive", "Opens files recursively")),
        default='Single'
    )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Sonic Riders PC / XBOX Extractor Settings:", icon="KEYFRAME_HLT")
        box.row().prop(self, "set_batch", expand=True)

    def execute(self, context):
        # noinspection PyUnresolvedReferences
        return ExtractSRPC(context, self.filepath, self.set_batch).execute()
