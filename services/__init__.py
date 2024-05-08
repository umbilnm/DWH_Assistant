from dotenv import load_dotenv
import os
load_dotenv()

from ruamel.yaml import YAML
strings_path = os.getenv('STRINGS_PATH') 
yaml = YAML()
with open(strings_path, 'r') as f:
    strings =yaml.load(f)

