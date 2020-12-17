# File:     startFootpedals.py
# Author:   Ben Doiron <ben.m.doiron@gmail.com>
# Github:   https://github.com/openENBY
# Date:     11 Nov 2020
# Brief:    This script interfaces and reads from VEC Infinity footpedals,
#           using keyboard inputs, mapped via data from the readFileScript.
# Note:     This code was written using Dragon Naturally Speaking
#           speech-to-text software.

import pywinusb.hid as hid
import ctypes
from ctypes import wintypes

# Local imports
import readFileScript

""" START MAGIC WINDOWS KEYPRESS CODE THAT I DIDN'T WRITE """
""" https://stackoverflow.com/questions/13564851/how-to-generate-keyboard-events-in-python """
user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_MOUSE    = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE     = 0x0004

MAPVK_VK_TO_VSC = 0

# msdn.microsoft.com/en-us/library/dd375731
VK_TAB  = 0x09
VK_MENU = 0x12

# C struct definitions
wintypes.ULONG_PTR = wintypes.WPARAM

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))
    
class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))
    
    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        # some programs use the scan code even if KEYEVENTF_SCANCODE
        # isn't set in dwFflags, so attempt to map the correct code.
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)
class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))
    
class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))
                
LPINPUT = ctypes.POINTER(INPUT)

def PressKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode,
                            dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
""" END WINDOWS KEYPRESS CODE THAT I DIDN'T WRITE """

# Class definition for the controller reader.
# Gets the applicable HID footpedal devices and the controller mappings from config.
class ControllerReader:
    def __init__( self ):
        # Look for footpedals with the VEC vendor ID.
        # TODO: There's an issue where the footpedals change order on reload.
        # This is fixed in the RPI version by reading them by bus order. 
        # Not yet sure if that's applicable to windows...
        filter = hid.HidDeviceFilter(vendor_id = 0x05f3)
        hid_device = filter.get_devices()
        
        # Assign the devices for later use and get the mappings from the config file.
        self.hid_devices = hid_device
        self.controller_maps = readFileScript.readFromIniFile()

# Class definition for the footpedal.
class newController:
    def __init__( self, control_map, device ):
        self.controls = control_map
        self.device = device
        
        print "Created device, opening..."
                
        # Opens the HID footpedal device for reading.
        self.device.open()
        
        # The raw data handler is called whenever a footpedal button is pressed.
        # Because of this, the data handler is non-blocking.
        self.device.set_raw_data_handler( self.readController )
        
    def readController( self, data ):
        # The controller returns inputs of 0-7 based on which footpedal(s) is down.
        # Each key is mapped via controls, so press or release that button.
        PressKey( self.controls[ 0 ] ) if( data[1] & 1 ) else ReleaseKey( self.controls[ 0 ] )
        PressKey( self.controls[ 1 ] ) if( data[1] & 2 ) else ReleaseKey( self.controls[ 1 ] )
        PressKey( self.controls[ 2 ] ) if( data[1] & 4 ) else ReleaseKey( self.controls[ 2 ] )
        
# Main
reader = ControllerReader()

# Verify that we have a correct number of controllers (as listed in our config file)
# If not, display a warning (but allow the program to continue running)
if len( reader.controller_maps ) != len( reader.hid_devices ):
    print "Error, controller and device mismatch..."

# Create a list of controllers from the found HID devices,
# passing the control map for the device in the process.
controller_list = []
for count, x in enumerate( reader.hid_devices ):
    controller_list.append( newController( reader.controller_maps[ count ], reader.hid_devices[ count ] ) )

# Non-blocking, so the program will still run in the background.
input('Press ENTER to exit')
