# Import data

no_export_list = (
    # Extra import functions
    # ("None__", "Set Format", "Set model format"),
    # Formats
    # ("C", "CNO", "Cno"),
    # ("E", "ENO", "Eno"),
    ("G", "GNO", "Gno"),
    # ("I", "INO", "Ino"),
    # ("L", "LNO", "Lno"),
    # ("S", "SNO", "Sno"),
    # ("U", "UNO", "Uno"),
    ("X", "XNO", "Xno"),
    # ("Z", "ZNO", "Zno"),
)

nn_export_list = (
    # Formats
    ("C", "CNO", "Cno"),
    ("E", "ENO", "Eno"),
    ("G", "GNO", "Gno"),
    ("I", "INO", "Ino"),
    ("L", "LNO", "Lno"),
    ("S", "SNO", "Sno"),
    ("U", "UNO", "Uno"),
    ("X", "XNO", "Xno"),
    ("Z", "ZNO", "Zno"),
)

no_list = (
    # Extra import functions
    ("Match__", "Match", "Tries to match the file with a known format (Experimental!!)"),
    # Formats
    ("C", "CNO", "Cno"),
    ("E", "ENO", "Eno"),
    ("G", "GNO", "Gno"),
    ("I", "INO", "Ino"),
    ("L", "LNO", "Lno"),
    ("S", "SNO", "Sno"),
    ("U", "UNO", "Uno"),
    ("X", "XNO", "Xno"),
    ("Z", "ZNO", "Zno"),
)

nd_list = (
    # Extra import functions
    ("Match__", "Match", "Tries to match the file with a known format (Experimental!!)"),
    # Formats
    ("C", "CND", "Cnd"),
    ("E", "END", "End"),
    ("G", "GND", "Gnd"),
    ("I", "IND", "Ind"),
    ("L", "LND", "Lnd"),
    ("S", "SND", "Snd"),
    ("U", "UND", "Und"),
    ("X", "XND", "Xnd"),
    ("Z", "ZND", "Znd"),
)

ni_list = (
    # Extra import functions
    ("Match__", "Match", "Tries to match the file with a known format (Experimental!!)"),
    # Formats
    ("C", "CNI", "Cni"),
    ("E", "ENI", "Eni"),
    ("G", "GNI", "Gni"),
    ("I", "INI", "Ini"),
    ("L", "LNI", "Lni"),
    ("S", "SNI", "Sni"),
    ("U", "UNI", "Uni"),
    ("X", "XNI", "Xni"),
    ("Z", "ZNI", "Zni"),
)

nm_list = (
    # Extra import functions
    ("Match__", "Match", "Tries to match the file with a known format (Experimental!!)"),
    # Formats
    ("C", "CNM", "Cnm"),
    ("E", "ENM", "Enm"),
    ("G", "GNM", "Gnm"),
    ("I", "INM", "Inm"),
    ("L", "LNM", "Lnm"),
    ("S", "SNM", "Snm"),
    ("U", "UNM", "Unm"),
    ("X", "XNM", "Xnm"),
    ("Z", "ZNM", "Znm"),
)

nv_list = (
    # Extra import functions
    ("Match__", "Match", "Tries to match the file with a known format (Experimental!!)"),
    # Formats
    ("C", "CNV", "Cnv"),
    ("E", "ENV", "Env"),
    ("G", "GNV", "Gnv"),
    ("I", "INV", "Inv"),
    ("L", "LNV", "Lnv"),
    ("S", "SNV", "Snv"),
    ("U", "UNV", "Unv"),
    ("X", "XNV", "Xnv"),
    ("Z", "ZNV", "Znv"),
)

ng_list = (
    # Extra import functions
    ("Match__", "Match", "Tries to match the file with a known format (Experimental!!)"),
    # Formats
    ("C", "CNG", "Cng"),
    ("E", "ENG", "Eng"),
    ("G", "GNG", "Gng"),
    ("I", "ING", "Ing"),
    ("L", "LNG", "Lng"),
    ("S", "SNG", "Sng"),
    ("U", "UNG", "Ung"),
    ("X", "XNG", "Xng"),
    ("Z", "ZNG", "Zng"),
)

# Syntax plays an important role in importing so follow this arrangement:

# [game (CaramelCaps) + _ + nn indicator (Capitalised)],
# [game title],
# [game + filetype | release date]
# NN version from exe if possible

# Therefore sonic riders (xbox) released 21st February 2006 becomes:
# [SonicRiders_X], [Sonic Riders], [Sonic Riders Model | 21 Feb 2006]


# Game formats should be sorted by date.

cn_list = (
    ("HouseOfTheDead4_C", "The House of the Dead 4", "The House of the Dead 4 Model | 17 Apr 2012"),
    ("SonicTheHedgehog4EpisodeI_C", "Sonic the Hedgehog 4: Episode I",
     "Sonic the Hedgehog 4: Episode I Model | 7 Oct 2010"),
    ("SonicTheHedgehog4EpisodeII_C", "Sonic the Hedgehog 4: Episode II",
     "Sonic the Hedgehog 4: Episode II Model | 7 Oct 2010"),
)

en_list = (
    ("SonicFreeRiders_E", "Sonic Free Riders", "Sonic Free Riders Model | 4 Nov 2010"),
    ("SonicTheHedgehog4EpisodeIPrototype_E", "Sonic the Hedgehog 4: Episode I (Prototype)",
     "Sonic the Hedgehog 4: Episode I (Prototype) Model | 9 Feb 2010"),
)

gn_list = (
    ("SuperMonkeyBallStepAndRoll_G", "Super Monkey Ball: Step & Roll",
     "Super Monkey Ball: Step & Roll Model | 9 Feb 2010"),
    # SEGA NN Library for Wii
    # nn Ver 1.20.20 Build:Oct 28 2008 15:51:05
    # 1.20.20
    ("SonicAndTheBlackKnight_G", "Sonic and the Black Knight", "Sonic and the Black Knight Model | 3 Mar 2009"),
    # SEGA NN Library for Wii
    # nn Ver 1.20.20 Build:Oct 28 2008 15:51:05
    # 1.20.20
    ("SonicUnleashed_G", "Sonic Unleashed", "Sonic Unleashed Model | 18 Nov 2008"),
    # SEGA NN Library for GAMECUBE
    # nn Ver 1.20.14 Build:Jun 24 2008 14:38:57
    # 1.20.14
    ("SonicRidersZeroGravity_G", "Sonic Riders Zero Gravity", "Sonic Riders Zero Gravity Model | 8 Jan 2008"),
    # SEGA NN Library for GAMECUBE
    # nn Ver 1.20.04 Build:May 14 2007 17:00:21
    # 1.20.04
    ("GhostSquad_G", "Ghost Squad", "Ghost Squad Model | 23 Oct 2007"),
    # SEGA NN Library for GAMECUBE
    # nn Ver 1.20.02 Build:Dec 12 2006 17:30:14
    # 1.20.02
    ("SonicAndTheSecretRings_G", "Sonic and the Secret Rings", "Sonic and the Secret Rings Model | 20 Feb 2007"),
    # SEGA NN Library for GAMECUBE
    # nn Ver 1.19.095 Build:Oct 10 2006 15:39:36
    # 1.19.095
    ("BleachShatteredBlade_G", "Bleach: Shattered Blade", "Bleach: Shattered Blade Model | 14 Dec 2006"),
    # SEGA NN Library for GAMECUBE
    # nn Ver 1.19.095 Build:Oct 10 2006 15:39:36
    # 1.19.095
    ("SuperMonkeyBallBananaBlitz_G", "Super Monkey Ball: Banana Blitz",
     "Super Monkey Ball: Banana Blitz | 19 Nov 2006"),
    # SEGA NN Library for GAMECUBE
    # nn Ver 1.19.09 Build:Jun 22 2006 19:57:49
    # 1.19.09
    ("SonicRiders_G", "Sonic Riders", "Sonic Riders Model | 21 Feb 2006"),
    # UNKNOWN

    # Dabi Tsuku 3 - Derby-ba o Tsukurou!
    # SEGA NN Library for GAMECUBE
    # nn Ver 1.07.02 Build:Sep  9 2003 11:06:38
    #
    # %s Version %s
    # (C) SEGA Corporation Creative Center Graphics Sect.
)

in_list = (
    ("SonicTheHedgehog4EpisodeI_I", "Sonic the Hedgehog 4: Episode I",
     "Sonic the Hedgehog 4: Episode I Model | 7 Oct 2010"),
    ("SonicTheHedgehog4EpisodeIPre2016_I", "Sonic the Hedgehog 4: Episode I (Pre 2016)",
     "Sonic the Hedgehog 4: Episode I (Pre 2016) Model | 7 Oct 2010"),
)

ln_list = (
    ("SonicTheHedgehog4EpisodeIIOuya_L", "Sonic the Hedgehog 4: Episode II (Ouya)",
     "Sonic the Hedgehog 4: Episode II for Ouya Model | July 3, 2013"),
    # UNKNOWN
    ("SonicTheHedgehog4EpisodeII_L", "Sonic the Hedgehog 4: Episode II",
     "Sonic the Hedgehog 4: Episode II Model | 7 Oct 2010"),
    # UNKNOWN
    ("LovingDeadsHouseOfTheDeadEX_L", "Loving Deads: The House of the Dead EX",
     "Loving Deads: The House of the Dead EX Model | 2009"),
    # UNKNOWN
    ("HouseOfTheDead4_L", "The House of the Dead 4", "The House of the Dead 4 Model | 30 Dec 2005"),
    # SEGA NN Library for Lindbergh
    # nn Ver 1.03.03 Build:Oct 21 2005 16:30:13

    # Too Spicy
    # SEGA NN Library for LINDBERGH 1.04.03
    # nn Ver 1.04.03 Build:Feb 15 2007 01:59:38
)

sn_list = (
    ("SonicRidersZeroGravity_S", "Sonic Riders Zero Gravity", "Sonic Riders Zero Gravity Model | 8 Jan 2008"),
    # SEGA NN Library for PlayStation2
    # nn Ver 1.18.56 Build:Dec 26 2006 17:14:10
    # 1.18.56
    # %s Version %s
    # (C) SEGA Corporation Creative Center Graphics Sect.
    ("SegaSuperstars_S", "Sega Superstars", "Sega Superstars Model | 22 Oct 2004"),
    # UNKNOWN
    ("SegaAges2500SeriesVol5GoldenAxe_S", "Sega Ages 2500 Series Vol. 5: Golden Axe",
     "Sega Ages 2500 Golden Axe Model | 25 Sep 2003"),
    # UNKNOWN

    # Sonic Riders
    # SEGA NN Library for PlayStation2
    # nn Ver 1.18.43 Build:Oct  7 2005 16:13:05
    # 1.18.43
    # %s Version %s
    # (C) SEGA Corporation Creative Center Graphics Sect.
)

un_list = (
    ("KOnAfterSchoolLive_U", "K-On! After School Live!!", "K-ON! Hokago Live!! Model | 30 Sep 2010"),
)

xn_list = (
    ("Sonic2006_X", "Sonic 2006", "Sonic '06 Model | 14 Nov 2006"),
    ("PhantasyStarUniverse_X", "Phantasy Star Universe", "Phantasy Star Universe Model | 31 Aug 2006"),
    ("SonicRiders_X", "Sonic Riders", "Sonic Riders Model | 21 Feb 2006"),
)

zn_list = (
    ("TransformersHumanAlliance_Z", "Transformers: Human Alliance", "Transformers Human Alliance Model | 2013"),
    # 1.01.06
    # nn Ver 1.01.06 Build:Aug 28 2013 14:10:27
    # SEGA NN Library for DirectX G2.0

    # K.O. Drive
    # 1.01.06
    # nn Ver 1.01.06 Build:Mar  1 2013 16:40:02
    # SEGA NN Library for DirectX G2.0

    # Sonic 4 Episode 2
    # 1.01.06
    # nn Ver 1.01.06 Build:Mar  4 2012 18:46:50
    # SEGA NN Library for DirectX G2.0
    ("Sonic4Episode1_Z", "Sonic 4 Ep 1", "Sonic 4 Episode 1 Model | 7 Oct 2010"),
    # UNKNOWN
    ("SegaGoldenGun_Z", "Sega Golden Gun", "Sega Golden Gun Model | 2010"),
    # 1.01.06
    # nn Ver 1.01.06 Build:Dec 10 2010 17:09:04
    # SEGA NN Library for DirectX G2.0

    # Let's Go Safari
    # 1.01.06
    # nn Ver 1.01.06 Build:Jun 26 2009 08:18:57
    # SEGA NN Library for DirectX G2.0

    # Super Monkey Ball Ticket Blitz
    # 1.01.06
    # nn Ver 1.01.06 Build:Jun 26 2009 08:18:57
    # SEGA NN Library for DirectX G2.0
)


determine_bone = {
    # Functions
    "Match__": 1,
    # Formats
    "HouseOfTheDead4_C": 2,
    "SonicTheHedgehog4EpisodeI_C": 2,
    "SonicTheHedgehog4EpisodeII_C": 2,

    "SonicFreeRiders_E": 0.5,
    "SonicTheHedgehog4EpisodeIPrototype_E": 2,

    "SuperMonkeyBallStepAndRoll_G": 1,
    "SonicAndTheBlackKnight_G": 1,
    "GhostSquad_G": 0.5,
    "SonicUnleashed_G": 0.5,
    "SonicRidersZeroGravity_G": 0.5,
    "SonicAndTheSecretRings_G": 1,
    "BleachShatteredBlade_G": 1,
    "SuperMonkeyBallBananaBlitz_G": 1,
    "SonicRiders_G": 0.5,

    "SonicTheHedgehog4EpisodeI_I": 1,
    "SonicTheHedgehog4EpisodeIPre2016_I": 1,

    "SonicTheHedgehog4EpisodeII_L": 2,
    "SonicTheHedgehog4EpisodeIIOuya_L": 2,
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
