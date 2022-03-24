import csv
# import gspread
# import json
# from oauth2client.service_account import ServiceAccountCredentials

# class SpreadSheet:
#     def __init__(self, json_path, key):
#         scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
#         credentials = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
#         gc = gspread.authorize(credentials)
#         self.ws = gc.open_by_key(key).get_worksheet(0)

#     def get_last_row(self):
#         return len(list(filter(None, self.ws.col_values(1)))) + 1

#     def write_log(self, *args):
#         row = self.get_last_row()
#         self.ws.append_row([*args])

class CSV:
    def __init__(self, path):
        self.path = path

    def write_log(self, *args):
        with open(self.path, 'a') as f:
            writer = csv.writer(f)
            writer.writerow([*args])

class Logger:
    pass