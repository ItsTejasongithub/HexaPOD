#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <ArduinoJson.h>
#include <ArduinoOTA.h>
#include <Update.h>

// WiFi Credentials
const char *ssid = "10xTC-AP2";
const char *password = "10xTechClub#";

// PCA9685 setup
#define PCA9685_ADDRESS 0x40
#define SDA_PIN 21
#define SCL_PIN 22
#define SERVO_FREQ 50  // Analog servos run at ~50 Hz updates

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(PCA9685_ADDRESS);
WebServer server(80);

// Servo configuration
#define NUM_SERVOS 18
#define SERVO_MIN 150   // Minimum pulse width (out of 4096)
#define SERVO_MAX 600   // Maximum pulse width (out of 4096)


void standUp();
void sitDown();


// Current servo positions (in degrees 0-180)
int servoPositions[NUM_SERVOS];

// OTA Update variables
bool otaInProgress = false;
String otaStatus = "Ready";

// Convert angle to PWM value
uint16_t angleToPWM(int angle) {
  return map(constrain(angle, 0, 180), 0, 180, SERVO_MIN, SERVO_MAX);
}

// Initialize all servos to center position
void initServos() {
  for (int i = 0; i < NUM_SERVOS; i++) {
    servoPositions[i] = 90;  // Center position
    pwm.setPWM(i, 0, angleToPWM(90));
  }
  delay(500);
}

// Setup OTA
void setupOTA() {
  // Port defaults to 3232
  ArduinoOTA.setPort(3232);

  // Hostname defaults to esp32-[MAC]
  ArduinoOTA.setHostname("ESP32-ServoController");

  // Set password for OTA updates (optional but recommended)
  ArduinoOTA.setPassword("servo123");

  ArduinoOTA.onStart([]() {
    String type;
    if (ArduinoOTA.getCommand() == U_FLASH)
      type = "sketch";
    else // U_SPIFFS
      type = "filesystem";

    otaInProgress = true;
    otaStatus = "Starting " + type + " update...";
    Serial.println("Start updating " + type);
    
    // Stop servo operations during update
    for (int i = 0; i < NUM_SERVOS; i++) {
      pwm.setPWM(i, 0, 0); // Turn off all servos
    }
  });

  ArduinoOTA.onEnd([]() {
    otaInProgress = false;
    otaStatus = "Update Complete - Rebooting...";
    Serial.println("\nEnd");
  });

  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    unsigned int percent = (progress / (total / 100));
    otaStatus = "Progress: " + String(percent) + "%";
    Serial.printf("Progress: %u%%\r", percent);
  });

  ArduinoOTA.onError([](ota_error_t error) {
    otaInProgress = false;
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) {
      otaStatus = "Auth Failed";
      Serial.println("Auth Failed");
    } else if (error == OTA_BEGIN_ERROR) {
      otaStatus = "Begin Failed";
      Serial.println("Begin Failed");
    } else if (error == OTA_CONNECT_ERROR) {
      otaStatus = "Connect Failed";
      Serial.println("Connect Failed");
    } else if (error == OTA_RECEIVE_ERROR) {
      otaStatus = "Receive Failed";
      Serial.println("Receive Failed");
    } else if (error == OTA_END_ERROR) {
      otaStatus = "End Failed";
      Serial.println("End Failed");
    }
    
    // Reinitialize servos after failed update
    initServos();
  });

  ArduinoOTA.begin();
  Serial.println("OTA Ready");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

// HTML Dashboard with OTA functionality
const char* dashboard_html = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32 Servo Controller</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .status {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        
        .controls {
            padding: 30px;
        }
        
        .ota-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            border: 2px solid #e9ecef;
        }
        
        .ota-section h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .ota-upload {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .file-input {
            flex: 1;
            min-width: 200px;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .ota-status {
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            font-weight: bold;
            text-align: center;
        }
        
        .ota-ready { background: #d4edda; color: #155724; }
        .ota-progress { background: #d1ecf1; color: #0c5460; }
        .ota-error { background: #f8d7da; color: #721c24; }
        .ota-success { background: #d4edda; color: #155724; }
        
        .control-panel {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .servo-group {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border: 2px solid #e9ecef;
            transition: transform 0.2s ease;
        }
        
        .servo-group:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .servo-control {
            margin-bottom: 15px;
        }
        
        .servo-label {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            font-weight: 600;
            color: #495057;
        }
        
        .servo-value {
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.85em;
            min-width: 40px;
            text-align: center;
        }
        
        .servo-slider {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: #ddd;
            outline: none;
            -webkit-appearance: none;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        
        .servo-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #667eea;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            transition: all 0.2s ease;
        }
        
        .servo-slider::-webkit-slider-thumb:hover {
            background: #5a6fd8;
            transform: scale(1.1);
        }
        
        .servo-slider::-moz-range-thumb {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #667eea;
            cursor: pointer;
            border: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .quick-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: center;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 2px solid #e9ecef;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .btn-primary {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-warning {
            background: #ffc107;
            color: #212529;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            z-index: 1000;
            transition: all 0.3s ease;
        }
        
        .connected {
            background: #28a745;
        }
        
        .disconnected {
            background: #dc3545;
        }
        
        @media (max-width: 768px) {
            .control-panel {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .quick-actions {
                flex-direction: column;
            }
            
            .ota-upload {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div id="connectionStatus" class="connection-status connected">Connected</div>
    
    <div class="container">
        <div class="header">
            <h1>🎛️ ESP32 Servo Controller</h1>
            <div class="status">18 Channel PCA9685 Controller with OTA</div>
        </div>
        
        <div class="controls">
            <!-- OTA Update Section -->
            <div class="ota-section">
                <h3>🔄 Firmware Update (OTA)</h3>
                <div class="ota-upload">
                    <input type="file" id="firmwareFile" class="file-input" accept=".bin" />
                    <button class="btn btn-warning" onclick="uploadFirmware()" id="uploadBtn">Upload Firmware</button>
                </div>
                <div id="otaStatus" class="ota-status ota-ready">Ready for firmware update</div>
                <small style="color: #6c757d; display: block; margin-top: 10px;">
                    Select a .bin file compiled for ESP32. Device will reboot automatically after successful update.
                </small>
            </div>
            
            <div class="control-panel">
                <div class="servo-group">
                    <h3 style="margin-bottom: 15px; color: #667eea;">Servos 1-6</h3>
                    <div id="servos-0-5"></div>
                </div>
                
                <div class="servo-group">
                    <h3 style="margin-bottom: 15px; color: #667eea;">Servos 7-12</h3>
                    <div id="servos-6-11"></div>
                </div>
                
                <div class="servo-group">
                    <h3 style="margin-bottom: 15px; color: #667eea;">Servos 13-18</h3>
                    <div id="servos-12-17"></div>
                </div>
            </div>
            
            <div class="quick-actions">
                <button class="btn btn-primary" onclick="setAllServos(90)">Center All</button>
                <button class="btn btn-secondary" onclick="setAllServos(0)">Min Position</button>
                <button class="btn btn-secondary" onclick="setAllServos(180)">Max Position</button>
                <button class="btn btn-success" onclick="sweepAll()">Sweep Test</button>
                <button class="btn btn-primary" onclick="getPositions()">Refresh</button>
            </div>

          <button class="btn btn-warning" onclick="standUp()">Stand Up</button>
          <button class="btn btn-warning" onclick="sitDown()">Sit Down</button>

        </div>
    </div>

    <script>
        let servos = {};
        let sweeping = false;
        
        // Initialize servo controls
        function initControls() {
            const groups = [
                { container: 'servos-0-5', start: 0, end: 5 },
                { container: 'servos-6-11', start: 6, end: 11 },
                { container: 'servos-12-17', start: 12, end: 17 }
            ];
            
            groups.forEach(group => {
                const container = document.getElementById(group.container);
                for (let i = group.start; i <= group.end; i++) {
                    const servoDiv = document.createElement('div');
                    servoDiv.className = 'servo-control';
                    servoDiv.innerHTML = `
                        <div class="servo-label">
                            <span>Servo ${i + 1}</span>
                            <span class="servo-value" id="value-${i}">90°</span>
                        </div>
                        <input type="range" class="servo-slider" id="servo-${i}" 
                               min="0" max="180" value="90" 
                               oninput="updateServo(${i}, this.value)">
                    `;
                    container.appendChild(servoDiv);
                    servos[i] = 90;
                }
            });
        }
        
        // OTA Upload function
        function uploadFirmware() {
            const fileInput = document.getElementById('firmwareFile');
            const uploadBtn = document.getElementById('uploadBtn');
            const statusDiv = document.getElementById('otaStatus');
            
            if (!fileInput.files[0]) {
                alert('Please select a firmware file first');
                return;
            }
            
            const file = fileInput.files[0];
            if (!file.name.endsWith('.bin')) {
                alert('Please select a valid .bin firmware file');
                return;
            }
            
            uploadBtn.disabled = true;
            uploadBtn.textContent = 'Uploading...';
            statusDiv.className = 'ota-status ota-progress';
            statusDiv.textContent = 'Uploading firmware...';
            
            const formData = new FormData();
            formData.append('firmware', file);
            
            fetch('/update', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    statusDiv.className = 'ota-status ota-success';
                    statusDiv.textContent = 'Upload successful! Device is rebooting...';
                    setTimeout(() => {
                        location.reload();
                    }, 5000);
                } else {
                    throw new Error('Upload failed');
                }
            })
            .catch(error => {
                console.error('Upload error:', error);
                statusDiv.className = 'ota-status ota-error';
                statusDiv.textContent = 'Upload failed. Please try again.';
                uploadBtn.disabled = false;
                uploadBtn.textContent = 'Upload Firmware';
            });
        }
        
        // Update individual servo
        function updateServo(servoId, angle) {
            document.getElementById(`value-${servoId}`).textContent = angle + '°';
            servos[servoId] = parseInt(angle);
            
            fetch('/setServo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ servo: servoId, angle: parseInt(angle) })
            }).catch(err => {
                console.error('Error setting servo:', err);
                updateConnectionStatus(false);
            });
        }
        
        // Set all servos to same position
        function setAllServos(angle) {
            if (sweeping) return;
            
            for (let i = 0; i < 18; i++) {
                document.getElementById(`servo-${i}`).value = angle;
                document.getElementById(`value-${i}`).textContent = angle + '°';
                servos[i] = angle;
            }
            
            fetch('/setAll', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ angle: angle })
            }).catch(err => {
                console.error('Error setting all servos:', err);
                updateConnectionStatus(false);
            });
        }
        
        // Sweep test
        async function sweepAll() {
            if (sweeping) return;
            sweeping = true;
            
            const btn = event.target;
            btn.textContent = 'Sweeping...';
            btn.disabled = true;
            
            try {
                const response = await fetch('/sweep', { method: 'POST' });
                if (response.ok) {
                    // Update UI during sweep
                    for (let angle = 0; angle <= 180; angle += 10) {
                        await new Promise(resolve => setTimeout(resolve, 100));
                        for (let i = 0; i < 18; i++) {
                            document.getElementById(`servo-${i}`).value = angle;
                            document.getElementById(`value-${i}`).textContent = angle + '°';
                        }
                    }
                    for (let angle = 180; angle >= 0; angle -= 10) {
                        await new Promise(resolve => setTimeout(resolve, 100));
                        for (let i = 0; i < 18; i++) {
                            document.getElementById(`servo-${i}`).value = angle;
                            document.getElementById(`value-${i}`).textContent = angle + '°';
                        }
                    }
                    // Return to center
                    for (let i = 0; i < 18; i++) {
                        document.getElementById(`servo-${i}`).value = 90;
                        document.getElementById(`value-${i}`).textContent = '90°';
                    }
                }
            } catch (err) {
                console.error('Sweep error:', err);
                updateConnectionStatus(false);
            }
            
            btn.textContent = 'Sweep Test';
            btn.disabled = false;
            sweeping = false;
        }
        
        // Get current positions
        function getPositions() {
            fetch('/getPositions')
                .then(response => response.json())
                .then(data => {
                    for (let i = 0; i < 18; i++) {
                        const angle = data.positions[i];
                        document.getElementById(`servo-${i}`).value = angle;
                        document.getElementById(`value-${i}`).textContent = angle + '°';
                        servos[i] = angle;
                    }
                    updateConnectionStatus(true);
                })
                .catch(err => {
                    console.error('Error getting positions:', err);
                    updateConnectionStatus(false);
                });
        }
        
        // Update connection status
        function updateConnectionStatus(connected) {
            const status = document.getElementById('connectionStatus');
            if (connected) {
                status.textContent = 'Connected';
                status.className = 'connection-status connected';
            } else {
                status.textContent = 'Disconnected';
                status.className = 'connection-status disconnected';
            }
        }

        function standUp() {
        fetch('/stand')  // GET request
        .then(response => response.json())
        .then(data => {
            const positions = data.positions;
            for (let i = 0; i < positions.length; i++) {
                document.getElementById(`servo-${i}`).value = positions[i];
                document.getElementById(`value-${i}`).textContent = positions[i] + '°';
                servos[i] = positions[i];
            }
            updateConnectionStatus(true);
        })
        .catch(err => {
            console.error('Stand error:', err);
            updateConnectionStatus(false);
        });
        }

        function sitDown() {
            fetch('/sit')  // GET request
                .then(response => response.json())
                .then(data => {
                    const positions = data.positions;
                    for (let i = 0; i < positions.length; i++) {
                        document.getElementById(`servo-${i}`).value = positions[i];
                        document.getElementById(`value-${i}`).textContent = positions[i] + '°';
                        servos[i] = positions[i];
                    }
                    updateConnectionStatus(true);
                })
                .catch(err => {
                    console.error('Sit Down error:', err);
                    updateConnectionStatus(false);
                });
        }

        // Check connection periodically
        setInterval(() => {
            fetch('/ping')
                .then(() => updateConnectionStatus(true))
                .catch(() => updateConnectionStatus(false));
        }, 5000);
        
        // Initialize on load
        window.onload = function() {
            initControls();
            getPositions();
        };
    </script>
</body>
</html>
)rawliteral";





// Handle root request
void handleRoot() {
  server.send(200, "text/html", dashboard_html);
}

void standUp() 
{
  // Assuming servo indexing:
  // Coxa servos = 0,3,6,9,12,15
  // Femur servos = 1,4,7,10,13,16
  // Tibia servos = 2,5,8,11,14,17

  int coxaIDs[] = {0,3,6,9,12,15};
  int femurIDs[] = {1,4,7,10,13,16};
  int tibiaIDs[] = {2,5,8,11,14,17};

  for (int i : coxaIDs) {
    servoPositions[i] = 90;  
    pwm.setPWM(i, 0, angleToPWM(90));
  }
  for (int i : femurIDs) {
    servoPositions[i] = 32;  
    pwm.setPWM(i, 0, angleToPWM(32));
  }
  for (int i : tibiaIDs) {
    servoPositions[i] = 50;  
    pwm.setPWM(i, 0, angleToPWM(50));
  }

  Serial.println("Robot moved to Stand Up position");
}

void sitDown() 
{
  // Assuming servo indexing:
  // Coxa servos = 0,3,6,9,12,15
  // Femur servos = 1,4,7,10,13,16
  // Tibia servos = 2,5,8,11,14,17

  int coxaIDs[] = {0,3,6,9,12,15};
  int femurIDs[] = {1,4,7,10,13,16};
  int tibiaIDs[] = {2,5,8,11,14,17};

  for (int i : coxaIDs) {
    servoPositions[i] = 90;  
    pwm.setPWM(i, 0, angleToPWM(90));
  }
  for (int i : femurIDs) {
    servoPositions[i] = 100;  
    pwm.setPWM(i, 0, angleToPWM(100));
  }
  for (int i : tibiaIDs) {
    servoPositions[i] = 20;  
    pwm.setPWM(i, 0, angleToPWM(20));
  }

  Serial.println("Robot moved to sit Down position");
}


void handleStand() {
  standUp();  
  // return JSON with updated positions so UI can sync
  String json = "{\"status\":\"success\",\"action\":\"stand\",\"positions\":[";
  for (int i = 0; i < NUM_SERVOS; i++) {
    json += String(servoPositions[i]);
    if (i < NUM_SERVOS - 1) json += ",";
  }
  json += "]}";
  server.send(200, "application/json", json);
}

void handleSit() {
  sitDown();
  // return JSON with updated positions so UI can sync
  String json = "{\"status\":\"success\",\"action\":\"sit\",\"positions\":[";
  for (int i = 0; i < NUM_SERVOS; i++) {
    json += String(servoPositions[i]);
    if (i < NUM_SERVOS - 1) json += ",";
  }
  json += "]}";
  server.send(200, "application/json", json);
}

// Handle OTA update upload
void handleUpdate() {
  HTTPUpload& upload = server.upload();
  
  if (upload.status == UPLOAD_FILE_START) {
    Serial.printf("Update: %s\n", upload.filename.c_str());
    otaInProgress = true;
    otaStatus = "Starting update...";
    
    // Stop all servo operations
    for (int i = 0; i < NUM_SERVOS; i++) {
      pwm.setPWM(i, 0, 0);
    }
    
    if (!Update.begin(UPDATE_SIZE_UNKNOWN)) {
      Update.printError(Serial);
      otaStatus = "Update begin failed";
      otaInProgress = false;
    }
  } else if (upload.status == UPLOAD_FILE_WRITE) {
    if (Update.write(upload.buf, upload.currentSize) != upload.currentSize) {
      Update.printError(Serial);
      otaStatus = "Update write failed";
      otaInProgress = false;
    } else {
      otaStatus = "Uploading: " + String((Update.progress() * 100) / Update.size()) + "%";
    }
  } else if (upload.status == UPLOAD_FILE_END) {
    if (Update.end(true)) {
      Serial.printf("Update Success: %uB\n", upload.totalSize);
      otaStatus = "Update complete - Rebooting...";
      server.send(200, "text/plain", "OK");
      delay(1000);
      ESP.restart();
    } else {
      Update.printError(Serial);
      otaStatus = "Update end failed";
      otaInProgress = false;
      // Reinitialize servos after failed update
      initServos();
    }
  }
}

// Handle individual servo control
void handleSetServo() {
  if (otaInProgress) {
    server.send(503, "application/json", "{\"status\":\"error\",\"message\":\"OTA update in progress\"}");
    return;
  }
  
  if (server.hasArg("plain")) {
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, server.arg("plain"));
    
    int servoId = doc["servo"];
    int angle = doc["angle"];
    
    if (servoId >= 0 && servoId < NUM_SERVOS && angle >= 0 && angle <= 180) {
      servoPositions[servoId] = angle;
      pwm.setPWM(servoId, 0, angleToPWM(angle));
      
      server.send(200, "application/json", "{\"status\":\"success\"}");
      Serial.printf("Servo %d set to %d degrees\n", servoId + 1, angle);
    } else {
      server.send(400, "application/json", "{\"status\":\"error\",\"message\":\"Invalid parameters\"}");
    }
  } else {
    server.send(400, "application/json", "{\"status\":\"error\",\"message\":\"No data received\"}");
  }
}

// Handle set all servos
void handleSetAll() {
  if (otaInProgress) {
    server.send(503, "application/json", "{\"status\":\"error\",\"message\":\"OTA update in progress\"}");
    return;
  }
  
  if (server.hasArg("plain")) {
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, server.arg("plain"));
    
    int angle = doc["angle"];
    
    if (angle >= 0 && angle <= 180) {
      for (int i = 0; i < NUM_SERVOS; i++) {
        servoPositions[i] = angle;
        pwm.setPWM(i, 0, angleToPWM(angle));
      }
      
      server.send(200, "application/json", "{\"status\":\"success\"}");
      Serial.printf("All servos set to %d degrees\n", angle);
    } else {
      server.send(400, "application/json", "{\"status\":\"error\",\"message\":\"Invalid angle\"}");
    }
  } else {
    server.send(400, "application/json", "{\"status\":\"error\",\"message\":\"No data received\"}");
  }
}

// Handle sweep test
void handleSweep() {
  if (otaInProgress) {
    server.send(503, "application/json", "{\"status\":\"error\",\"message\":\"OTA update in progress\"}");
    return;
  }
  
  Serial.println("Starting sweep test...");
  
  // Sweep from 0 to 180
  for (int angle = 0; angle <= 180; angle += 10) {
    for (int i = 0; i < NUM_SERVOS; i++) {
      servoPositions[i] = angle;
      pwm.setPWM(i, 0, angleToPWM(angle));
    }
    delay(100);
  }
  
  // Sweep back from 180 to 0
  for (int angle = 180; angle >= 0; angle -= 10) {
    for (int i = 0; i < NUM_SERVOS; i++) {
      servoPositions[i] = angle;
      pwm.setPWM(i, 0, angleToPWM(angle));
    }
    delay(100);
  }
  
  // Return to center
  for (int i = 0; i < NUM_SERVOS; i++) {
    servoPositions[i] = 90;
    pwm.setPWM(i, 0, angleToPWM(90));
  }
  
  server.send(200, "application/json", "{\"status\":\"success\"}");
  Serial.println("Sweep test completed");
}

// Handle get positions
void handleGetPositions() {
  String json = "{\"positions\":[";
  for (int i = 0; i < NUM_SERVOS; i++) {
    json += String(servoPositions[i]);
    if (i < NUM_SERVOS - 1) json += ",";
  }
  json += "],\"otaStatus\":\"" + otaStatus + "\"}";
  
  server.send(200, "application/json", json);
}

// Handle ping for connection check
void handlePing() {
  server.send(200, "application/json", "{\"status\":\"ok\",\"ota\":\"" + otaStatus + "\"}");
}

void setup() {
  Serial.begin(115200);
  Serial.println("ESP32 Servo Controller with OTA Starting...");
  
  // Initialize I2C communication
  Wire.begin(SDA_PIN, SCL_PIN);
  
  // Initialize PCA9685
  pwm.begin();
  pwm.setOscillatorFrequency(27000000);
  pwm.setPWMFreq(SERVO_FREQ);
  
  delay(100);
  
  // Initialize all servos to center position
  initServos();
  Serial.println("Servos initialized to center position");

    // Static IP setup
  IPAddress local_IP(192, 168, 0, 160);
  IPAddress gateway(192, 168, 0, 1);
  IPAddress subnet(255, 255, 255, 0);
  IPAddress primaryDNS(8, 8, 8, 8);
  IPAddress secondaryDNS(8, 8, 4, 4);

  if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
    Serial.println("⚠️ STA Failed to configure");
  }

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.println("WiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  
  // Setup OTA
  setupOTA();
  
  // Setup web server routes
  server.on("/", handleRoot);
  server.on("/setServo", HTTP_POST, handleSetServo);
  server.on("/setAll", HTTP_POST, handleSetAll);
  server.on("/sweep", HTTP_POST, handleSweep);
  server.on("/getPositions", HTTP_GET, handleGetPositions);
  server.on("/ping", HTTP_GET, handlePing);
  server.on("/update", HTTP_POST, []() {
    server.send(200, "text/plain", (Update.hasError()) ? "FAIL" : "OK");
  }, handleUpdate);
  
  server.on("/stand", HTTP_GET, handleStand);
  server.on("/sit", HTTP_GET, handleSit);

  // Start server
  server.begin();
  Serial.println("Web server started!");
  Serial.println("Open your browser and go to: http://" + WiFi.localIP().toString());
  Serial.println("OTA Hostname: ESP32-ServoController");
  Serial.println("OTA Password: servo123");
}

void loop() {
  // Handle OTA updates
  ArduinoOTA.handle();
  
  // Handle web server requests
  server.handleClient();
  
  // Small delay to prevent watchdog issues
  delay(1);
}
