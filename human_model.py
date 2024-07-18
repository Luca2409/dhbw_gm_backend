import requests
import json
import logging
import os



def create_model(image_url):
    payload = {
        "image_url": image_url,
        "enable_pbr": True,
    }
    headers = {
        "Authorization": f"Bearer msy_ulYwM82wj8Mi3CguDMqc9OHlEy068L4u3bV0"
    }

    response = requests.post(
        "https://api.meshy.ai/v1/image-to-3d",
        headers=headers,
        json=payload,
    )
    response.raise_for_status()

    # Annahme: Die JSON-Antwort enthält ein Feld "result"
    model_id = response.json().get("result")

    if model_id:
        return model_id
    else:
        raise ValueError("Model ID not found in the response")


def get_model(task_id):
    headers = {
        "Authorization": f"Bearer msy_ulYwM82wj8Mi3CguDMqc9OHlEy068L4u3bV0"
    }

    def fetch_model(task_id):
        response = requests.get(
            f"https://api.meshy.ai/v1/image-to-3d/{task_id}",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    json_response = fetch_model(task_id)

    try:
        glb_url = json_response['model_urls']['glb']
        if not glb_url:
            raise KeyError("glb url is empty or 0")
    except KeyError as e:
        print(f"KeyError: {e}. Retrying with fallback task_id.")
        json_response = fetch_model("0190c078-e20c-7b8b-868a-0f0396c0c718")
        try:
            glb_url = json_response['model_urls']['glb']
        except KeyError as e:
            print(f"KeyError on retry: {e}")
            return None

    return glb_url


def download_glb(url):
    output_folder = "glb"
    filename = "model.glb"

    # Erstellen des Ausgabeordners, falls er nicht existiert
    os.makedirs(output_folder, exist_ok=True)

    # Vollständigen Pfad zur Ausgabedatei erstellen
    output_path = os.path.join(output_folder, filename)

    response = requests.get(url)
    response.raise_for_status()  # Überprüfen, ob die Anfrage erfolgreich war

    with open(output_path, 'wb') as file:
        file.write(response.content)