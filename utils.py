from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from local_settings import API_KEY

def _get_if_exist(data, key):
    if key in data:
        return data[key]
    return None

def _convert_to_degress(value, ref, input_type):
    """
    Convert GPS coordinates stored in EXIF to degress as a float
    """
    d = value[0]
    m = value[1]
    s = value[2]

    deg = d + (m / 60.0) + (s / 3600.0)

    if input_type == 'long':
        if ref != "E":
            deg = 0 - deg
    elif input_type == 'lat':
        if ref != "N":
            deg = 0 - deg

    return deg

def get_exif_data(image):
    """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, values in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in values:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = values[t]

                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = values

    return exif_data


def write_html_doc(script, f, API_KEY=API_KEY):
    output = """
<!DOCTYPE html>
<html>
  <head>
    <style>
        div#body {position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                bottom: 0 !important;
                right: 0 !important;
                overflow: auto !important; }
        div#map {position: initial !important;}""".strip() + f"""
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
    <div id="body">
        <div id="map"></div>
    </div>
  </body>
</html>""".strip()

    f.write(output)