# File:     readFileScript.py
# Author:   Ben Doiron <ben.m.doiron@gmail.com>
# Github:   https://github.com/openENBY
# Date:     11 Nov 2020
# Brief:    This script reads keyboard mappings for
#           Vector infinity footpedals from a config file
#           (For use with the startFootpedals script).
# Note:     This code was written using Dragon Naturally Speaking
#           speech-to-text software.

import ConfigParser

def readFromIniFile():
    config = ConfigParser.ConfigParser()
    config.read( "./config.ini" )

    # Create a list to hold each controller.
    controllers = []

    # Check to see what controllers exist through the controllers section.
    if "controllers" in config.sections():
        for controller in config.items( "controllers" ):

            # Each controller is a key, their (true/false) value dictates whether to use them.
            if controller[ 1 ] == "true":
                print controller[ 0 ], "found"

                # Create a map to hold each controller's mapping
                mapping = []

                # Each controller has a binding for left, center, and right, as per infinity footpedal design.
                # These buttons are mapped to a specific input, using windows keyboard inputs.
                for( each_key, each_val ) in config.items( controller[ 0 ] + "_bindings" ):
                    print each_key, "=", each_val

                    # Append each key (left, center, right) to the list of mappings.
                    # Use hex to interpret ascii values from the config file.
                    mapping = mapping + [ int( each_val, 16 ) ]

                # Append the mapping list for the controller to the list of controllers.
                controllers = controllers + [ mapping ]
                print
            
        print controllers
        return controllers
                      
    else:
        print "Config file does not have [controllers] section.  Please add it."
