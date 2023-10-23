from flask import current_app
import requests

def get_file(obj, f_key):
    obj_file = getattr(obj, f_key)
    if obj_file is None:
        return None
    url = f"{current_app.config.get('DATA_FILE_MS_URL')}/{current_app.config.get('DATA_FILE_MS_API')}/{obj_file}"
    response = requests.get(url)
    if response.status_code == 200:
        response = response.json()
        return f"{current_app.config.get('DATA_FILE_MS_URL')}{response['data']['path']}"
    return None
