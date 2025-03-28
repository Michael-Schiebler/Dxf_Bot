"""
DXF_bot v1.0.0
Copyright (c) 2025 Michael Schiebler
Licensed under CC BY-NC 4.0 (Non-Commercial)
See LICENSE.txt for details.
"""

print("─" * 75, flush=True)
print("""

        ██████╗ ██╗  ██╗███████╗         ██████╗  ██████╗ ████████╗    
        ██╔══██╗╚██╗██╔╝██╔════╝         ██╔══██╗██╔═══██╗╚══██╔══╝    
        ██║  ██║ ╚███╔╝ █████╗           ██████╔╝██║   ██║   ██║       
        ██║  ██║ ██╔██╗ ██╔══╝           ██╔══██╗██║   ██║   ██║       
        ██████╔╝██╔╝ ██╗██║    ███████╗  ██████╔╝╚██████╔╝   ██║       
        ╚═════╝ ╚═╝  ╚═╝╚═╝    ╚══════╝  ╚═════╝  ╚═════╝    ╚═╝
                                               v1.0 - CC BY-NC 4.0
                                            Michael Schiebler 2025
        """, flush=True)
print("─" * 75, flush=True)
print("\n")
print("Loading...",end="\r")


import openai
import telebot
import os
import ezdxf
from ezdxf.math import ConstructionArc, Vec2
from ezdxf.render import forms
from math import radians
from base64 import b64encode
from time import sleep
import json
import io


#imports [TelegramTOKEN,  llm_model,   OpenAIkey,  debug_mode,  schema, image_detail, layercolor, startfile etc
with open("config.py") as c:
    exec(c.read())  # Not ideal

bot = telebot.TeleBot(TelegramTOKEN)
openai.api_key = OpenAIkey


def text_to_feature_list(text):
    completion = openai.chat.completions.create(
        model=llm_model,
        n=1,
        temperature=0.2,
        response_format={"type": "json_schema", "json_schema": schema},
        messages=[
            {"role": "developer", "content": text_prompt},
            {
                "role": "user",
                "content": text
            }
        ],

    )

    # Extract code from the response
    json_list = completion.choices[0].message.content
    
    #display cost of call
    print_cost(completion.usage.completion_tokens, completion.usage.prompt_tokens)
    #log response
    log_output(json_list)
    
    return json_list

def image_to_feature_list(image, caption):
    completion = openai.chat.completions.create(
        model=llm_model,
        n=1,
        temperature=0.2,
        response_format={"type": "json_schema", "json_schema": schema},
        messages=[
            {"role": "developer", "content": img_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": caption},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image}",
                            "detail": image_detail, 
                        },
                    },
                ],
            }
        ],

    )

    # Extract code from the response
    json_list = completion.choices[0].message.content
    
    #display cost of call
    print_cost(completion.usage.completion_tokens, completion.usage.prompt_tokens)
    # log response
    log_output(json_list)
    
    return json_list

def log_output(string):
    # log response
    log_path = "log/llm_out.JSON"
    # Ensure the directory exists before writing the file
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "w") as f:
        f.write(str(string))
        
def print_cost(completion_tokens, prompt_tokens):
    #display cost of call
    print(f"Input tokens: {prompt_tokens}")
    print(f"Output tokens: {completion_tokens}")
    cost = round(completion_tokens*(10/1000000) + prompt_tokens*(2.5/1000000), 4)
    print(f"Cost of API call: ${cost} = {round(cost*100,2)} cents")
    

def create_dxf(json_data, output_filename):
    doc = ezdxf.new(dxfversion="AC1024")
    layers = doc.layers
    msp = doc.modelspace()
    
    # Check for thickness entry
    thickness = None       #sets default thickness
    for entity in json_data["data"]:
        if entity.get("type") == "thickness":
            thickness = entity.get("thickness", None)
            break
    
    for entity in json_data["data"]:
        entity_type = entity.get("type")
        layer = entity.get("layer", "default")
        
        if layer not in layers and layer in layer_names:   #redundant but llm can make errors
           layers.add(name=layer, color = layer_colors[layer_names.index(layer)])
            

        if entity_type == "line":
            msp.add_line(
                start=(entity["point1x"], entity["point1y"],thickness),
                end=(entity["point2x"], entity["point2y"],thickness),
                dxfattribs={"layer": layer } 
            )
            #add construction geometry
            msp.add_line(start=(entity["point1x"], entity["point1y"],0),end=(entity["point2x"], entity["point2y"],thickness),dxfattribs={"layer": "0" } )
                        
                        
        if entity_type == "len_angle_line":
            direction = Vec2.from_angle(radians(entity["angle"])) * entity["length"]
            start=Vec2(entity["point1x"], entity["point1y"],thickness)
            msp.add_line(
                start,
                end = (start + direction),
                dxfattribs={"layer": layer } 
            )
            #add construction geometry
            start=Vec2(entity["point1x"], entity["point1y"],0)
            msp.add_line( start,end = (start + direction), dxfattribs={"layer": "0" } )
            
        elif entity_type == "arc":
            msp.add_arc(
                center=(entity["centerx"], entity["centery"],thickness),
                radius=entity["radius"],
                start_angle=entity["start_angle"],
                end_angle=entity["end_angle"],
                dxfattribs={"layer": layer }
            )
            #add construction geometry
            msp.add_arc(
                center=(entity["centerx"], entity["centery"],0),
                radius=entity["radius"],
                start_angle=entity["start_angle"],
                end_angle=entity["end_angle"],
                dxfattribs={"layer": "0" }
            )
        elif entity_type == "circle":
            circle = msp.add_circle(
                center=(entity["centerx"], entity["centery"],thickness),
                radius=entity["radius"],
                dxfattribs={"layer": layer }
            )
            #add construction geometry
            circle = msp.add_circle(
                center=(entity["centerx"], entity["centery"],0),
                radius=entity["radius"],
                dxfattribs={"layer": "0" }
            )
                
        elif entity_type == "polyline":
            points = entity.get("points", [])
            close = entity.get("close", False)
            if points:
                msp.add_lwpolyline(points, close=close, dxfattribs={"layer": layer,"elevation": thickness})
                msp.add_lwpolyline(points, close=close, dxfattribs={"layer": "0", "elevation": 0 })
                 
        elif entity_type == "arc3point":
            points = entity.get("points", [])
            if points:
                arc = ConstructionArc.from_3p(points[0], points[1], points[2])     #calculate arc parameters
                msp.add_arc(center=(arc.center[0],arc.center[1],thickness), radius=arc.radius, start_angle=arc.start_angle, end_angle=arc.end_angle,dxfattribs={"layer": layer})
                 #add construction geometry
                msp.add_arc(center=arc.center, radius=arc.radius, start_angle=arc.start_angle, end_angle=arc.end_angle,dxfattribs={"layer": "0"})
            

        
    doc.saveas(output_filename)
    print(f"DXF file '{output_filename}' created successfully. \n \n")

def generate_filename():
    path = default_name + ".dxf"
    i=1
    while os.path.exists(path):
        path = default_name + "(" + str(i) + ")" + ".dxf"
        i += 1
    os.makedirs(os.path.dirname(path), exist_ok=True)   #creates the output dir if not present
    return path

# Handle the /start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message, "Send me a sketch or an audio message, and I'll try to convert it to a DXF file")
    print("Start command received \n")
    
# Handle the /help command
@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(
        message, "Send an image (with optional caption), an audio message or a '/draw' command. It will be turned into a dxf file.")
    print("Help command received \n")
    

#handle /draw + text
@bot.message_handler(commands=['draw'])
def draw(message):
    print("Received /draw command")
    # Get the arguments after the command
    args = message.text.split(maxsplit=1)
    
    # Check if there's a message 
    if len(args) > 1:
        print("'" + args[1] + "'" )
        print("Requesting JSON file from llm")
        
        llm_output = text_to_feature_list(args[1])
        
        json_data = json.loads(llm_output)
        
        filename = generate_filename()  
        create_dxf(json_data, filename)
        
        bot.send_message(message.chat.id, "Process complete. DXF file ready")
        if start_file: os.startfile(filename)
    else:
        print("Lack of arguments")
        bot.reply_to(message, "Provide more info about what you want the bot to draw eg. /draw a square'")
    

# Handle images
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_id = message.photo[-1].file_id  # Get highest quality photo
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    user_caption = message.caption or ""     # Send empty string if no caption is present, to avoid raising exceptions

    bot.reply_to(message, "Image received, processing...")

    # Convert image to Base64
    base64_image = b64encode(downloaded_file).decode('utf-8')

    print("Image received")
    print("Requesting sketch analysis...")
    llm_output = image_to_feature_list(base64_image, user_caption)
    
    #llm_output = debug
    
    json_data = json.loads(llm_output)
    
    filename = generate_filename()  
    create_dxf(json_data, filename)
    
    bot.send_message(message.chat.id, "Process complete. DXF file ready")
    if start_file: os.startfile(filename)


# Handle audio
@bot.message_handler(content_types=['voice', 'audio'])
def handle_audio(message):
    bot.reply_to(message, "Message received, processing...")
    print("Received audio message")
    
    file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
    file = bot.download_file(file_info.file_path)
    
    audio_file = io.BytesIO(file)
    audio_file.name = "audio.ogg"  # Set a name for OpenAI processing
    
    print("Requesting transcription")
    transcription = openai.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )

    transcribed_text = transcription.text
    print("'"+transcribed_text+"'")
    print("Requesting JSON file from llm")
    
    llm_output = text_to_feature_list(transcribed_text)
    
    json_data = json.loads(llm_output)
    
    filename = generate_filename()  
    create_dxf(json_data, filename)
    
    bot.send_message(message.chat.id, "Process complete. DXF file ready")
    os.startfile(filename)
        

def main():
    
    
    if debug_mode:
        print("Bot started in debug mode")
        bot.polling()
    
    # Run bot and handle errors
    else:
       while True:
            try:
                print("Bot online")
                bot.polling()

            except Exception as e:
                print(f"Error: {e}")
                for i in range(4):
                    print(f"Reconnecting in {5-i} seconds...", end='\r')
                    sleep(1)
                print("Reconnecting in 1 second...  ", end='\r')
                sleep(1)
                print("Reconnecting...              ")

if __name__ == "__main__":
    main()
