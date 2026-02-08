import json
from datetime import datetime

def convert_format_1(data):
    location_parts = data["location"].split("/")
    return {
        "deviceID": data["deviceID"],
        "deviceType": data["deviceType"],
        "timestamp": data["timestamp"],
        "location": {
            "country": location_parts[0],
            "city": location_parts[1],
            "area": location_parts[2],
            "factory": location_parts[3],
            "section": location_parts[4]
        },
        "data": {
            "status": data["operationStatus"],
            "temperature": data["temp"]
        }
    }

def convert_format_2(data):
    dt = datetime.strptime(data["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")
    timestamp_ms = int(dt.timestamp() * 1000)
    return {
        "deviceID": data["device"]["id"],
        "deviceType": data["device"]["type"],
        "timestamp": timestamp_ms,
        "location": {
            "country": data["country"],
            "city": data["city"],
            "area": data["area"],
            "factory": data["factory"],
            "section": data["section"]
        },
        "data": {
            "status": data["data"]["status"],
            "temperature": data["data"]["temperature"]
        }
    }

if __name__ == "__main__":
    with open("data-1.json") as f1:
        data1 = json.load(f1)

    with open("data-2.json") as f2:
        data2 = json.load(f2)

    unified1 = convert_format_1(data1)
    unified2 = convert_format_2(data2)

    if unified1 == unified2:
        result = unified1
    else:
        result = {
            "format_1_result": unified1,
            "format_2_result": unified2
        }

    with open("data-result.json", "w") as out_file:
        json.dump(result, out_file, indent=2)

    print("Output saved to data-result.json")
    
    