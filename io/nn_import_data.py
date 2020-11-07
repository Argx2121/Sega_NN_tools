# lists
# determine_function is in nn_import - only needs to change for formats that need their own function

no_list = (
    # extra import functions
    ("Match__", "Match", "Tries to match the file with a known format (Experimental!!)"),
    ("All__", "Read All", "Brute-forces the file, checking the whole file for models (Experimental, may be slow)"),
    # formats
    ("C", "CNO", "Cno"),
    ("E", "ENO", "Eno"),
    ("L", "LNO", "Lno"),
    ("S", "SNO", "Sno (Experimental!!)"),
    ("X", "XNO", "Xno"),
    ("Z", "ZNO", "Zno"),
)

# game formats from newest to oldest

# syntax plays a role in importing so follow this arrangement - no_list is just for the user:
# [game (caramel caps) + _ + nn indicator (_ for non game, in caps)], [game], [game + file | platform | release date]
# therefore sonic riders (xbox) released 21st February 2006 becomes:
# [SonicRiders_X], [Sonic Riders], [Sonic Riders Model / Archive | PC / XBOX | 21 Feb 2006]
# please don't shorten names, _ is used in non games as the variable is reassigned


# if any lists are added here you should add in nn.py
cno_list = (
    ("HouseOfTheDead4_C", "The House of the Dead 4", "The House of the Dead 4 Model | 17 Apr 2012"),
)

eno_list = (
    ("SonicFreeRiders_E", "Sonic Free Riders", "Sonic Free Riders Model / Archive | 4 Nov 2010"),
)

gno_list = (
)

lno_list = (
    ("HouseOfTheDead4_L", "The House of the Dead 4", "The House of the Dead 4 Model | 30 Dec 2005"),
)

sno_list = (
    ("SonicRidersZeroGravity_S", "Sonic Riders Zero Gravity", "Sonic Riders Zero Gravity Model | 8 Jan 2008"),
)

xno_list = (
    ("Sonic2006_X", "Sonic 2006", "Sonic '06 Model | 14 Nov 2006"),
    ("PhantasyStarUniverse_X", "Phantasy Star Universe", "Phantasy Star Universe Model | 31 Aug 2006"),
    ("SonicRiders_X", "Sonic Riders", "Sonic Riders Model / Archive | 21 Feb 2006"),
)

zno_list = (
    ("Sonic4Episode1_Z", "Sonic 4 Ep 1", "Sonic 4 Episode 1 Model | 7 Oct 2010"),
)


determine_bone = {
    # functions
    "Match__": 1, "All__": 1,
    # formats
    "HouseOfTheDead4_C": 2,
    "SonicFreeRiders_E": 0.5,
    "HouseOfTheDead4_L": 5,
    "SonicRidersZeroGravity_S": 1,
    "Sonic2006_X": 10, "PhantasyStarUniverse_X": 1, "SonicRiders_X": 0.5,
    "Sonic4Episode1_Z": 1,
}


def specific(no_nn_format, self):
    layout = self.layout

    def empty_set():
        pass

    def xno_set():
        def srpc_set():
            this_box = layout.box()
            this_box.label(text="Riders specific settings:", icon="KEYFRAME")
            this_box.row().prop(self, "image", expand=True)
            this_box.row().prop(self, "all_blocks")

        determine_internal_draw = {
            "Sonic2006_X": empty_set, "SonicRiders_X": srpc_set,
            "All__": empty_set, "PhantasyStarUniverse_X": empty_set
        }
        determine_internal_draw[self.X]()

    determine_draw = {
        "Match__": empty_set, "All__": empty_set,
        "C": empty_set, "E": empty_set, "G": empty_set,
        "L": empty_set, "S": empty_set, "X": xno_set, "Z": empty_set,
    }
    determine_draw[no_nn_format]()  # execute the right ui for the format
