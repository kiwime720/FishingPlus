import csv
import os

def get_fishingPlace(type):
    csv_path = os.path.join(os.path.dirname(__file__), 'fishingPlaceData.csv')

    with open(csv_path, newline='', encoding='utf-8') as data:
        reader = csv.DictReader(data)

        target_col = ['낚시터명', '소재지도로명주소', '소재지지번주소', 'WGS84위도', 'WGS84경도']

        result = []
        for row in reader:
            if type != None:
                if type == 'sea' and row['낚시터유형'] != '바다':
                    continue
                elif type == 'ground' and row['낚시터유형'] == '바다':
                    continue

            filtered_row = {}
            for key in target_col:
                if key in row:
                    if (key == 'WGS84위도' or key == 'WGS84경도') and row[key] != '':
                        filtered_row[key] = float(row[key])
                    else:
                        filtered_row[key] = row[key]
            result.append(filtered_row)
        return result