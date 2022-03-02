import datetime
import sys
import time
import bluetooth

from bluepy.btle import BTLEException
from bluepy.sensortag import SensorTag
import gspread
from oauth2client.service_account import ServiceAccountCredentials

GDOCS_OAUTH_JSON = "ai4ee-334323-5c661ee33327.json"
GDOCS_SPREADSHEET_NAME = "AI4EE"
GDOCS_WORKSHEET_NAME = "data"

addr = '00001101-0000-1000-8000-00805f9b34fb'

service_matches = bluetooth.find_service( uuid=addr )

buf_size = 1024;

if len(service_matches) == 0:
    print("Couldn't find your sensor.")
    sys.exit(0)

first_match = service_matches[0]
print(service_matches[0])
#port = first_match["port"]
port = 1
print(port)
name = first_match["name"]
print(name)
#host = first_match["host"]
host = '78:E3:6D:18:59:22'
print(host)

print("Connecting to \"{}\" on {}".format(name, host))

sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

sock.connect((host, port))

print("Connected")


#GOOGLE SHEET STUFF
def login_open_sheet(oauth_key_file, spreadsheet_name, worksheet_name):
    """Connect to Google Docs spreadsheet and return the first worksheet."""
    try:
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(oauth_key_file, scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open(spreadsheet_name).worksheet(worksheet_name)
        return worksheet

    except Exception as e:
        print('Unable to login and get spreadsheet. '
              'Check OAuth credentials, spreadsheet name, '
              'and make sure spreadsheet is shared to the '
              'client_email address in the OAuth .json file!')
        print('Google sheet login failed with error:', e)
        sys.exit(1)


def append_readings(worksheet, readings):
    """Append the data in the spreadsheet, including a timestamp."""
    try:
        # remove erroneous readings
        if readings["humidity"] < 1 or readings["humidity"] > 99:
            readings["humidity"] = ''

        columns = ["9808temp", "1080temp", "humidity"]
        now = datetime.datetime.now()
        #worksheet.append_row([now.strftime("%Y-%m-%d %H:%M:%S")], temp,humidity,pressure)
        worksheet.append_row([now.strftime("%Y-%m-%d %H:%M:%S")] + [readings.get(col, '') for col in columns])
        print("Wrote a row to {0}".format(GDOCS_SPREADSHEET_NAME))
        return worksheet

    except Exception as e:
        # Error appending data, most likely because credentials are stale.
        # Null out the worksheet so a login is performed.
        print("Append error, logging in again")
        print(e)
        return None

def get_readings(sensor):
    readings = {}
    data = sock.recv(buf_size)
    #readings[sensor] = data.decode('ASCII')
    readings["9808temp", "1080temp", "humidity"] = data.decode('ASCII')

    if not readings:
        print("Sensor disconnected. Please Reconnect")

        #continue

def main():
    print('Connecting to {}'.format(name)) #NEEDS REPLACING of SENSORTAG_ADDRESS
    worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME, GDOCS_WORKSHEET_NAME)

    print('Logging sensor measurements to {0}.'.format(GDOCS_SPREADSHEET_NAME))
    print('Press Ctrl-C to quit.')

    while True:
        data = sock.recv(buf_size)
        print(data)
        sock.send(data)

        if data == b'#':
            print("FOUND THE #")
            time.sleep(10)

        tempList = list(data)
        print(type(tempList))

        #print('The array is ',len(tempList))
        #if tempList[i] == '#':
        #print("this is the index 0")
        #print(tempList[0])

        readings = {"9808temp":0, "1080temp":0, "humidity":0}
        #readings["9808temp", "1080temp", "humidity"] = data.decode('ASCII')
        worksheet = append_readings(worksheet, readings)
        #get_readings("9808temp")
        #time.sleep(3)
        #get_readings("1080temp")
        #time.sleep(3)
        #get_readings("humidity")
        #time.sleep(3)

        print("Time:\t{}".format(datetime.datetime.now()))

        print()
        print("loop")


while True:
    if __name__ == "__main__":
        main()
