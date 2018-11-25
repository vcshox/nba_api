import json

def read_json(json_path):
	with open(json_path, 'r') as json_file:
		json_obj = json.load(json_file)
		json_file.close()
		return json_obj
		
def write_json(json_path, json_obj):
	with open(json_path, 'w') as json_file:
		json_file.write(json.dumps(json_obj, indent=2))
		json_file.close()