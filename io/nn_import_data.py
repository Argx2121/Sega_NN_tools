# lists lists
# determine_function is in nn_import - only needs to change for functions that need their own function
# *no_format in nn_import_settings and determine_nn_no

no_list = (
    # keep debug first!!
    ("Debug__", "Debug", "For Developer testing and otherwise"),
    # extra import functions
    ("Match__", "Match", "Tries to match the file with a known format (Experimental!!)"),
    # formats
    ("L", "LNO", "Lno"),
    ("S", "SNO", "Sno"),
    ("X", "XNO", "Xno"),
    ("Z", "ZNO", "Zno"),
)

# game formats from newest to oldest

# syntax plays a role in importing so follow this arrangement - no_list is just for the user:
# [game (caramel caps) + _ + nn indicator (_ for non game)], [game], [game + file | platform | release date]
# therefore sonic riders (xbox) released 21st February 2006 becomes:
# [SonicRiders_X], [Sonic Riders], [Sonic Riders Model / Archive | PC / XBOX | 21 Feb 2006]
# please don't shorten names, _ is used in non games as the variable is reassigned

lno_list = (
    ("Latest_L", "Latest", "Latest released game | N/A"),
    ("HouseOfTheDead4_L", "The House of the Dead 4", "The House of the Dead 4 Model | 30 Dec 2005"),
)

sno_list = (
    ("Latest_S", "Latest", "Latest released game | N/A"),
    ("SonicRidersZeroGravity_S", "Sonic Riders Zero Gravity", "Sonic Riders Zero Gravity Model | 8 Jan 2008"),
)

xno_list = (
    ("Latest_X", "Latest", "Latest released game | N/A"),
    ("Sonic2006_X", "Sonic 2006", "Sonic '06 Model | 14 Nov 2006"),
    ("PhantasyStarUniverse_X", "Phantasy Star Universe", "Phantasy Star Universe Model | 31 Aug 2006"),
    ("SonicRiders_X", "Sonic Riders", "Sonic Riders Model / Archive | 21 Feb 2006"),
)

zno_list = (
    ("Latest_Z", "Latest", "Latest released game | N/A"),
    ("Sonic4Episode1_Z", "Sonic 4 Ep 1", "Sonic 4 Episode 1 Model | 7 Oct 2010"),
)

determine_format_no = {
    "L": "lno_format", "S": "sno_format", "X": "xno_format", "Z": "zno_format"
}

determine_bone = {
    "Match__": 1, "Debug__": 1,
    "Latest_L": 1, "Latest_S": 1,  "Latest_X": 1, "Latest_Z": 1,
    "HouseOfTheDead4_L": 5,
    "SonicRidersZeroGravity_S": 1,
    "Sonic2006_X": 10, "PhantasyStarUniverse_X": 1, "SonicRiders_X": 0.1,
    "Sonic4Episode1_Z": 1,
}


def specific(no_nn_format, self):
    layout = self.layout

    def xno_set():
        def s06_set():
            this_box = layout.box()
            this_box.label(text="Sonic '06 specific settings:", icon="KEYFRAME")

            this_box.row().prop(self, "colour")

        def srpc_set():
            this_box = layout.box()
            this_box.label(text="Riders specific settings:", icon="KEYFRAME")
            this_box.row().prop(self, "image", expand=True)
            this_box.row().prop(self, "all_blocks")

        determine_internal_draw = {
            "Sonic2006_X": s06_set, "SonicRiders_X": srpc_set,
            "Latest_X": empty_set, "PhantasyStarUniverse_X": empty_set
        }
        determine_internal_draw[self.xno_format]()

    def empty_set():
        pass

    determine_draw = {
        "Match__": empty_set, "Debug__": empty_set,
        "L": empty_set, "S": empty_set, "X": xno_set, "Z": empty_set
    }
    determine_draw[no_nn_format]()  # execute the right ui for the format
