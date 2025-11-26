from dataclasses import dataclass

from ..nn import nn_unknown, nn_information_file, nn_texture_library, nn_effects, nn_node_names, \
    nn_object, nn_offset_file, nn_file_name, nn_end, nn_camera, nn_motion, nn_light, nn_morph
from ..nn.nn_object import ModelData
from ...io import nn_import_data as nn_data
from ..util import *


class ReadNn:
    __slots__ = ["f", "filepath", "file_len", "format_type", "read_animation", "debug", "nn", "big_endian", "det_n"]

    def __init__(self, f, filepath, format_type="", animation=False, debug=False):
        self.f = f
        self.filepath = filepath
        self.file_len = os.path.getsize(self.filepath)
        self.format_type = format_type
        self.read_animation = animation
        self.debug = debug
        self.nn = self.NnFile()
        self.big_endian = {"C", "E", "G"}
        self.det_n = {
            # specific
            "NCIF": self._info_1, "NEIF": self._info_1, "NGIF": self._info_1,
            "NIIF": self._info_1, "NLIF": self._info_1, "NSIF": self._info_1, "NUIF": self._info_1,
            "NXIF": self._info_1, "NZIF": self._info_1,

            "NCTL": self._tex_2, "NETL": self._tex_2, "NGTL": self._tex_2,
            "NITL": self._tex_1, "NLTL": self._tex_1, "NSTL": self._tex_1, "NUTL": self._tex_1,
            "NXTL": self._tex_1, "NZTL": self._tex_1,

            "NCNN": self._node_2, "NENN": self._node_2, "NGNN": self._node_2,
            "NINN": self._node_1, "NLNN": self._node_1, "NSNN": self._node_1, "NUNN": self._node_1,
            "NXNN": self._node_1, "NZNN": self._node_1,

            "NCTN": self._mname_2, "NETN": self._mname_2, "NGTN": self._mname_2,
            "NITN": self._mname_1, "NLTN": self._mname_1, "NSTN": self._mname_1, "NUTN": self._mname_1,
            "NXTN": self._mname_1, "NZTN": self._mname_1,

            "NCOB": self._obj_c, "NEOB": self._obj_e, "NGOB": self._obj_g,
            "NIOB": self._obj_i, "NLOB": self._obj_l, "NSOB": self._obj_s, "NUOB": self._obj_u,
            "NXOB": self._obj_x, "NZOB": self._obj_z,

            "NCCA": self._cam_2, "NECA": self._cam_2, "NGCA": self._cam_2,
            "NICA": self._cam_1, "NLCA": self._cam_1, "NSCA": self._cam_1, "NUCA": self._cam_1,
            "NXCA": self._cam_1, "NZCA": self._cam_1,

            "NCLI": self._light_2, "NELI": self._light_2, "NGLI": self._light_2,
            "NILI": self._light_1, "NLLI": self._light_1, "NSLI": self._light_1, "NULI": self._light_1,
            "NXLI": self._light_1, "NZLI": self._light_1,

            "NCMT": self._morph_2, "NEMT": self._morph_2, "NGMT": self._morph_2,
            "NIMT": self._morph_1, "NLMT": self._morph_1, "NSMT": self._morph_1, "NUMT": self._morph_1,
            "NXMT": self._morph_1, "NZMT": self._morph_1,

            "NCMM": self._nmot_2, "NEMM": self._nmot_2, "NGMM": self._nmot_2,
            "NIMM": self._nmot_1, "NLMM": self._nmot_1, "NSMM": self._nmot_1, "NUMM": self._nmot_1,
            "NXMM": self._nmot_1, "NZMM": self._nmot_1,

            "NCMC": self._nmot_2, "NEMC": self._nmot_2, "NGMC": self._nmot_2,
            "NIMC": self._nmot_1, "NLMC": self._nmot_1, "NSMC": self._nmot_1, "NUMC": self._nmot_1,
            "NXMC": self._nmot_1, "NZMC": self._nmot_1,

            "NCML": self._nmot_2, "NEML": self._nmot_2, "NGML": self._nmot_2,
            "NIML": self._nmot_1, "NLML": self._nmot_1, "NSML": self._nmot_1, "NUML": self._nmot_1,
            "NXML": self._nmot_1, "NZML": self._nmot_1,

            "NCMO": self._nmot_2, "NEMO": self._nmot_2, "NGMO": self._nmot_2,
            "NIMO": self._nmot_1, "NLMO": self._nmot_1, "NSMO": self._nmot_1, "NUMO": self._nmot_1,
            "NXMO": self._nmot_1, "NZMO": self._nmot_1,

            "NCMA": self._nmot_2, "NEMA": self._nmot_2, "NGMA": self._nmot_2,
            "NIMA": self._nmot_1, "NLMA": self._nmot_1, "NSMA": self._nmot_1, "NUMA": self._nmot_1,
            "NXMA": self._nmot_1, "NZMA": self._nmot_1,

            "NCEF": self._eff_2, "NEEF": self._eff_2, "NGEF": self._eff_2,
            "NIEF": self._eff_1, "NLEF": self._eff_1, "NSEF": self._eff_1, "NUEF": self._eff_1,
            "NXEF": self._eff_1, "NZEF": self._eff_1,

            # generic
            "NOF0": self._nof0, "NFN0": self._nfn0, "NEND": self._nend,
        }  # supported blocks

    @dataclass
    class NnFile:
        start: int = 0  # after n_if
        textures: Tuple[str, ...] = False  # texture names + interp
        effect: tuple = False
        bones: Tuple[str, ...] = False  # bone names
        model: ModelData = False  # model data
        camera: tuple = False
        light: tuple = False
        animation: tuple = False
        morphs: tuple = False
        morph_names: tuple = False
        name: str = "Unnamed_File"  # file name
        end: bool = False  # if end of file reached

    # functions
    def _read_block(self):
        f = self.f
        det_n = self.det_n
        block_name = read_str(f, 4)
        if block_name in det_n:
            if self.format_type[-1] == "_":
                self.format_type = getattr(nn_data, block_name[1].lower() + "no_list")[0][0]
            start_time = console_out_pre("Reading %s..." % block_name)
            det_n[block_name]()
            console_out_post(start_time)
        elif block_name.startswith("N"):
            self._nn_unknown(block_name)

    def read_file(self):
        while not self.nn.end and self.file_len > self.f.tell():
            self._read_block()
        if self.nn.model:
            if not self.nn.textures:
                self.read_texture_names()
            if not self.nn.bones:
                self.read_bone_names()
            if not self.nn.effect:
                self.read_effect_names()
        if self.nn.morphs:
            if not self.nn.morph_names:
                self.read_morph_names()
        if self.nn.name == "Unnamed_File":
            self.nn.name = bpy.path.basename(self.filepath)
        return self.format_type, self.nn

    def read_texture_names(self):
        if self.debug:
            print("Trying external texture names")

        if os.path.exists(self.filepath + ".texture_names"):
            f = open(self.filepath + ".texture_names", "rb")
            texture_count = read_int(f)
            texture_names = read_str_nulls(f, os.path.getsize(self.filepath) - 4)[:texture_count]
            self.nn.textures = [(t + ".png", (nn_texture_library.interp_mag(0), nn_texture_library.interp_mag(0))) for t in texture_names]
            f.close()

            if self.debug:
                print(self.nn.textures)
            return

        final_letter = "t"
        if self.filepath[-3:].isupper():
            final_letter = "T"

        if os.path.exists(self.filepath[:-1] + final_letter):
            f = open(self.filepath[:-1] + final_letter, "rb")
            f.seek(4, 1)
            f.seek(read_int(f), 1)
            block_name = read_str(f, 4)

            if block_name[0] == "N" and block_name[2] == "T" and block_name[3] == "L":  # N*TL
                if block_name[1] in self.big_endian:
                    self.nn.textures = nn_texture_library.Read(
                        f, f.tell() - 4, self.filepath, self.format_type).be()
                else:
                    self.nn.textures = nn_texture_library.Read(
                        f, f.tell() - 4, self.filepath, self.format_type).le()
                if self.debug:
                    print(self.nn.textures)
            f.close()

    def read_bone_names(self):
        if self.debug:
            print("Trying external bone names")

        final_letter = "a"
        if self.filepath[-3:].isupper():
            final_letter = "A"

        if os.path.exists(self.filepath[:-1] + final_letter):
            f = open(self.filepath[:-1] + final_letter, "rb")
            f.seek(4, 1)
            f.seek(read_int(f), 1)
            block_name = read_str(f, 4)

            if block_name[0] == block_name[2] == block_name[3]:  # N*NN
                if block_name[1] in self.big_endian:
                    self.nn.bones = nn_node_names.Read(f, f.tell() - 4).be()
                else:
                    self.nn.bones = nn_node_names.Read(f, f.tell() - 4).le()

            if self.debug:
                stdout.write("Bone names: " + str(self.nn.bones) + "\n")
            f.close()

    def read_effect_names(self):
        if self.debug:
            print("Trying external effect names")

        final_letter = "e"
        if self.filepath[-3:].isupper():
            final_letter = "E"

        if os.path.exists(self.filepath[:-1] + final_letter):
            f = open(self.filepath[:-1] + final_letter, "rb")
            f.seek(4, 1)
            f.seek(read_int(f), 1)
            block_name = read_str(f, 4)

            if block_name[0] == "N" and block_name[2] == "E" and block_name[3] == "F":  # N*EF
                if block_name[1] in self.big_endian:
                    self.nn.effect = nn_effects.Read(f, f.tell() - 4).be()
                else:
                    self.nn.effect = nn_effects.Read(f, f.tell() - 4).le()

            if self.debug:
                stdout.write("Effect names: " + str(self.nn.effect) + "\n")
            f.close()

    def read_morph_names(self):
        if self.debug:
            print("Trying external morph names")

        final_letter = "h"
        if self.filepath[-3:].isupper():
            final_letter = "H"

        if os.path.exists(self.filepath[:-1] + final_letter):
            f = open(self.filepath[:-1] + final_letter, "rb")
            f.seek(4, 1)
            f.seek(read_int(f), 1)
            block_name = read_str(f, 4)

            if block_name[0] == 'N' and block_name[2] == 'T' and block_name[3] == 'N':
                if block_name[1] in self.big_endian:
                    self.nn.morph_names = nn_node_names.Read(f, f.tell() - 4).be()
                else:
                    self.nn.morph_names = nn_node_names.Read(f, f.tell() - 4).le()

            if self.debug:
                stdout.write("Morph names: " + str(self.nn.morph_names) + "\n")
            f.close()

    def find_file_name(self, index: int):
        """Reads NN file until NEND in search of file name.
        If no file name block is found,
        a generic name with the filetype based of the file contents + the file index is returned.
        Run this function after a N*IF string as been read."""
        f = self.f
        block_types = {
            "N_OB": "no", "N_TL": "no",
            "N_NN": "na",
            "N_MA": "nv", "N_MO": "nm", "N_MC": "nd", "N_MT": "ng", "N_MM": "nf", "N_ML": "ni",
            "N_CA": "nd", "N_LI": "ni",
        }

        start = f.tell() - 4

        self._info_1()
        block = read_str(f, 4)

        block_type = block[1]
        block = block[:1] + "_" + block[2:]
        block = block_types[block]

        if block_type in self.big_endian:
            endian = ">"
        else:
            endian = "<"

        f.seek(start + 20)  # use NOF0 offset
        f.seek(read_int(f, endian) + start)

        b_name = read_str(f, 4)
        while b_name != "NEND" and b_name != "NFN0":
            f.seek(read_int(f), 1)
            b_name = read_str(f, 4)

        if b_name == "NFN0":
            b_len = read_int(f)
            end_of_block = b_len + f.tell()
            f.seek(8, 1)
            file_name = read_str_nulls(f, b_len)[0]
            f.seek(end_of_block)
            b_name = read_str(f, 4)
            while b_name != "NEND":
                f.seek(read_int(f), 1)
                b_name = read_str(f, 4)
            f.seek(read_int(f), 1)
        else:
            f.seek(read_int(f), 1)
            file_name = "Unnamed_File_" + str(index) + "." + block_type.lower() + block
            index += 1
        return file_name, index

    def write_model(self, model_info, settings):
        f = self.f
        format_type = self.format_type
        nof0_offsets = []
        block_count = 1
        big_endian = False
        version_number = 1
        alignment = 16
        if format_type[-1] in self.big_endian:
            big_endian = True

        if model_info.materials.texture_list and settings.texture_block:
            if big_endian:
                nof0_offsets = nn_texture_library.Write(
                    f, format_type, model_info.materials.texture_list, nof0_offsets).be()
            else:
                nof0_offsets = nn_texture_library.Write(
                    f, format_type, model_info.materials.texture_list, nof0_offsets).le()
            block_count += 1

        # NXEF

        if settings.bone_block:
            if big_endian:
                nof0_offsets = nn_node_names.Write(
                    f, format_type, [b.name for b in model_info.bones], nof0_offsets).be()
            else:
                nof0_offsets = nn_node_names.Write(
                    f, format_type, [b.name for b in model_info.bones], nof0_offsets).le()
            block_count += 1

        if format_type[-1] == "G":
            version_number = 1
            nof0_offsets = nn_object.WriteModel(f, format_type, self.debug, nof0_offsets, model_info, settings).gno()
        elif format_type[-1] == "X":
            version_number = 1
            nof0_offsets = nn_object.WriteModel(f, format_type, self.debug, nof0_offsets, model_info, settings).xno()
        elif format_type[-1] == "Z":
            version_number = 1
            nof0_offsets = nn_object.WriteModel(f, format_type, self.debug, nof0_offsets, model_info, settings).zno()

        offset_file_start = f.tell()
        if big_endian:
            nn_offset_file.Write(f, nof0_offsets).be()
        else:
            nn_offset_file.Write(f, nof0_offsets).le()
        offset_file_end = f.tell()

        if settings.name:
            nn_file_name.Write(f, model_info.name).generic()
        nn_end.Write(f, alignment).generic()

        f.seek(0)
        if big_endian:
            nn_information_file.Write(f, format_type, block_count, offset_file_start, offset_file_end, version_number).be()
        else:
            nn_information_file.Write(f, format_type, block_count, offset_file_start, offset_file_end, version_number).le()

        if settings.order and model_info.materials.texture_list:
            end_str = "." + format_type[-1].lower() + "vr"
            tex_names = [bpy.path.basename(a).rsplit(".", 1)[0] + end_str for a in model_info.materials.texture_list]
            tex_names = '\n'.join(tex_names)
            nf = open(self.filepath + ".order.txt", 'w')
            nf.write(tex_names)
            nf.close()

    def write_camera(self, camera_info, settings):
        f = self.f
        format_type = self.format_type
        nof0_offsets = []
        block_count = 1
        big_endian = False
        version_number = 1
        alignment = 16
        if format_type[-1] in self.big_endian:
            big_endian = True

        if big_endian:
            nof0_offsets = nn_camera.Write(f, format_type, settings.debug, nof0_offsets, camera_info, settings).be()
        else:
            nof0_offsets = nn_camera.Write(f, format_type, settings.debug, nof0_offsets, camera_info, settings).le()
        block_count += 1

        # motion here later

        offset_file_start = f.tell()
        if big_endian:
            nn_offset_file.Write(f, nof0_offsets).be()
        else:
            nn_offset_file.Write(f, nof0_offsets).le()
        offset_file_end = f.tell()

        if settings.name:
            nn_file_name.Write(f, camera_info.name).generic()
        nn_end.Write(f, alignment).generic()

        f.seek(0)
        if big_endian:
            nn_information_file.Write(f, format_type, block_count, offset_file_start, offset_file_end, version_number).be()
        else:
            nn_information_file.Write(f, format_type, block_count, offset_file_start, offset_file_end, version_number).le()

    # block definitions
    # specific
    def _info_1(self):
        self.nn.start = nn_information_file.Read(self.f).type_1()
        if self.debug:
            message = "Post info file position: " + str(self.nn.start)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def _tex_1(self):
        self.nn.textures = nn_texture_library.Read(self.f, self.nn.start, self.filepath, self.format_type).le()
        if self.debug:
            message = "Texture names: " + str(self.nn.textures)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def _tex_2(self):
        self.nn.textures = nn_texture_library.Read(self.f, self.nn.start, self.filepath, self.format_type).be()
        if self.debug:
            message = "Texture names: " + str(self.nn.textures)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def _eff_1(self):
        self.nn.effect = nn_effects.Read(self.f, self.nn.start).le()
        if self.debug:
            message = "Effects: " + str(self.nn.effect)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def _eff_2(self):
        self.nn.effect = nn_effects.Read(self.f, self.nn.start).be()
        if self.debug:
            message = "Effects: " + str(self.nn.effect)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def _cam_1(self):
        self.nn.camera = nn_camera.Read(self.f).type_1()

    def _cam_2(self):
        self.nn.camera = nn_camera.Read(self.f).type_2()

    def _light_1(self):
        self.nn.light = nn_light.Read(self.f).type_1()

    def _light_2(self):
        self.nn.light = nn_light.Read(self.f).type_2()

    def _morph_1(self):
        self.nn.morphs = nn_morph.Read(self.f, self.nn.start, self.format_type, self.debug).le()

    def _morph_2(self):
        self.nn.morphs = nn_morph.Read(self.f, self.nn.start, self.format_type, self.debug).be()

    def _nmot_1(self):
        self.nn.animation = nn_motion.Read(self.f, self.nn.start).le()

    def _nmot_2(self):
        self.nn.animation = nn_motion.Read(self.f, self.nn.start).be()

    def _node_1(self):
        self.nn.bones = nn_node_names.Read(self.f, self.nn.start).le()
        if self.debug:
            message = "Bone names: " + str(self.nn.bones)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def _node_2(self):
        self.nn.bones = nn_node_names.Read(self.f, self.nn.start).be()
        if self.debug:
            message = "Bone names: " + str(self.nn.bones)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def _mname_1(self):
        self.nn.morph_names = nn_node_names.Read(self.f, self.nn.start).le()  # its okay theyre the same code
        if self.debug:
            message = "Morph names: " + str(self.nn.morph_names)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def _mname_2(self):
        self.nn.morph_names = nn_node_names.Read(self.f, self.nn.start).be()
        if self.debug:
            message = "Morph names: " + str(self.nn.morph_names)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def _nn_unknown(self, block_name):
        nn_unknown.Read(self.f, block_name).generic()

    def _obj_c(self):
        self.nn.model = nn_object.ReadModel(self.f, self.nn.start, self.format_type, self.debug).cno()
        console_out_pre("")

    def _obj_e(self):
        self.nn.model = nn_object.ReadModel(self.f, self.nn.start, self.format_type, self.debug).eno()
        console_out_pre("")

    def _obj_g(self):
        self.nn.model = nn_object.ReadModel(self.f, self.nn.start, self.format_type, self.debug).gno()
        console_out_pre("")

    def _obj_i(self):
        self.nn.model = nn_object.ReadModel(self.f, self.nn.start, self.format_type, self.debug).ino()
        console_out_pre("")

    def _obj_l(self):
        self.nn.model = nn_object.ReadModel(self.f, self.nn.start, self.format_type, self.debug).lno()
        console_out_pre("")

    def _obj_s(self):
        self.nn.model = nn_object.ReadModel(self.f, self.nn.start, self.format_type, self.debug).sno()
        console_out_pre("")

    def _obj_u(self):
        self.nn.model = nn_object.ReadModel(self.f, self.nn.start, self.format_type, self.debug).uno()
        console_out_pre("")

    def _obj_x(self):
        self.nn.model = nn_object.ReadModel(self.f, self.nn.start, self.format_type, self.debug).xno()
        console_out_pre("")

    def _obj_z(self):
        self.nn.model = nn_object.ReadModel(self.f, self.nn.start, self.format_type, self.debug).zno()
        console_out_pre("")

    # generic
    def _nof0(self):
        nn_offset_file.Read(self.f).generic()

    def _nfn0(self):
        self.nn.name = nn_file_name.Read(self.f).generic()
        if self.debug:
            message = "File name: " + str(self.nn.name)
            stdout.write("| \n" + message + " " * (50 - len(message)))

    def _nend(self):
        nn_end.Read(self.f).generic()
        self.nn.end = True
