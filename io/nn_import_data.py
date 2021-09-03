# Import data

no_list = (
    # Extra import functions
    ("Match__", "Match", "Tries to match the file with a known format (Experimental!!)"),
    # Formats
    ("C", "CNO", "Cno"),
    ("E", "ENO", "Eno"),
    ("G", "GNO", "Gno"),
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
    ("SonicTheHedgehog4EpisodeIPrototype_E", "Sonic the Hedgehog 4: Episode I (Prototype)",
     "Sonic the Hedgehog 4: Episode I (Prototype) Model | 9 Feb 2010"),
)

gno_list = (
    ("SuperMonkeyBallStepAndRoll_G", "Super Monkey Ball: Step & Roll",
     "Super Monkey Ball: Step & Roll Model | 9 Feb 2010"),
    ("SonicAndTheBlackKnight_G", "Sonic and the Black Knight", "Sonic and the Black Knight Model | 3 Mar 2009"),
    ("SonicRidersZeroGravity_G", "Sonic Riders Zero Gravity", "Sonic Riders Zero Gravity Model | 8 Jan 2008"),
    ("SonicUnleashed_G", "Sonic Unleashed", "Sonic Unleashed Model | 18 Nov 2008"),
    ("SonicAndTheSecretRings_G", "Sonic and the Secret Rings", "Sonic and the Secret Rings Model | 20 Feb 2007"),
    ("BleachShatteredBlade_G", "Bleach: Shattered Blade", "Bleach: Shattered Blade Model | 14 Dec 2006"),
    ("SuperMonkeyBallBananaBlitz_G", "Super Monkey Ball: Banana Blitz",
     "Super Monkey Ball: Banana Blitz | 19 Nov 2006"),
    ("SonicRiders_G", "Sonic Riders", "Sonic Riders Model | 21 Feb 2006"),
)

ino_list = (
    ("SonicTheHedgehog4EpisodeI_I", "Sonic the Hedgehog 4: Episode I",
     "Sonic the Hedgehog 4: Episode I Model | 7 Oct 2010"),
    ("SonicTheHedgehog4EpisodeIPre2016_I", "Sonic the Hedgehog 4: Episode I (Pre 2016)",
     "Sonic the Hedgehog 4: Episode I (Pre 2016) Model | 7 Oct 2010"),
)

lno_list = (
    ("SonicTheHedgehog4EpisodeII_L", "Sonic the Hedgehog 4: Episode II",
     "Sonic the Hedgehog 4: Episode II Model | 7 Oct 2010"),
    ("LovingDeadsHouseOfTheDeadEX_L", "Loving Deads: The House of the Dead EX",
     "Loving Deads: The House of the Dead EX Model | 2009"),
    ("HouseOfTheDead4_L", "The House of the Dead 4", "The House of the Dead 4 Model | 30 Dec 2005"),
)

sno_list = (
    ("SonicRidersZeroGravity_S", "Sonic Riders Zero Gravity", "Sonic Riders Zero Gravity Model | 8 Jan 2008"),
    ("SegaSuperstars_S", "Sega Superstars", "Sega Superstars Model | 22 Oct 2004"),
    ("SegaAges2500SeriesVol5GoldenAxe_S", "Sega Ages 2500 Series Vol. 5: Golden Axe",
     "Sega Ages 2500 Golden Axe Model | 25 Sep 2003"),
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
    "SonicTheHedgehog4EpisodeIPrototype_E": 2,

    "SuperMonkeyBallStepAndRoll_G": 1,
    "SonicAndTheBlackKnight_G": 1,
    "SonicUnleashed_G": 1,
    "SonicRidersZeroGravity_G": 0.5,
    "SonicAndTheSecretRings_G": 1,
    "BleachShatteredBlade_G": 1,
    "SuperMonkeyBallBananaBlitz_G": 1,
    "SonicRiders_G": 0.5,

    "SonicTheHedgehog4EpisodeI_I": 1,
    "SonicTheHedgehog4EpisodeIPre2016_I": 1,

    "SonicTheHedgehog4EpisodeII_L": 2,
    "LovingDeadsHouseOfTheDeadEX_L": 5,
    "HouseOfTheDead4_L": 5,

    "SonicRidersZeroGravity_S": 1,
    "SegaSuperstars_S": 1,
    "SegaAges2500SeriesVol5GoldenAxe_S": 1,

    "KOnAfterSchoolLive_U": 20,

    "Sonic2006_X": 10,
    "PhantasyStarUniverse_X": 1,
    "SonicRiders_X": 0.5,

    "TransformersHumanAlliance_Z": 1,
    "Sonic4Episode1_Z": 1,
    "SegaGoldenGun_Z": 5
}
