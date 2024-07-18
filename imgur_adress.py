import requests


def upload_to_imgur(image_path):
    url = "https://api.imgur.com/3/upload"
    headers = {"Authorization": "Client-ID 3eed12ead2c95f7"}
    with open(image_path, "rb") as img:
        payload = {"image": img.read()}
        response = requests.post(url, headers=headers, files=payload)
        response.raise_for_status()  # Check for errors
        return response.json()['data']['link']