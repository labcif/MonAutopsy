import json, pprint, os
from pprint import pprint


with open(os.path.dirname(__file__) + '\\config.json') as f:
	config = json.load(f)

pprint(config['cpu_usage']['max'])