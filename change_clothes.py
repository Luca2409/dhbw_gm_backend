import requests
from gradio_client import Client, handle_file
from PIL import Image
import os

def change_clothes():
    # Erstellen eines Clients für die API
    client = Client("yisol/IDM-VTON")

    # Beispielhafte URLs für die Eingabebilder
    background_image_url = 'https://yisol-idm-vton.hf.space/file=/tmp/gradio/96741724e32388a6ef1ec541f0d3ae37ccac11f8/00034_00.jpg'
    garment_image_url = 'https://yisol-idm-vton.hf.space/file=/tmp/gradio/b1dc13cbbad31c37433bcbb7f85c4af4a044dd4f/04469_00.jpg'

    # Funktion zum Herunterladen der Eingabebilder zur weiteren Verwendung
    def download_image(url, save_path):
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f'Image downloaded from {url} to {save_path}')
            return save_path
        else:
            print(f'Failed to download image from {url}')
            return None

    # Lade die Bilder herunter
    background_image_path = download_image(background_image_url, 'background_image.jpg')
    garment_image_path = download_image(garment_image_url, 'garment_image.jpg')

    # Prüfe, ob die Bilder korrekt heruntergeladen wurden
    if not background_image_path or not garment_image_path:
        print("Fehler beim Herunterladen der Eingabebilder. Beende das Skript.")
    else:
        try:
            # Konfigurieren der Parameter für den API-Aufruf
            result = client.predict(
                dict={
                    "background": handle_file(background_image_path),  # Hintergrundbild
                    "layers": [],  # Liste von Ebenen (leere Liste hier)
                    "composite": None  # Kompositbild (None hier)
                },
                garm_img=handle_file(garment_image_path),  # Kleidungsbild
                garment_des="Hello!!",  # Beschreibung des Kleidungsstücks
                is_checked=True,  # Einstellung für das Checkbox-Feld "Yes"
                is_checked_crop=False,  # Einstellung für das Checkbox-Feld "Yes" zum Zuschneiden
                denoise_steps=30,  # Anzahl der Denoising-Schritte
                seed=42,  # Seed-Wert für Zufälligkeit
                api_name="/tryon"  # API-Endpunkt
            )

            # result enthält die Pfade der generierten Dateien
            output_image_path, masked_image_output_path = result

            # Ergebnisverarbeitung
            print(f'Result paths: {result}')

            # Funktion zum Speichern der Bilder als PNG
            def save_image_as_png(input_path, output_path):
                try:
                    image = Image.open(input_path)  # Bild öffnen
                    image.save(output_path, 'PNG')  # Bild als PNG speichern
                    print(f'Image saved as {output_path}')
                except Exception as e:
                    print(f'Error saving image {input_path} as PNG: {e}')

            # Verzeichnisse für die gespeicherten PNG-Bilder
            output_image_png_path = 'output_image.png'
            masked_image_output_png_path = 'masked_image_output.png'

            # Speichern der Bilder als PNG
            save_image_as_png(output_image_path, output_image_png_path)
            save_image_as_png(masked_image_output_path, masked_image_output_png_path)

            print("Bilder wurden als PNG gespeichert.")

        except Exception as e:
            print(f"An error occurred during the API call or file handling: {e}")