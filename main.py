import csv
from pathlib import Path
from typing import List, Optional
from geopy.geocoders import Nominatim
import folium

def read_csv_file (input_file: str)->List[List[str]]:
    return [row for row in csv.reader(Path(input_file).read_text(encoding="utf-8").splitlines(),delimiter=',')]

def the_biggest(file_header: List[str], file_content: List[List[str]]):
    geolocator = Nominatim(user_agent="as")
    time_index = file_header.index("time")
    x_cords = file_header.index("latitude")
    y_cords = file_header.index("longitude")
    depth = file_header.index("mag")
    combined = list(map((lambda place : [place[x_cords],place[y_cords]]),sorted(file_content,key=lambda el: el[depth],reverse=True)))[:5]
    adres = [geolocator.reverse(combined[i],language="en") for i in range (5)]
    trzesienia = list(map((lambda place : ["czas: "+place[time_index],"sila: "+place[depth]]),sorted(file_content,key=lambda el: el[depth],reverse=True)))[:5]
    for i in range(5):
        if adres[i] is not None:
            print(f"{trzesienia[i]} {adres[i]}")
        else:
            print(f"{trzesienia[i]} brak danych o lokalizacji")
        print()


def count_by_year(file_header: List[str], file_content: List[List[str]], year:str, month:Optional [str]=None, day: Optional [str]=None):
    time_index = file_header.index("time")
    new_data=[]
    locations = list(map(lambda data: [data[time_index][:10]], file_content))
    new_data = list(filter(lambda data: data[0][:4]==year,locations))
    if month is not None:
        new_data = list(filter(lambda data: data[0][5:7]==month,new_data))
    if day is not None:
        new_data = list(filter(lambda data: data[time_index][0][8:10]==day,new_data))

    if not new_data:
        print("brak danych")
        exit(1)
    return new_data

def find_near_earthquake(file_header: List[str], file_content: List[List[str]], place: Optional[str]=None,cords: Optional[str]=None):
    geolocator = Nominatim(user_agent="as")
    x_cords = file_header.index("latitude")
    y_cords = file_header.index("longitude")

    count=10
    if place is None:
        coordinates = cords.split(",")
        coordinates = [float(i) for i in coordinates]
        adres = geolocator.reverse(cords,language="en")
        if adres is None:
            print("brak danych o polozeniu")
            exit(1)
        adres=adres[0].split(",")
        adres=adres[-4:]
        print("Wprowadzony region: \n")
        print(adres)
        print("\nPobliskie trzesienia: \n")
        found = list(filter (lambda cords: ((float(cords[x_cords])<coordinates[0]+2 and float(cords[x_cords])>coordinates[0]-2) and
                                            ((float(cords[y_cords])<coordinates[1]+2 and float(cords[y_cords])>coordinates[1]-2))),file_content))[:count]

        for i in found:
            print(i)

    elif cords is None:
        adres = geolocator.geocode(place)
        if adres is None:
            print("brak danych o polozeniu")
            exit(1)
        print("Wprowadzony region: \n")
        print(adres)
        coordinates = [adres.latitude, adres.longitude]
        coordinates = [float(i) for i in coordinates]
        found = list(filter (lambda cords: ((float(cords[x_cords])<coordinates[0]+2 and float(cords[x_cords])>coordinates[0]-2)
                                            and ((float(cords[y_cords])<coordinates[1]+2 and float(cords[y_cords])>coordinates[1]-2))),file_content))[:count]
        for i in found:
            print(i)
def place_color(var):
    var = float(var)
    if var<2.5:
        return "lightgreen"

    if var>=2.50 and var<4:
        return "green"

    if var>=4 and var<5.5:
        return "darkgreen"

    if var>=5.5 and var<7:
        return "orange"

    if var>=7 and var<8:
        return "lightred"

    if var>=8 and var<9:
        return "red"

    if var>=9 and var<10:
        return "darkred"

def build_map(file_header: List[str], file_content: List[List[str]], year:str, month:Optional [str]=None, day: Optional [str]=None):
    time_index = file_header.index("time")
    x_cords = file_header.index("latitude")
    y_cords = file_header.index("longitude")
    magnitude = file_header.index("mag")
    new_data=[]
    locations = list(map(lambda data: [data[time_index][:10],data[x_cords],data[y_cords], data[magnitude]], file_content))
    new_data = list(filter(lambda data: data[0][:4]==year,locations))
    if month is not None:
        new_data = list(filter(lambda data: data[0][5:7]==month,new_data))
    if day is not None:
        new_data = list(filter(lambda data: data[time_index][0][8:10]==day,new_data))

    if not new_data:
        print("brak danych")
        exit(1)
    m = folium.Map(location=(22,51), zoom_start=2, tiles="Stamen Terrain")
    for i in range(len(new_data)):
        folium.Marker(
            location=[new_data[i][1],new_data[i][2]],
            icon=folium.Icon(color=place_color(new_data[i][3])),
            range=5,
            tooltip=["wspolrzedne trzesienia: "+new_data[i][1],new_data[i][2]+ " skala: "+new_data[i][3]]
        ).add_to(m)
    m.save("footprint.html")


file_content = read_csv_file("Global_Earthquake_Data.csv")
header = file_content[0]
file_content=file_content[1:]

# the_biggest(header,file_content)
# print(len(count_by_year(header,file_content,"2022",None, "19")))
# find_near_earthquake(header,file_content,None, "33, 67")
build_map(header,file_content,"2001","12",None)
