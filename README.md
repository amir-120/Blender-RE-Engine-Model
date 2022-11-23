# Blender-RE-Engine-Model

## Note
In collaboration with Galen I decided to automate the process of importing and setting up RE Engine assets at the moment this addon only has been tested on DMC5 and can only import assets not export.

## How to Install & Use
### Installing
You need Blender 3.3.1 or newer as that is the version I developed this on
First you need to install the addon download the latest version here: https://github.com/amir-120/Blender-RE-Engine-Model/releases
In Blender go to Edit->Preferences->Add-ons->Install and select the zip file and it should now install the addon
Make sure it is enabled (The checkbox should be like this):

![image](https://user-images.githubusercontent.com/18630540/203515093-5d40c817-e325-4272-9872-092be7b3db4f.png)

Now that the add-on is intalled and enabled it will add few tools in Blender that we use:
Access the side panel by pressing the N (default key) in a 3d view port on your keyboard, a new menu should now be added to it called "RE Engine Mesh" select a mesh and if you want an MDF file (hold the control button for multi file selection) and configure the options to your liking and press the "Import" button at the bottom of the menu

![image](https://user-images.githubusercontent.com/18630540/203517040-3efdf424-c95a-4baa-9614-86eb27cd9ad7.png)

![image](https://user-images.githubusercontent.com/18630540/203520052-748920d3-22ef-4463-baf1-fe3a11bec9c5.png)

*Note that if you want to import the materials you need to select the MDF file that you want to load the materials from and the MDF file must be in a subdirectory of the "X64" folder that contains the textures in the correct path for that you can just use the unedited folder structure of the .pak that you have extracted or you can manually select the root folder and MDF file inside the "Material" segment when you have "Load Materials" checked*

This would import and set up the model for rendering in Eveen (Cycles not set up to work with this add-on yet) using the node system

![image](https://user-images.githubusercontent.com/18630540/203520616-2926792b-e519-4f63-9039-d0ce794acdae.png)

This add-on might not be 100% accurate to how the model looks in the game but if you want to you can tweak the values and inputs by editing the "Material Definition" node in the eidtor to your likings

![image](https://user-images.githubusercontent.com/18630540/203521328-523ebc41-fa72-4be7-923d-080516676165.png)

This addon adds two set of nodes that can be used for manually setting up models
The "RE Engine Shaders" is a set of output shaders that goe to the material output

![image](https://user-images.githubusercontent.com/18630540/203521679-b04141a3-ccfa-4d3b-a655-d9cad1896043.png)

The "RE Engine Nodes" is a set of nodes that can be used for specific materials like the wrinkle maps used for skin materials

![image](https://user-images.githubusercontent.com/18630540/203522246-d5fd4c1d-011c-41c5-ba44-4c2ff778772c.png)

The add-on by default uses the "RE Engine Dynamic Shader" shader node because it can be changed to any of the other shaders on demand and you can automatically connect nodes using the "Autoconnect" feature by selecting the shader node and pressin the button

![image](https://user-images.githubusercontent.com/18630540/203522611-314366b1-97b3-44cc-857e-f016dc3beebd.png)

# Important
This add-on does not support automation for setting up specific types of materials including the emissive materials such as the devil trigger materials, orb materials such as the gem on the DSD's hilt
This only effects the automatic material settup as there are no shaders for the items mentioned above but you can set them up manually using your own shaders or Blender's default shaders like the "Principled BSDF"
