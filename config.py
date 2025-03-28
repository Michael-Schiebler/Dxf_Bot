
#  _______   __    __  ________  __                  __                                           ______   __                                         __      __                     
# |       \ |  \  |  \|        \|  \                |  \                                         /      \ |  \                                       |  \    |  \                    
# | $$$$$$$\| $$  | $$| $$$$$$$$| $$____    ______ _| $$_           _______   ______   _______  |  $$$$$$\ \$$  ______   __    __   ______   ______ _| $$_    \$$  ______   _______  
# | $$  | $$ \$$\/  $$| $$__    | $$    \  /      \   $$ \         /       \ /      \ |       \ | $$_  \$$|  \ /      \ |  \  |  \ /      \ |      \   $$ \  |  \ /      \ |       \ 
# | $$  | $$  >$$  $$ | $$  \   | $$$$$$$\|  $$$$$$\$$$$$$        |  $$$$$$$|  $$$$$$\| $$$$$$$\| $$ \    | $$|  $$$$$$\| $$  | $$|  $$$$$$\ \$$$$$$\$$$$$$  | $$|  $$$$$$\| $$$$$$$\
# | $$  | $$ /  $$$$\ | $$$$$   | $$  | $$| $$  | $$| $$ __       | $$      | $$  | $$| $$  | $$| $$$$    | $$| $$  | $$| $$  | $$| $$   \$$/      $$| $$ __ | $$| $$  | $$| $$  | $$
# | $$__/ $$|  $$ \$$\| $$      | $$__/ $$| $$__/ $$| $$|  \      | $$_____ | $$__/ $$| $$  | $$| $$      | $$| $$__| $$| $$__/ $$| $$     |  $$$$$$$| $$|  \| $$| $$__/ $$| $$  | $$
# | $$    $$| $$  | $$| $$ _____| $$    $$ \$$    $$ \$$  $$       \$$     \ \$$    $$| $$  | $$| $$      | $$ \$$    $$ \$$    $$| $$      \$$    $$ \$$  $$| $$ \$$    $$| $$  | $$
#  \$$$$$$$  \$$   \$$ \$$|      \$$$$$$$   \$$$$$$   \$$$$         \$$$$$$$  \$$$$$$  \$$   \$$ \$$       \$$ _\$$$$$$$  \$$$$$$  \$$       \$$$$$$$  \$$$$  \$$  \$$$$$$  \$$   \$$
#                          \$$$$$$                                                                            |  \__| $$                                                             
#                                                                                                              \$$    $$                                                             
#                                                                                                               \$$$$$$                                                              
                                                                                                                                                            
# DXF_bot Configuration File
# Copyright (c) 2025 Michael Schiebler
# This software is licensed under CC BY-NC 4.0 (Non-Commercial)
# See LICENSE.txt for full details.

#IMPORTANT: PLACE YOUR API KEYS HERE
TelegramTOKEN = "YOUR KEY"
OpenAIkey = "YOUR KEY"


debug_mode = False     #disables error handling
log_path = "log\\llm_output.JSON"  
start_file = True   #controls wether output file is opened after creation
default_name = "output\\output_dxf"  #default name of output file, (n) will be appended if it already exists. Dxf extension added automatically, dir created automatically
llm_model = "gpt-4o"   #must be a model with image input capabilities
image_detail = "low"   #enum low, high, resolution of image passed to llm, for actual working mechanism refer to openai API reference



layer_names = ["outer", "inner"]  #array of layer names the llm can use. 
layer_colors = [1,3,5]  #each value maps to layer_name of same array index, values given in ACI  eg.  1 = Red \ 3 = Green \ 5 = Blue  \ 0 = Black \ 256 = white
layer_description = "Use different layers as appropriate"   #If any of the layer names are not clear to the llm describe their usage here.


#______________________________________________________________________________________________________________________________________________________________


schema = {
  "name": "geometries_list",
  "schema": {
  "type": "object",
  "properties": {
    "data": {
      "type": "array",
      "description": "the data array contains all the data of the drawing, such as lines or circles or thickness value. It will be parsed by the edxf library",
      "items": {
        "anyOf": [
          {
            "type": "object",
            "description": "this objects sets the thickness of the drawing",
            "properties": {
              "type": { "type": "string", "enum": ["thickness"] },
              "thickness": { "type": "number" }
            },
            "required": ["type", "thickness"],
            "additionalProperties": False
          },
          {
            "type": "object",
            "description": "this is used to indicate a line given the coordinates of start and end points",
            "properties": {
              "type": { "type": "string", "enum": ["line"] },
              "point1x": { "type": "number" },
              "point1y": { "type": "number" },
              "point2x": { "type": "number" },
              "point2y": { "type": "number" },
              "layer": { "type": "string", "enum": layer_names },
            },
            "required": ["type", "point1x", "point1y", "point2x", "point2y", "layer"],
            "additionalProperties": False
          },
          {
            "type": "object",
            "description": "this is used to indicate a line given start coordinates, angle and length. Angle of line given in degrees, 0 aligns with the positive x axis, then the angle increases counterclockwise",
            "properties": {
              "type": { "type": "string", "enum": ["len_angle_line"] },
              "point1x": { "type": "number" },  
              "point1y": { "type": "number" },
              "angle": { "type": "number" },  
              "length": { "type": "number" },
              "layer": { "type": "string", "enum": layer_names },
            },
            "required": ["type", "point1x", "point1y", "point2x", "point2y", "layer"],
            "additionalProperties": False
          },
          {
            "type": "object",
            "description": "this is used to indicate a circle given radius and center coordinates",
            "properties": {
              "type": { "type": "string", "enum": ["circle"] },
              "centerx": { "type": "number" },
              "centery": { "type": "number" },
              "radius": { "type": "number" },
              "layer": { "type": "string", "enum": layer_names },
            },
            "required": ["type", "centerx", "centery", "radius", "layer"],
            "additionalProperties": False
          },
          {
            "type": "object",
            "description": "this draws an arc given coordinates of center and the beginning and end angle of the arc. The arc is drawn counterclockwise from the start angle to the end angle.",
            "properties": {
              "type": { "type": "string", "enum": ["arc"] },
              "centerx": { "type": "number" },
              "centery": { "type": "number" },
              "radius": { "type": "number" },
              "start_angle": { "type": "number" },
              "end_angle": { "type": "number" },
              "layer": { "type": "string", "enum": layer_names },
            },
            "required": ["type", "centerx", "centery", "radius", "start_angle", "end_angle", "layer"],
            "additionalProperties": False
          },
          {
            "type": "object",
            "description": "this draws a polyline given an array of points to connect",
            "properties": {
              "type": { "type": "string", "enum": ["polyline"] },
              "points": {
                "type": "array",
                "items": {
                  "type": "array",
                  "items": { "type": "number" },
                  "minItems": 2,
                  "maxItems": 2
                },
                "minItems": 2
              },
              "layer": { "type": "string", "enum":layer_names },
            },
            "required": ["type", "points", "layer"],
            "additionalProperties": False
          },
          {
            "type": "object",
            "description": "this draws an arc given an array of 3 points to connect, starting from first point in array, ending at the second point, passing through the third point of the array",
            "properties": {
              "type": { "type": "string", "enum": ["arc3point"] },
              "points": {
                "type": "array",
                "items": {
                  "type": "array",
                  "items": { "type": "number" },
                  "minItems": 3,
                  "maxItems": 3
                },
                "minItems": 3
              },
              "layer": { "type": "string", "enum":layer_names },
            },
            "required": ["type", "points", "layer"],
            "additionalProperties": False
          }
          
        ]
      }
    }
  },
  "required": ["data"]
}
}



img_prompt = f"""Given a technical sketch generate data describing its features in detail, a script will use the ezdxf library to turn it into a dxf file.
            The thickness object sets the thickness for the whole drawing.{layer_description}.
            Break down complex geometries into its components. Infer missing dimensions based on similar features, if a position has no dimension given
            its like to be centered or simmetrical to other features. All dimensions are in mm."""

text_prompt = f"""Given description of a technical drawing generate data describing its features in detail, a script will use the ezdxf library to turn it into a dxf file.
            The thickness object sets the thickness for the whole drawing.{layer_description}. 
            Break down complex geometries into its components. Infer missing dimensions based on similar features, if a position has no dimension given
            its like to be centered or simmetrical to other features. All dimensions are in mm."""
