from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from local_settings import API_KEY

def _get_if_exist(data, key):
    if key in data:
        return data[key]
    return None

def _convert_to_degress(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    d = value[0]

    m = value[1]

    s = value[2]

    return d + (m / 60.0) + (s / 3600.0)

def get_exif_data(image):
    """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
    exif_data = {}
    info = image.getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]

                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value

    return exif_data


def write_html_doc(script, API_KEY=API_KEY):
    return """
<!DOCTYPE html>
<html>
  <head>
    <style>
      div#map {position: static !important;}""".strip() + f"""
    </style>
    <title>Info Window With maxWidth</title>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=default"></script>
    <link rel="stylesheet" type="text/css" href="./style.css" />
    <script src="./{script}"></script>
  </head>
  <body>
    <!-- Async script executes immediately and must be after any DOM elements used in callback. -->
    <script
      src="https://maps.googleapis.com/maps/api/js?key={API_KEY}&callback=initMap&libraries=&v=weekly"
      async
    ></script>
    <div id="map"></div>
  </body>
</html>""".strip()