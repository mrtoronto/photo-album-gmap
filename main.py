import json
import numpy as np
import os
from PIL import Image
from PIL.ExifTags import TAGS
from GPSPhoto import gpsphoto
import subprocess
from constants import STYLES_STRING
from utils import (_get_if_exist, 
					_convert_to_degress, 
					get_exif_data,
					write_html_doc)


def get_coords_list(folder_name):
    """ 
    Code adopted from https://github.com/aleaf/GIS_utils 
    """

    coord_list = []
    failed_photos = {}
    photos = [f"{folder_name}/{photo}" for photo in os.listdir(folder_name)]
    for photo in photos:
        data = gpsphoto.getGPSData(photo)
        try:
            image = Image.open(photo)
            exifdata = get_exif_data(image)
        except:
            image = None
            exifdata = None


        if exifdata and "GPSInfo" in exifdata:
            gps_info = exifdata["GPSInfo"]
            gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
            gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
            gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
            gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')
            
            if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                lat = _convert_to_degress(gps_latitude)
                if gps_latitude_ref != "N":                     
                    lat = 0 - lat

                longi = _convert_to_degress(gps_longitude)
                if gps_longitude_ref != "E":
                    longi = 0 - longi
                    
                coord_list.append(((lat, longi), photo))
            
        elif data:
            lat = float(data['Latitude'])
            longi = float(data['Longitude'])

            coord_list.append(((lat, longi), photo))

        else:
            failed_photos[photo] = {'exif': exifdata, 
                                    'gps': data}

    print(f'Could not find coordinates in {len(failed_photos)}/{len(photos)} photos.')
    print(f'Successfully read {len(coord_list)}/{len(photos)} photos.')
    
    return coord_list, failed_photos


class makeMap:
    def __init__(self, centerLat, centerLng, zoom):
        self.center = (float(centerLat),float(centerLng))
        self.zoom = int(zoom)
        self.points = []
        self.STYLES_STRING = STYLES_STRING
        
    def write_line(self, f, line, tabs):
        tab_str = '\t' * tabs
        f.write(f'{tab_str}{line}\n')
        
    def draw(self, file):
        f = open(file,'w')
        self.write_line(f, 'function closeLastOpenedInfoWindow() {', 0)
        self.write_line(f, 'if (lastOpenedInfoWindow) {', 1)
        self.write_line(f, 'lastOpenedInfoWindow.close();', 2)
        self.write_line(f, '}', 1)
        self.write_line(f, '}', 0)

        self.write_line(f, 'var lastOpenedInfoWindow = new google.maps.InfoWindow({', 0)
        self.write_line(f, 'content: "",', 2)
        self.write_line(f, '});', 1)
        self.write_line(f, '', 0)

        self.write_line(f, 'function initMap(): void {', 0)
        self.drawmap(f)
        self.drawpoints(f)
        self.write_line(f, '});', 0)
        self.write_line(f, '}', 0)
        f.close()
        
    def drawmap(self, f):
        self.write_line(f, 'var infoWindow = new google.maps.InfoWindow({', 1)
        self.write_line(f, f'content: "",', 2)
        self.write_line(f, '});', 1)
        self.write_line(f, 'const center = { lat:' + str(self.center[0]) +', lng: ' + str(self.center[1]) + '}', 1)
        self.write_line(f, 'const map = new google.maps.Map(', 1)
        self.write_line(f, 'document.getElementById("map") as HTMLElement,', 2)
        self.write_line(f, '{', 2)
        self.write_line(f, f'styles: {self.STYLES_STRING},', 3)
        self.write_line(f, f'zoom: {self.zoom},', 3)
        self.write_line(f, f'center: center,', 3)
        self.write_line(f, '});', 2)
        
    def drawpoint(self, f, lat, lon, image_name, title, point_num):
        self.write_line(f, '', 0)
        self.write_line(f, 'var pos = { lat: ' + str(lat) + ', lng: ' + str(lon) + '};', 2)
        self.write_line(f, 'var marker' + point_num + ' = new google.maps.Marker({', 2)
        self.write_line(f, 'position: pos,', 3)
        self.write_line(f, 'map,', 3)
        self.write_line(f, f'title: "{title}"', 3)
        self.write_line(f, '});', 2)
        
    def addpointListener(self, f, image_name, point_num):
        self.write_line(f, 'google.maps.event.addListener(marker' + point_num + ', "click", function() {', 2)
        self.write_line(f, f'var content = \'<img style="max-width:500px" src="{image_name}">\'', 3)
        self.write_line(f, 'infoWindow.setContent(content);', 3)
        self.write_line(f, 'infoWindow.open(map, marker' + point_num + ');', 3)
        self.write_line(f, '});', 2)
        
    
        
    def drawpoints(self,f):
        self.write_line(f, 'google.maps.event.addDomListener(window, "load", function() {', 1)
        for point_num, point in enumerate(self.points):
            self.drawpoint(f,
                           point['lat'],
                           point['lng'],
                           point['img'], 
                           point['img'], 
                           str(point_num))
            self.addpointListener(f, point['img'], str(point_num))

            
    def addpoint(self, lat, lng, image_name):
        self.points.append({'lat': lat, 'lng': lng,'img' : image_name})



def main():
	picture_folder = 'cuba'

	assert os.path.exists(picture_folder), 'Make sure image folder is set properly!'

	if not os.path.exists('output'):
		os.mkdir('output')

	coord_list, failed_photos = get_coords_list(folder_name=picture_folder)

	with open(f'output/{picture_folder}_failed.json', 'w') as f:
		json.dump(failed_photos, f, indent=4, default=str)

	mymap = makeMap(np.mean([i[0][0] for i in coord_list]), 
	                np.mean([i[0][1] for i in coord_list]), 
	                10)

	for (lat, longi), image_name in coord_list:
	    mymap.addpoint(lat, longi, image_name)

	mymap.draw(f'output/{picture_folder}_map.ts')
	print(f'Created .ts file: output/{picture_folder}_map.ts')

	### Compile typescript to JS
	process = subprocess.Popen(f"tsc output/{picture_folder}_map.ts".split(), 
								stdout=subprocess.PIPE)
	output, error = process.communicate()
	print(f'Created .js file: output/{picture_folder}_map.js')

	### Create HTML file
	with open(f'output/{picture_folder}_map.html', 'w') as f:
		html = write_html_doc(f"{picture_folder}_map.js")
		f.write(html)

	print(f'Created .html file: output/{picture_folder}_map.html')


if __name__ == "__main__":
	main()