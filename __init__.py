'''
Copyright (C) 2022 Darkness
amir008hosein@gmail.com

Created by Darkness
'''

bl_info = {
    "name": "RE Engine Model Utilities",
    "description": "Can be used to import and set up models from RE Engine, "
                   "special thanks to galen for making the shaders",
    "author": "Darkness, galen",
    "version": (1, 0, 0),
    "blender": (3, 3, 1),
    "location": "3D Viewport and Node Editor",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Import - Node" }


# Load the modules
from . import UI
from . import CustomNodes

# Register
import traceback

def register():
    try:
        UI.Register()
        CustomNodes.Register()
    except: traceback.print_exc()

def unregister():
    try:
        UI.Unregister()
        CustomNodes.Unregister()
    except: traceback.print_exc()