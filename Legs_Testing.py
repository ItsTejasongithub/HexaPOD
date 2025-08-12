from flask import Flask, request, render_template_string
from adafruit_servokit import ServoKit
import RPi.GPIO as GPIO
import traceback

app = Flask(__name__)

# Setup PCA9685 for 16 channels
kit = ServoKit(channels=16)

# Define your physical pins for GPIO servos (BOARD numbering)
PHYSICAL_PINS = [11, 13, 15]  # Physical pins on Raspberry Pi header

# Function to convert physical pins to BCM pins (used if mode is BCM)
PHYSICAL_TO_BCM = {
    11: 17,
    13: 27,
    15: 22
}

def convert_physical_to_bcm(pin_list):
    return [PHYSICAL_TO_BCM.get(pin, pin) for pin in pin_list]

# Setup GPIO mode safely
if GPIO.getmode() is None:
    GPIO.setmode(GPIO.BOARD)
    gpio_mode = GPIO.BOARD
    print("GPIO mode set to BOARD")
else:
    gpio_mode = GPIO.getmode()
    print(f"GPIO mode already set to {gpio_mode}")

# Determine pins to use based on mode
if gpio_mode == GPIO.BOARD:
    gpio_pins = PHYSICAL_PINS
elif gpio_mode == GPIO.BCM:
    gpio_pins = convert_physical_to_bcm(PHYSICAL_PINS)
else:
    raise RuntimeError("Unsupported GPIO mode")

# Setup PWM for GPIO servos
PWM_FREQ = 50  # 50 Hz for servos
gpio_pwms = []

for pin in gpio_pins:
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, PWM_FREQ)
    pwm.start(7.5)  # Middle position ~90 degrees
    gpio_pwms.append(pwm)

def angle_to_duty_cycle(angle):
    return 2.5 + (angle / 180.0) * 10

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Servo Control</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 30px; }
        h2 { color: #333; }
        label { display: block; margin-top: 15px; }
        input[type=range] { width: 300px; }
        .channel { margin-bottom: 20px; }
        .angle { font-weight: bold; }
    </style>
    <script>
        function updateAngleDisplay(channel) {
            var slider = document.getElementById('servo' + channel);
            var display = document.getElementById('angle' + channel);
            display.innerText = slider.value + '°';

            fetch('/move_servo?channel=' + channel + '&angle=' + slider.value)
                .then(response => response.json())
                .then(data => {
                    if(data.status !== 'success') {
                        alert('Error: ' + data.message);
                    }
                })
                .catch(error => {
                    alert('Request failed: ' + error);
                });
        }
    </script>
</head>
<body>
    <h2>Servo Control</h2>

    <h3>PCA9685 Servos (Channels 0,1,2)</h3>
    {% for ch in pca_channels %}
    <div class="channel">
        <label for="servo{{ch}}">Servo Channel {{ch}} (PCA9685): <span id="angle{{ch}}" class="angle">90°</span></label>
        <input type="range" min="0" max="180" value="90" id="servo{{ch}}" oninput="updateAngleDisplay({{ch}})">
    </div>
    {% endfor %}

    <h3>GPIO Servos ({{gpio_mode_name}} pins {{ gpio_pins|join(', ') }})</h3>
    {% for idx, pin in enumerate(gpio_pins) %}
        {% set idx_plus = idx + 3 %}
        <div class="channel">
            <label for="servo{{idx_plus}}">Servo GPIO Pin {{pin}}: <span id="angle{{idx_plus}}" class="angle">90°</span></label>
            <input type="range" min="0" max="180" value="90" id="servo{{idx_plus}}" oninput="updateAngleDisplay({{idx_plus}})">
        </div>
    {% endfor %}
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(
        HTML,
        pca_channels=[0,1,2],
        gpio_pins=gpio_pins,
        gpio_mode_name="BOARD" if gpio_mode == GPIO.BOARD else "BCM",
        enumerate=enumerate
    )

@app.route('/move_servo')
def move_servo():
    try:
        channel_str = request.args.get('channel')
        angle_str = request.args.get('angle')

        if channel_str is None or angle_str is None:
            return {"status": "error", "message": "Missing channel or angle parameter"}, 400

        channel = int(channel_str)
        angle = int(angle_str)

        if not (0 <= angle <= 180):
            return {"status": "error", "message": f"Angle {angle} out of range (0-180)"}, 400

        if channel in [0, 1, 2]:
            kit.servo[channel].angle = angle
            return {"status": "success", "channel": channel, "angle": angle}

        elif channel in [3, 4, 5]:
            gpio_index = channel - 3
            if gpio_index >= len(gpio_pwms):
                return {"status": "error", "message": f"Invalid GPIO servo channel {channel}"}, 400
            duty_cycle = angle_to_duty_cycle(angle)
            gpio_pwms[gpio_index].ChangeDutyCycle(duty_cycle)
            return {"status": "success", "channel": channel, "angle": angle}

        else:
            return {"status": "error", "message": f"Invalid channel {channel}. Allowed: 0-5"}, 400

    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": str(e)}, 400

@app.route('/shutdown')
def shutdown():
    GPIO.cleanup()
    return "GPIO cleaned up and server shutting down."

if __name__ == '__main__':
    print("Starting servo web control server...")
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        GPIO.cleanup()
