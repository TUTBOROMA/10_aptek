import sys
import requests
from io import BytesIO
from PIL import Image
from config import GEOCODER_APIKEY, SEARCH_APIKEY, STATICMAP_APIKEY


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <address>")
        sys.exit(1)

    address = " ".join(sys.argv[1:])
    
    geocoder_url = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": GEOCODER_APIKEY,
        "geocode": address,
        "format": "json"
    }
    
    response = requests.get(geocoder_url, params=geocoder_params)
    if not response.ok:
        sys.exit(2)
    
    try:
        geo_data = response.json()
        toponym = geo_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        longitude, latitude = toponym["Point"]["pos"].split()
    except (KeyError, IndexError):
        sys.exit(3)

    search_url = "https://search-maps.yandex.ru/v1/"
    search_params = {
        "apikey": SEARCH_APIKEY,
        "text": "аптека",
        "ll": f"{longitude},{latitude}",
        "lang": "ru_RU",
        "type": "biz",
        "results": 10
    }
    
    response = requests.get(search_url, params=search_params)
    if not response.ok:
        sys.exit(4)
    
    features = response.json().get("features", [])[:10]
    points = []
    
    for feature in features:
        meta = feature["properties"]["CompanyMetaData"]
        coords = feature["geometry"]["coordinates"]
        color = "pm2grm"
        
        if "Hours" in meta:
            availability = meta["Hours"].get("Availabilities", [])
            if availability and availability[0].get("TwentyFourHours"):
                color = "pm2gnm"
            else:
                color = "pm2blm"
        
        points.append(f"{coords[0]},{coords[1]},{color}")
    
    map_url = "https://static-maps.yandex.ru/1.x/"
    map_params = {
        "ll": f"{longitude},{latitude}",
        "spn": "0.05,0.05",
        "l": "map",
        "pt": "~".join(points),
        "apikey": STATICMAP_APIKEY
    }
    
    response = requests.get(map_url, params=map_params)
    if response.ok:
        Image.open(BytesIO(response.content)).show()
    else:
        sys.exit(5)


if __name__ == "__main__":
    main()