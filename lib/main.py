import network
import time
from math import sin
from umqtt.simple import MQTTClient
from constants import consts
from machine import Pin
import utime
from picozero import RGBLED
from picozero import Speaker
from JSONHelpers import JSONHelpers
from Songs import Songs
import re
import _thread
from machine import RTC
import rp2
import sys
import utime as time
import usocket as socket
import ustruct as struct
import machine



# --- OUTPUTS ON PICO -- #

led = Pin("LED", Pin.OUT)
button = Pin(0, Pin.IN, Pin.PULL_UP)
random_LED = Pin(1, Pin.OUT)
rgb_led = RGBLED(red = 2, green = 3, blue = 4)

# 1st hour digit LEDs  - Green
led_1 = Pin(5, Pin.OUT)
led_2 = Pin(6, Pin.OUT)

# 2nd hour digit LEDs - Red
led_3 = Pin(7, Pin.OUT)
led_4 = Pin(8, Pin.OUT)
led_5 = Pin(9, Pin.OUT)
led_6 = Pin(10, Pin.OUT)

# 1st minute digit LEDs - Green
led_7 = Pin(11, Pin.OUT)
led_8 = Pin(12, Pin.OUT)
led_9 = Pin(13, Pin.OUT)

# 2nd minute digit LEDs - Yellow
led_10 = Pin(14, Pin.OUT)
led_11 = Pin(15, Pin.OUT)
led_12 = Pin(16, Pin.OUT)
led_13 = Pin(17, Pin.OUT)

# Ticker (each second) - Red
led_14 = Pin(18, Pin.OUT)

speaker = Speaker(22)

led_14.value(0)



# --- INSTANCIATE STUFF --- #
json_helpers = JSONHelpers()
saved_alarms = json_helpers.read_json_file()
songs = Songs()
rtc = RTC()



# --- CONSTANTS AND VARIABLES --- #

# Fill in your WiFi network name (ssid) and password here:
wifi_ssid = consts.WIFI_SSID
wifi_password = consts.WIFI_PASSWORD

# Adafruit IO Authentication and Feed MQTT Topic details
mqtt_host = consts.MQTT_HOST
mqtt_username = consts.MQTT_USERNAME
mqtt_password = consts.MQTT_PASSWORD
mqtt_publish_topic = consts.MQTT_PUBLISH_TOPIC
mqtt_receive_topic = consts.MQTT_RECEIVE_TOPIC

# A random ID for this MQTT Client
# It needs to be globally unique across all of Adafruit IO.
mqtt_client_id = consts.MQTT_CLIENT_ID
mqtt_client = None

RGB_RED = (255, 0, 0)
RGB_GREEN = (0, 255, 0)
RGB_BLUE = (0, 0, 255)
RGB_YELLOW = (255, 60, 0)
RGB_OFF = (0, 0, 0)

messageReceived = False
alarm_is_active = False
activated_alarms = []
clock_is_running = False
SONG_LENGTH = 32
song_length_counter = 0
has_pinged = False

# Wintertime / Summertime
GMT_OFFSET = 3600 * 2 # 3600 = 1 h (wintertime)
#GMT_OFFSET = 3600 * 2 # 3600 = 1 h (summertime)
NTP_HOST = 'pool.ntp.org'



# --- FUNCTIONS --- #

# Get time from NTP Server
def getTimeNTP():
    NTP_DELTA = 2208988800
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(NTP_HOST, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    ntp_time = struct.unpack("!I", msg[40:44])[0]
    return time.gmtime(ntp_time - NTP_DELTA + GMT_OFFSET)

# Copy time to PI Pico's RTC
def setTimeRTC():
    tm = getTimeNTP()
    rtc.datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))

def turn_off_all_leds():
    led_1.value(0)
    led_2.value(0)
    led_3.value(0)
    led_4.value(0)
    led_5.value(0)
    led_6.value(0)
    led_7.value(0)
    led_8.value(0)
    led_9.value(0)
    led_10.value(0)
    led_11.value(0)
    led_12.value(0)
    led_13.value(0)
    led_14.value(0)
    random_LED.value(0)

def turn_on_all_leds():
    for i in range(14):
        led_variable_name = "led_" + str(i + 1)
        led = globals()[led_variable_name]
        led.value(1)

def boot_up_signal():
    turn_off_all_leds()
    delay = 0.1
    number_of_leds = 14
    for i in range(14):
        led_variable_name = "led_" + str(i + 1)
        led = globals()[led_variable_name]
        led.value(1)
        time.sleep(delay)
    time.sleep(0.1)
    turn_off_all_leds()
    time.sleep(0.3)
    turn_on_all_leds()
    time.sleep(1)
    turn_off_all_leds()

def connectToWifi():
    global rgb_led
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_ssid, wifi_password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        rgb_led.color = RGB_BLUE
        time.sleep(0.5)
        rgb_led.color = RGB_OFF
        time.sleep(0.5)
    print("Connected to WiFi")
    rgb_led.color = RGB_GREEN
    time.sleep(0.2)
    rgb_led.color = RGB_OFF
    time.sleep(0.2)
    rgb_led.color = RGB_GREEN
    time.sleep(0.2)
    rgb_led.color = RGB_OFF
    time.sleep(0.2)
    rgb_led.color = RGB_GREEN
    time.sleep(0.2)
    rgb_led.color = RGB_OFF
    time.sleep(0.2)
    
# Initialize our MQTTClient and connect to the MQTT server
def initializeMQTTClient():
    mqtt_client = MQTTClient(
            client_id=mqtt_client_id,
            server=mqtt_host,
            user=mqtt_username,
            password=mqtt_password)

    mqtt_client.connect()
    
def is_24_hour_clock(time_str):
    pattern = r"^(?:[01]?[0-9]|2[0-3]):[0-5][0-9]$"
    return re.match(pattern, time_str) is not None

def alarm_already_activated(time):
    for activated_alarm in activated_alarms:
        if time == activated_alarm:
            return True    
    return False

def get_current_time():
    timestamp = rtc.datetime()
    timestring = "%04d-%02d-%02d %02d:%02d:%02d"%(timestamp[0:3] + timestamp[4:7])
    return timestring

def update_json_file():
    global saved_alarms
    saved_alarms = json_helpers.read_json_file()
    
def turn_on_led(led):
    led.value(0)
    
def get_binary_from_digit(digit):
    # print("Getting binary from digit: " + str(digit))
    if (digit == 0): return [0, 0, 0 ,0]
    if (digit == 1): return [0, 0, 0, 1]
    if (digit == 2): return [0, 0, 1, 0]
    if (digit == 3): return [0, 0, 1, 1]
    if (digit == 4): return [0, 1, 0, 0]
    if (digit == 5): return [0, 1, 0, 1]
    if (digit == 6): return [0, 1, 1, 0]
    if (digit == 7): return [0, 1, 1, 1]
    if (digit == 8): return [1, 0, 0, 0]
    if (digit == 9): return [1, 0, 0, 1]
    
    return -1
    
def display_digit_in_4_binary_lights(digit, led_1, led_2, led_3, led_4):
    digit = int(digit)
    binary_array = get_binary_from_digit(digit)
    led_1.value(binary_array[0])
    led_2.value(binary_array[1])
    led_3.value(binary_array[2])
    led_4.value(binary_array[3])

def display_digit_in_3_binary_lights(digit, led_1, led_2, led_3):
    digit = int(digit)
    binary_array = get_binary_from_digit(digit)
    led_1.value(binary_array[1])
    led_2.value(binary_array[2])
    led_3.value(binary_array[3])

def display_digit_in_2_binary_lights(digit, led_1, led_2):
    digit = int(digit)
    binary_array = get_binary_from_digit(digit)
    led_1.value(binary_array[2])
    led_2.value(binary_array[3])

def display_current_time_in_leds(current_time):
    ##print("DISPLAYING CURRENT TIME")
    ##print(current_time)
    
    # Set 1st hour digit
    display_digit_in_2_binary_lights(current_time[0], led_1, led_2)
    
    # Set hour 2nd digit
    display_digit_in_4_binary_lights(current_time[1], led_3, led_4, led_5, led_6)
    
    # Set 1st minute digit
    display_digit_in_3_binary_lights(current_time[3], led_7, led_8, led_9)
    
    # Set 2nd minute digit
    display_digit_in_4_binary_lights(current_time[4], led_10, led_11, led_12, led_13)
    
def play_song():
    global speaker
    global alarm_is_active
    speaker.play(songs.starmachine, wait = False)
    return

# So that we can respond to messages on an MQTT topic, we need a callback
# function that will handle the messages.
def mqtt_subscription_callback(topic, message):
    global rgb_led
    global messageReceived
    global alarm_is_active
    global saved_alarms
    global speaker
    global random_LED
    global song_length_counter
    #messageReceived = True
    print (f'Topic {topic} received message {message}')  # Debug print out of what was received over MQTT
    if message == b'2':
        print("Emptying json file...")
        json_helpers.empty_json_file()
        update_json_file()
        message_received_signal()
    elif message == b'1':
        print("TURN ALARM OFF!")
        random_LED.value(0)
        alarm_is_active = False
        speaker.off()
        rgb_led.color = RGB_OFF
        song_length_counter = 0
        message_received_signal()
        
    elif is_24_hour_clock(message):
        print(message + " IS A CLOCK AND CAN BE SAVED TO DATABASE")
        key = get_current_time()
        data_to_append = { key: message }
        json_helpers.append_to_json_file(data_to_append)
        update_json_file()
        message_received_signal()
    else:
        print("Yo: " + str(message) + " IS NOT A CORRECT TIME OR COMMAND AND IS DISCARDED")
        
    #print("messageReceived value in callback: ", messageReceived)
    
def message_received_signal():
    global rbg_led
    rgb_led.color = RGB_GREEN
    time.sleep(2)
    rgb_led.color = RGB_OFF
    
def run_clock():
    global clock_is_running
    global alarm_is_active
    global song_length_counter
    global SONG_LENGTH
    while clock_is_running:
        if (alarm_is_active):
            song_length_counter += 1
            if (song_length_counter >= SONG_LENGTH):
                song_length_counter = 0
                play_song()
        timestamp = rtc.datetime()
        timestring = "%04d-%02d-%02d %02d:%02d:%02d"%(timestamp[0:3] + timestamp[4:7])
        current_time = timestring[11:16]
        display_current_time_in_leds(current_time)
        led_14.toggle()
        time.sleep(1)
        
def mqtt_connect():
    global mqtt_client_id
    global mqtt_host
    global mqtt_username
    global mqtt_password
    global mqtt_subscription_callback
    mqtt_client = MQTTClient(
        client_id = mqtt_client_id,
        server = mqtt_host,
        user = mqtt_username,
        password = mqtt_password)
    mqtt_client.set_callback(mqtt_subscription_callback)
    mqtt_client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_host))
    return mqtt_client

def reconnect():
    print('Failed to connect to MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()


# --- RUN PROGRAM --- #

try:
    turn_off_all_leds()
    boot_up_signal()
    connectToWifi()

    # Set the time using RTC and start a new thread where the
    # clock is running
    setTimeRTC()
    clock_is_running = True
    _thread.start_new_thread(run_clock, ())
    mqtt_client = mqtt_connect()
    # Once connected, subscribe to the MQTT topic
    mqtt_client.subscribe(mqtt_receive_topic)
    print(mqtt_client)
    print("Connected and subscribed.")
except OSError as e:
    reconnect()
while True:
    buttonIsPressed = button.value() == 0
    if buttonIsPressed:
        rgb_led.color = RGB_BLUE
        time.sleep(4)
        if buttonIsPressed:
            rgb_led.color = RGB_RED
            time.sleep(3)
            machine.reset()
    
    timestamp = rtc.datetime()
    timestring = "%04d-%02d-%02d %02d:%02d:%02d"%(timestamp[0:3] + timestamp[4:7])
    print(timestring)
    current_time = timestring[11:16]
    
    
    if True:
        #rgb_led.color = RGB_BLUE
        #time.sleep(2)
        print(f'Waiting for messages on {mqtt_receive_topic}')
        try:
            mqtt_client.check_msg()
            #print("MessageReceived value: ", messageReceived)
            #while messageReceived:
                #rgb_led.color = RGB_GREEN
               # time.sleep(2)
                #rgb_led.color = RGB_OFF
               # time.sleep(3)
               # messageReceived = False
              ##  print(f'Waiting for messages AGAIN on {mqtt_receive_topic}')
               # time.sleep(0.1)
               # mqtt_client.check_msg()
               # time.sleep(1)
        except Exception as e:
            error_message = 'Time of error: ' + current_time + f' Error: {e}'
            print('Time of error: ' + current_time)
            print(f'Error: {e}')
            error_messages_file = open("error-messages.txt", "w")
            error_messages_file.write(error_message)
            error_messages_file.close()
            
            mqtt_client.disconnect()
            rgb_led.color = RGB_RED
            time.sleep(4)
            mqtt_client = mqtt_connect()
            # Once connected, subscribe to the MQTT topic
            mqtt_client.subscribe(mqtt_receive_topic)
            print(mqtt_client)
            print("Connected and subscribed.")
            print("Connected and subscribed AGAIN.")
            rgb_led.color = RGB_BLUE
            time.sleep(5)
            
        rgb_led.color = RGB_OFF
    time.sleep(3)
    print("Publishing....")
    mqtt_client.publish(mqtt_publish_topic, timestring)
    print("Has published!")
    if (not int(current_time[4]) % 2 == 0 and has_pinged):
        print("setting has_pinged to False")
        has_pinged = False
    
    if (int(current_time[4]) % 2 == 0 and not has_pinged):
       print("PINGING!")
       time.sleep(3)
       mqtt_client.ping()
       has_pinged = True

                    
    
    # Check if alarm should be turned on
    if not alarm_is_active:
        for alarm in saved_alarms.values():
            if (alarm == current_time) and not alarm_already_activated(alarm):
                # Alarm turns on
                print("ALARM ON")
                alarm_is_active = True
                play_song()
                random_LED.value(1)
                activated_alarms = []
                activated_alarms.append(alarm)
                break
    
    rgb_led.color = RGB_OFF
    time.sleep(3)
