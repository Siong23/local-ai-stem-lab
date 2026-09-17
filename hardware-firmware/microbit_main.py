from microbit import *
import music
 
# Version 1.2: no JSON library required on the micro:bit.
speaker.on()
uart.init(baudrate=115200)
display.show(Image.YES)
sleep(700)
display.clear()
 
ICONS = {
    "HAPPY": Image.HAPPY,
    "SAD": Image.SAD,
    "YES": Image.YES,
    "NO": Image.NO,
    "HEART": Image.HEART,
    "SURPRISED": Image.SURPRISED,
    "ASLEEP": Image.ASLEEP,
}
 
 
def reply(request_id, status, values):
    fields = [request_id, status] + [str(value) for value in values]
    uart.write("|".join(fields) + "\n")
 
 
def handle_line(raw):
    request_id = "0"
    try:
        fields = raw.decode("utf-8").split("|")
        candidate = fields[0]
        if not 1 <= len(candidate) <= 32:
            raise ValueError("BAD_ID")
        for char in candidate:
            if char not in "0123456789abcdef":
                raise ValueError("BAD_ID")
        request_id = candidate
        if len(fields) < 2:
            raise ValueError("BAD_FIELDS")
        action = fields[1]
        count = 3 if action == "I" else 4 if action == "N" else 2
        if len(fields) != count:
            raise ValueError("BAD_FIELDS")
 
        if action == "P":
            values = ["PONG", "1.2"]
        elif action == "L":
            values = [display.read_light_level()]
        elif action == "T":
            values = [temperature()]
        elif action == "A":
            values = list(accelerometer.get_values())
        elif action == "B":
            values = [int(button_a.is_pressed()), int(button_b.is_pressed())]
        elif action == "I":
            icon_name = fields[2]
            if icon_name not in ICONS:
                raise ValueError("BAD_ICON")
            display.show(ICONS[icon_name])
            values = [icon_name]
        elif action == "C":
            display.clear()
            values = ["CLEARED"]
        elif action == "N":
            frequency, duration = int(fields[2]), int(fields[3])
            if not 100 <= frequency <= 2000 or not 50 <= duration <= 2000:
                raise ValueError("TONE_BOUNDS")
            music.pitch(frequency, duration, wait=True)
            values = [frequency, duration]
        else:
            raise ValueError("BAD_ACTION")
        reply(request_id, "OK", values)
    except ValueError:
        reply(request_id, "ERR", ["BAD_COMMAND"])
    except Exception:
        reply(request_id, "ERR", ["DEVICE_ERROR"])
 
 
# Keep partial reads until LF; reject an oversized line as a whole.
buffer = bytearray()
discard = False
 
 
def feed(data):
    global buffer, discard
    for value in data:
        if value == 126:  # Reserved ~ marker resets line assembly.
            buffer = bytearray()
            discard = False
        elif value == 10:
            if discard:
                reply("0", "ERR", ["BAD_FRAME"])
            elif buffer:
                handle_line(bytes(buffer))
            buffer = bytearray()
            discard = False
        elif value == 13:
            continue  # Accept CRLF as well as LF.
        elif not discard:
            if value < 32 or value > 126 or len(buffer) >= 60:
                buffer = bytearray()
                discard = True
            else:
                buffer.append(value)
 
 
while True:
    data = uart.read()
    if data:
        feed(data)
    else:
        sleep(1)
