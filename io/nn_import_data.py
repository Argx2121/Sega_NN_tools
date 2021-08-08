# Import data

no_list = (
    # Extra import functions
    ("Match__", "Match", "Tries to match the file with a known format (Experimental!!)"),
    # Formats
    ("C", "CNO", "Cno"),
    ("E", "ENO", "Eno"),
    ("I", "INO", "Ino"),
    ("L", "LNO", "Lno"),
    ("S", "SNO", "Sno (Experimental!!)"),
    ("U", "UNO", "Uno"),
    ("X", "XNO", "Xno"),
    ("Z", "ZNO", "Zno"),
)

# Syntax plays an important role in importing so follow this arrangement:

# [game (CaramelCaps) + _ + nn indicator (Capitalised)],
# [game title],
# [game + filetype | release date]

# Therefore sonic riders (xbox) released 21st February 2006 becomes:
# [SonicRiders_X], [Sonic Riders], [Sonic Riders Model | 21 Feb 2006]


# Game formats should be sorted by date.

cno_list = (
    ("HouseOfTheDead4_C", "The House of the Dead 4", "The House of the Dead 4 Model | 17 Apr 2012"),
)

eno_list = (
    ("SonicFreeRiders_E", "Sonic Free Riders", "Sonic Free Riders Model | 4 Nov 2010"),
)

gno_list = (
)

ino_list = (
    ("Sonic4Episode1_I", "Sonic 4 Ep 1", "Sonic 4 Episode 1 Model | 7 Oct 2010"),
)

lno_list = (
    ("LovingDeadsHouseOfTheDeadEX_L", "Loving Deads: The House of the Dead EX",
     "Loving Deads: The House of the Dead EX Model | 2009"),
    ("HouseOfTheDead4_L", "The House of the Dead 4", "The House of the Dead 4 Model | 30 Dec 2005"),
)

sno_list = (
    ("SonicRidersZeroGravity_S", "Sonic Riders Zero Gravity", "Sonic Riders Zero Gravity Model | 8 Jan 2008"),
)

uno_list = (
    ("KOnAfterSchoolLive_U", "K-On! After School Live!!", "K-ON! Hokago Live!! Model | 30 Sep 2010"),
)

xno_list = (
    ("Sonic2006_X", "Sonic 2006", "Sonic '06 Model | 14 Nov 2006"),
    ("PhantasyStarUniverse_X", "Phantasy Star Universe", "Phantasy Star Universe Model | 31 Aug 2006"),
    ("SonicRiders_X", "Sonic Riders", "Sonic Riders Model | 21 Feb 2006"),
)

zno_list = (
    ("TransformersHumanAlliance_Z", "Transformers: Human Alliance", "Transformers Human Alliance Model | 2013"),
    ("Sonic4Episode1_Z", "Sonic 4 Ep 1", "Sonic 4 Episode 1 Model | 7 Oct 2010"),
    ("SegaGoldenGun_Z", "Sega Golden Gun", "Sega Golden Gun Model | 2010"),
)


determine_bone = {
    # Functions
    "Match__": 1,
    # Formats
    "HouseOfTheDead4_C": 2,

    "SonicFreeRiders_E": 0.5,

    "Sonic4Episode1_I": 1,

    "LovingDeadsHouseOfTheDeadEX_L": 5,
    "HouseOfTheDead4_L": 5,

    "SonicRidersZeroGravity_S": 1,

    "KOnAfterSchoolLive_U": 20,

    "Sonic2006_X": 10,
    "PhantasyStarUniverse_X": 1,
    "SonicRiders_X": 0.5,

    "TransformersHumanAlliance_Z": 1,
    "Sonic4Episode1_Z": 1,
    "SegaGoldenGun_Z": 5
}
