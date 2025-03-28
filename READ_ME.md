____________________________________________________________________________________

        ██████╗ ██╗  ██╗███████╗         ██████╗  ██████╗ ████████╗    
        ██╔══██╗╚██╗██╔╝██╔════╝         ██╔══██╗██╔═══██╗╚══██╔══╝    
        ██║  ██║ ╚███╔╝ █████╗           ██████╔╝██║   ██║   ██║       
        ██║  ██║ ██╔██╗ ██╔══╝           ██╔══██╗██║   ██║   ██║       
        ██████╔╝██╔╝ ██╗██║    ███████╗  ██████╔╝╚██████╔╝   ██║       
        ╚═════╝ ╚═╝  ╚═╝╚═╝    ╚══════╝  ╚═════╝  ╚═════╝    ╚═╝
                                         v1.0 Michael Schiebler 2025
____________________________________________________________________________________


This bot tries to turn a picture (eg. a hand drawn sketch with dimension), an audio description or a text description into a DXF file.

CLIENT SIDE USAGE: 
        /start gives a welcome message as standard for telegram bots
	/help gives info about available commands
	/draw command needs an argument eg. "/draw a face"
	send image + optional caption
	send audio. Works in various languages as llm is multilingual
	
____________________________________________________________________________________

SERVER SIDE USAGE:

- Nothing will run unless you open config.py and add your API keys first
- Main script handles bot server. It must run at all times in order for the bot to respond.
- "config.py" contains environment variables. Most can be left as default. All variables have comments describing their usage.
   IMPORTANT: API keys must be provided from both telegram and openAI, the default ones are placeholders.
	
-JSON schema inside config.py:
  -The schema describes what constitutes valid output for the llm. A custom parser then turns the JSON outputted by the llm
   (found in log) into a DXF
  -JSON schema descriptions get passed to llm and are important in its comprehension of the schema. 
  -JSON parser may not be able to handle changes made to the schema

-Prompts inside config.py: 
  Self explanatory, can be tweaked to get better results
