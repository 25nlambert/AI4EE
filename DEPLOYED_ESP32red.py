from __future__ import print_function

import datetime
import sys
import time
import bluetooth
import webbrowser

from bluepy.btle import BTLEException
from bluepy.sensortag import SensorTag
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# configurations to be set accordingly
SENSORTAG_ADDRESS = "78:E3:6D:18:3B:7A"
GDOCS_OAUTH_JSON = "ai4ee-334323-5c661ee33327.json"
GDOCS_SPREADSHEET_NAME = "AI4EE"
GDOCS_WORKSHEET_NAME = "data"
FREQUENCY_SECONDS = 54.0  # it takes about 4-5 seconds to obtain readings and upload to google sheets

#======================================================================================================

#DON'T NEED THISS????
#def rx_and_echo():
#
#    while True:
#        data = sock.recv(buf_size)
#        print(data)
#        sock.send(data)
#DON'T NEED THISS???? ^^^^^^

addr = None

if len(sys.argv) < 2:
    print("No device specified. Searching all nearby bluetooth devices for "
          "the SampleServer service...")
else:
    #addr = sys.argv[1]
    #addr = "78:E3:6D:18:3B:7A"
    print("Searching for SampleServer on {}...".format(addr))

# search for the SampleServer service
#uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
service_matches = bluetooth.find_service( name= "Sensor198" )

buf_size = 1024;

if len(service_matches) == 0:
    print("Couldn't find the SampleServer service.")
    sys.exit(0)

first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

#port=1
print("Connecting to \"{}\" on {}".format(name, host))

# Create the client socket
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((host, port))

print("Connected. Type something...")

#=======================================================================================================

def get_readings(tag):
    """Get sensor readings and collate them in a dictionary."""
    try:
        #enable_sensors(tag)
        readings = {}
        # humidity sensor
        ########readings["humidity_temp"], readings["humidity"] = tag.humidity.read()
        # barometer
        readings["baro_temp"] = data.decode('ASCII')

        # round to 2 decimal places for all readings
        readings = {key: round(value, 2) for key, value in readings.items()}
        return readings

    except BTLEException as e:
        print("Unable to take sensor readings.")
        print(e)
        return {}

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
        #if readings["humidity"] < 1 or readings["humidity"] > 99:
         #   readings["humidity"] = ''

        columns = ["baro_temp"]
        now = datetime.datetime.now()
        worksheet.append_row([now.strftime("%Y-%m-%d %H:%M:%S")] + [readings.get(col, '') for col in columns])
        print("Wrote a row to {0}".format(GDOCS_SPREADSHEET_NAME))
        return worksheet

    except Exception as e:
        # Error appending data, most likely because credentials are stale.
        # Null out the worksheet so a login is performed.
        print("Append error, logging in again")
        print(e)
        return None


def main():
    print('Connecting to {}'.format(SENSORTAG_ADDRESS)) #NEEDS REPLACING of SENSORTAG_ADDRESS
    worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME, GDOCS_WORKSHEET_NAME)

    print('Logging sensor measurements to {0}.'.format(GDOCS_SPREADSHEET_NAME))
    print('Press Ctrl-C to quit.')
    while True:

        #rx_and_echo
        data = sock.recv(buf_size)
        print(data)
        sock.send(data)

        if data == b'#':
            print("FOUND THE #")
            time.sleep(3)

        # get sensor readings
        readings = {}
        readings["baro_temp"] = data.decode('ASCII')
        if not readings:
            print("Sensor disconnected. Please Reconnect")

            continue

        # print readings
        print("Time:\t{}".format(datetime.datetime.now()))
        #print("Humidity reading:\t{}, temperature:\t{}".format(readings["humidity"], readings["humidity_temp"]))
        if data == b'$':
            webbrowser.open('http://74.75.114.195:3001/api/push/djfoGLlGk2?msg=OK&ping=')
        if data != b'#':
            worksheet = append_readings(worksheet, readings)
        # login if necessary.
        if worksheet is None:
            worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME, GDOCS_WORKSHEET_NAME)
            continue

        print()
        print("loop")
        #ORIGINAL SLEEP
        #time.sleep(FREQUENCY_SECONDS)

while True:
    if __name__ == "__main__":
        main()
