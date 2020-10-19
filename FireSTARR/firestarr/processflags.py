"""Priority flags for subprocess"""
# https://stackoverflow.com/questions/46849574/start-process-with-low-priority-popen
## Run with 'Above Normal' priority
ABOVE_NORMAL_PRIORITY_CLASS = 0x00008000
## Run with 'Below Normal' priority
BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
## Run with 'High' priority
HIGH_PRIORITY_CLASS         = 0x00000080
## Run with 'Idle' priority
IDLE_PRIORITY_CLASS         = 0x00000040
## Run with 'Normal' priority
NORMAL_PRIORITY_CLASS       = 0x00000020
## Run with 'Realtime' priority
REALTIME_PRIORITY_CLASS     = 0x00000100
## Do not create a window while running
CREATE_NO_WINDOW            = 0x08000000
