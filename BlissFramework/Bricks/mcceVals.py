
# hummm isn't it best to load theses values from SPEC ???

# MCCE_RANGE_LIST
# MCCE_RANGE_NB
# MCCE_RANGE_UNIT
# MCCE_GAIN_NB
# MCCE_GAIN_LIST
# MCCE_FREQ_NB
# MCCE_FREQ_LIST

# 84.CYRIL> syms MCCE*
# MCCE_DEV           MCCE_GAIN_LIST   MCCE_RANGE          MCCE_SLEEP  
# MCCE_FREQ          MCCE_GAIN_NB     MCCE_RANGE_LIST     MCCE_TYPE   
# MCCE_FREQ_LIST     MCCE_MODE        MCCE_RANGE_NB   
# MCCE_FREQ_NB       MCCE_NO          MCCE_RANGE_UNIT 
# MCCE_GAIN          MCCE_POL         MCCE_SETUPOK    


#  short     void  DevMcceSetMode
# string     void  DevMcceSetPolarity
# string     void  DevMcceSetRange
#  short     void  DevMcceSetGain
#  short     void  DevMcceSetFrequency
# string     void  DevMcceSetSource
#  short     void  DevMcceSetModNum
#   long     void  DevMcceSetLeakage
#   long     void  DevMcceSetOffset


#  MCCE_RANGE_LIST[1][0] = 1e-11
#  MCCE_RANGE_LIST[1][1] = 3e-11
#  MCCE_RANGE_LIST[1][2] = 1e-10
#  MCCE_RANGE_LIST[1][3] = 3e-10
#  
#  MCCE_RANGE_LIST[2][0] = 1e-10
#  MCCE_RANGE_LIST[2][1] = 3e-10
#  MCCE_RANGE_LIST[2][2] = 1e-9
#  MCCE_RANGE_LIST[2][3] = 3e-9
#  MCCE_RANGE_LIST[2][4] = 1e-8
#  MCCE_RANGE_LIST[2][5] = 3e-8
#  MCCE_RANGE_LIST[2][6] = 1e-7
#  MCCE_RANGE_LIST[2][7] = 3e-7
#
#  MCCE_RANGE_LIST[3][0] = 1e-8
#  MCCE_RANGE_LIST[3][1] = 3e-8
#  MCCE_RANGE_LIST[3][2] = 1e-7
#  MCCE_RANGE_LIST[3][3] = 3e-7
#  MCCE_RANGE_LIST[3][4] = 1e-6
#  MCCE_RANGE_LIST[3][5] = 3e-6
#  MCCE_RANGE_LIST[3][6] = 1e-5
#  MCCE_RANGE_LIST[3][7] = 3e-5
#  
#  MCCE_RANGE_LIST[4][0] = MCCE_RANGE_LIST[5][0] = 30
#  MCCE_RANGE_LIST[4][1] = MCCE_RANGE_LIST[5][1] = 100
#  MCCE_RANGE_LIST[4][2] = MCCE_RANGE_LIST[5][2] = 300
#  MCCE_RANGE_LIST[4][3] = MCCE_RANGE_LIST[5][3] = 1000
#  
#  MCCE_RANGE_LIST[6][0] = 1e-10
#  MCCE_RANGE_LIST[6][1] = 1e-9
#  MCCE_RANGE_LIST[6][2] = 1e-8
#  MCCE_RANGE_LIST[6][3] = 1e-7

MCCE_RANGE_LIST = [
    [     "0",     "0",     "0",     "0" ],
    [ "1e-11", "3e-11", "1e-10", "3e-10" ],
    [ "1e-10", "3e-10", "1e-09", "3e-09", "1e-08", "3e-08", "1e-07", "3e-07"],
    [ "1e-08", "3e-08", "1e-07", "3e-07", "1e-06", "3e-06", "1e-05", "3e-05"],
    [    "30",   "100",   "300", "1000"],
    [    "30",   "100",   "300", "1000"],
    [ "1e-10", "1e-09", "1e-08", "1e-07"]
]

#    MCCE_RANGE_NB[1] = 4
#    MCCE_RANGE_NB[2] = MCCE_RANGE_NB[3] = 8
#    MCCE_RANGE_NB[4] = MCCE_RANGE_NB[5] = MCCE_RANGE_NB[6] = 4

MCCE_RANGE_NB = [0, 4, 8, 8, 4, 4, 4]
   
#    MCCE_RANGE_UNIT[1] = MCCE_RANGE_UNIT[2] = MCCE_RANGE_UNIT[3] =      \
#        MCCE_RANGE_UNIT[6] = "Amper CC"
#    MCCE_RANGE_UNIT[5] = "KOhm"
#    MCCE_RANGE_UNIT[4] = "MOhm"

MCCE_RANGE_UNIT = [0, "Amper CC", "Amper CC", "Amper CC", 
                   "KOhm", "MOhm", "Amper CC"  ]
  
#    MCCE_GAIN_LIST[4][0] = MCCE_GAIN_LIST[5][0] = 1
#    MCCE_GAIN_LIST[4][1] = MCCE_GAIN_LIST[5][1] = 10
#    MCCE_GAIN_LIST[4][2] = MCCE_GAIN_LIST[5][2] = 100

#    MCCE_GAIN_NB = 3

MCCE_GAIN_NB = 3

MCCE_GAIN_LIST = [
    [],
    [],
    [],
    [],
    [ 1, 10, 100],
    [ 1, 10, 100],
    []
]

    
#    MCCE_FREQ_LIST[1][0] = MCCE_FREQ_LIST[2][0] = MCCE_FREQ_LIST[3][0] = \
#        MCCE_FREQ_LIST[6][0]= 3
#
#    MCCE_FREQ_LIST[1][1] = MCCE_FREQ_LIST[2][1] = MCCE_FREQ_LIST[3][1] = \
#        MCCE_FREQ_LIST[6][1] = 10
#
#    MCCE_FREQ_LIST[1][2] = MCCE_FREQ_LIST[2][2] = MCCE_FREQ_LIST[3][2] = \
#        MCCE_FREQ_LIST[6][2] = 100
#
#    MCCE_FREQ_LIST[1][3] = MCCE_FREQ_LIST[2][3] = MCCE_FREQ_LIST[3][3] = \
#        MCCE_FREQ_LIST[6][3] = 1000
#
#    MCCE_FREQ_NB = 4

MCCE_FREQ_NB = 4

MCCE_FREQ_LIST =  [
    [ ],
    [ 3, 10, 100, 1000],
    [ 3, 10, 100, 1000],
    [ 3, 10, 100, 1000],
    [ ],
    [ ],
    [ 3, 10, 100, 1000]
]
