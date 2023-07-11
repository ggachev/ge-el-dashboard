import json
from datetime import datetime

UPLOAD_FOLDER_ROOT = r"/data/"

data = {
    "id": "",
    "meta": {
        "appliance_phase_U": {
            "type": "",
            "brand": "",
            "manufacture_year": "",
            "model_number": "",
            "voltage": "",
            "wattage": "",
            "notes": ""
        },
        "appliance_phase_V": {
            "type": "",
            "brand": "",
            "manufacture_year": "",
            "model_number": "",
            "voltage": "",
            "wattage": "",
            "notes": ""
        },
        "appliance_phase_W": {
            "type": "",
            "brand": "",
            "manufacture_year": "",
            "model_number": "",
            "voltage": "",
            "wattage": "",
            "notes": ""
        },
        "header": {
            "collection_time": "",
            "notes": "",
            "number_samples": "",
            "sampling_frequency_Hz": "",
            "ambient_temperature_celsius": "",
            "location": ""
        }
    }
}
def save_to_json(number_of_file, metadata_u, metadata_v, metadata_w, notes, number_samples, sampling_frequency, temperature, location):

    data["id"] = number_of_file

    n = 0
    for key in data["meta"]["appliance_phase_U"]:
        data["meta"]["appliance_phase_U"][key] = metadata_u[n]
        n += 1
    
    n = 0
    for key in data["meta"]["appliance_phase_V"]:
        data["meta"]["appliance_phase_V"][key] = metadata_v[n]
        n += 1

    n = 0
    for key in data["meta"]["appliance_phase_W"]:
        data["meta"]["appliance_phase_W"][key] = metadata_w[n]
        n += 1
    
    current_day_year = str(datetime.now().day) + "." + str(datetime.now().month) + "." + str(datetime.now().year)
    data["meta"]["header"]["collection_time"] = current_day_year

    data["meta"]["header"]["notes"] = notes

    data["meta"]["header"]["number_samples"] = number_samples

    #Convert s in Hz
    sampling_frequency = 1 / sampling_frequency

    data["meta"]["header"]["sampling_frequency_Hz"] = sampling_frequency

    data["meta"]["header"]["ambient_temperature_celsius"] = temperature

    data["meta"]["header"]["location"] = location

    json_string = json.dumps(data, indent=4)

    filename = UPLOAD_FOLDER_ROOT + str(number_of_file) + ".json"

    with open(filename, "w") as write_file:
        write_file.write(json_string)

def read_metadata(filepath):
    with open(filepath) as json_file:
        data = json.load(json_file)
    return data