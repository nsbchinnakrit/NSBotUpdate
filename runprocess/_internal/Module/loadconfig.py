import os
import json

config = {}

def load_config(config_file):
    if os.path.exists(config_file):
        with open(config_file) as file:
            config = json.load(file)
            return config
    else:
        raise FileNotFoundError("File not found.")

config_file = "config.json"  # ตำแหน่งของไฟล์ config.json

try:
    config = load_config(config_file)
    print("Config loaded successfully.")
    # print("Config:", config)
except FileNotFoundError as e:
    print("Error:", str(e))