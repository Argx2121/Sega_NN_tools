from Sega_NN_tools.io.nn_import import match, debug, phantasy_star_universe_x, sonic_riders_x

no_list = (
    # keep debug first!!
    ("Debug__", "Debug", "For Developer testing and otherwise"),
    # extra import functions
    ("Match__", "Match", "Tries to match the file with a known format (Experimental!!)"),
    # formats
    ("X", "XNO", "Xno"),
    ("Z", "ZNO", "Zno"),
)

xno_list = (
    # game formats from newest to oldest
    ("Latest_X", "Latest", "Latest released game | N/A"),
    ("Sonic2006_X", "Sonic 2006", "Sonic '06 Model | 14 Nov 2006"),
    ("PhantasyStarUniverse_X", "Phantasy Star Universe", "Phantasy Star Universe Model | 31 Aug 2006"),
    ("SonicRiders_X", "Sonic Riders", "Sonic Riders Model / Archive | 21 Feb 2006"),
    # syntax plays a role in importing so follow this arrangement - no_list is just for the user:
    # [game (caramel caps) + _ + nn indicator (_ for non game)], [game], [game + file | platform | release date]
    # therefore sonic riders (xbox) released 21st February 2006 becomes:
    # [SonicRiders_X], [Sonic Riders], [Sonic Riders Model / Archive | PC / XBOX | 21 Feb 2006]
    # please don't shorten names, _ is used in non games as the variable is reassigned
)

zno_list = (
    ("Latest_Z", "Latest", "Latest released game | N/A"),
    ("Sonic4Episode1_Z", "Sonic 4 Ep 1", "Sonic 4 Episode 1 Model | 7 Oct 2010"),
)

determine_format_no = {
    "X": "xno_format", "Z": "zno_format"
}

determine_bone = {
    "Match__": 1, "Debug__": 1,
    "Sonic2006_X": 10, "PhantasyStarUniverse_X": 1, "SonicRiders_X": 0.1,
    "Sonic4Episode1_Z": 1,
    "X": 1, "Z": 1
}

determine_function = {  # only for formats that need their own importer function
    "Match__": match, "Debug__": debug,
    "PhantasyStarUniverse_X": phantasy_star_universe_x,
    "SonicRiders_X": sonic_riders_x,
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
        "X": xno_set, "Z": empty_set
    }
    determine_draw[no_nn_format]()  # execute the right ui for the format
