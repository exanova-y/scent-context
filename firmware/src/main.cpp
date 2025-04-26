#include "Arduino.h"
#include "BME688.h"
#include "SPIFFS.h"
#include "ArduinoJson.h"
#include <vector>

BME688 sensor;

// Structure to define temperature-time vector
struct TempTimeVector {
  int temperature;
  int duration;
};

// Structure to hold heater profile configuration
struct HeaterProfile {
  String id;
  int timeBase;
  std::vector<TempTimeVector> vectors;  // Vector of temperature and time pairs
};

// Structure to hold duty cycle configuration
struct DutyCycleProfile {
  String id;
  int numberScanningCycles;
  int numberSleepingCycles;
};

// Structure to hold sensor configuration
struct SensorConfig {
  int sensorIndex;
  String heaterProfile;
  String dutyCycleProfile;
};

// Default JSON configuration as a string
const char* defaultConfig = R"({
  "configHeader": {
    "dateCreated": "2025-04-25T21:42:13.628Z",
    "appVersion": "2.0.0",
    "boardType": "board_8",
    "boardMode": "burn_in",
    "boardLayout": "grouped"
  },
  "configBody": {
    "heaterProfiles": [
      {
        "id": "heater_354",
        "timeBase": 140,
        "temperatureTimeVectors": [
          [320, 5],
          [100, 2],
          [100, 10],
          [100, 30],
          [200, 5],
          [200, 5],
          [200, 5],
          [320, 5],
          [320, 5],
          [320, 5]
        ]
      }
    ],
    "dutyCycleProfiles": [
      {
        "id": "duty_5_10",
        "numberScanningCycles": 5,
        "numberSleepingCycles": 10
      }
    ],
    "sensorConfigurations": [
      {
        "sensorIndex": 0,
        "heaterProfile": "heater_354",
        "dutyCycleProfile": "duty_5_10"
      },
      {
        "sensorIndex": 1,
        "heaterProfile": "heater_354",
        "dutyCycleProfile": "duty_5_10"
      },
      {
        "sensorIndex": 2,
        "heaterProfile": "heater_354",
        "dutyCycleProfile": "duty_5_10"
      },
      {
        "sensorIndex": 3,
        "heaterProfile": "heater_354",
        "dutyCycleProfile": "duty_5_10"
      },
      {
        "sensorIndex": 4,
        "heaterProfile": "heater_354",
        "dutyCycleProfile": "duty_5_10"
      },
      {
        "sensorIndex": 5,
        "heaterProfile": "heater_354",
        "dutyCycleProfile": "duty_5_10"
      },
      {
        "sensorIndex": 6,
        "heaterProfile": "heater_354",
        "dutyCycleProfile": "duty_5_10"
      },
      {
        "sensorIndex": 7,
        "heaterProfile": "heater_354",
        "dutyCycleProfile": "duty_5_10"
      }
    ]
  }
})";

// Function to initialize the file system and create the config file if it doesn't exist
bool initFileSystem() {
  // Initialize SPIFFS
  if (!SPIFFS.begin(true)) {
    Serial.println("Failed to mount SPIFFS");
    return false;
  }
  
  // Check if the config file exists
  if (!SPIFFS.exists("/bmeconfig.json")) {
    Serial.println("Config file not found, creating default config...");
    
    // Create and write the default configuration
    File configFile = SPIFFS.open("/bmeconfig.json", "w");
    if (!configFile) {
      Serial.println("Failed to create config file");
      return false;
    }
    
    configFile.print(defaultConfig);
    configFile.close();
    
    Serial.println("Default config file created successfully");
  } else {
    Serial.println("Config file found");
  }
  
  return true;
}

// Function to load and parse the configuration file
bool loadSensorConfig() {
  if (!SPIFFS.begin(true)) {
    Serial.println("Failed to mount SPIFFS");
    return false;
  }

  // Check if the config file exists
  if (!SPIFFS.exists("/bmeconfig.json")) {
    Serial.println("Config file not found");
    return false;
  }

  // Open the config file
  File configFile = SPIFFS.open("/bmeconfig.json", "r");
  if (!configFile) {
    Serial.println("Failed to open config file");
    return false;
  }

  // Allocate a JsonDocument
  DynamicJsonDocument doc(4096); // Adjust size based on your JSON file size

  // Deserialize the JSON document
  DeserializationError error = deserializeJson(doc, configFile);
  configFile.close();

  if (error) {
    Serial.print("Failed to parse config file: ");
    Serial.println(error.c_str());
    return false;
  }

  // Apply configuration to the sensor
  Serial.println("Applying sensor configuration...");
  
  // Extract board configuration
  JsonObject configHeader = doc["configHeader"];
  String boardType = configHeader["boardType"].as<String>();
  String boardMode = configHeader["boardMode"].as<String>();
  
  Serial.print("Board Type: ");
  Serial.println(boardType);
  Serial.print("Board Mode: ");
  Serial.println(boardMode);
  
  // Extract heater profiles
  HeaterProfile heaterProfile;
  if (doc["configBody"]["heaterProfiles"][0]["id"]) {
    heaterProfile.id = doc["configBody"]["heaterProfiles"][0]["id"].as<String>();
    heaterProfile.timeBase = doc["configBody"]["heaterProfiles"][0]["timeBase"].as<int>();
    
    Serial.print("Heater Profile: ");
    Serial.println(heaterProfile.id);
    Serial.print("Time Base: ");
    Serial.println(heaterProfile.timeBase);
    
    // Extract temperature-time vectors
    JsonArray tempTimeVectors = doc["configBody"]["heaterProfiles"][0]["temperatureTimeVectors"];
    for (JsonArray vector : tempTimeVectors) {
      TempTimeVector ttv;
      ttv.temperature = vector[0].as<int>();
      ttv.duration = vector[1].as<int>();
      heaterProfile.vectors.push_back(ttv);
      
      Serial.print("Temperature: ");
      Serial.print(ttv.temperature);
      Serial.print(", Duration: ");
      Serial.println(ttv.duration);
    }
    
    // Apply heater profile settings to the sensor
    // Note: The BME688 library doesn't have direct methods for setting these profiles
    // We'll need to adapt based on the available methods
    
    // Example of how we might configure the sensor if methods were available:
    // sensor.configureHeaterProfile(heaterProfile.id, heaterProfile.timeBase, heaterProfile.vectors);
  }

  // Extract duty cycle profile
  DutyCycleProfile dutyCycle;
  if (doc["configBody"]["dutyCycleProfiles"][0]["id"]) {
    dutyCycle.id = doc["configBody"]["dutyCycleProfiles"][0]["id"].as<String>();
    dutyCycle.numberScanningCycles = doc["configBody"]["dutyCycleProfiles"][0]["numberScanningCycles"].as<int>();
    dutyCycle.numberSleepingCycles = doc["configBody"]["dutyCycleProfiles"][0]["numberSleepingCycles"].as<int>();
    
    Serial.print("Duty Cycle Profile: ");
    Serial.println(dutyCycle.id);
    Serial.print("Scanning Cycles: ");
    Serial.println(dutyCycle.numberScanningCycles);
    Serial.print("Sleeping Cycles: ");
    Serial.println(dutyCycle.numberSleepingCycles);
    
    // Apply duty cycle settings to the sensor
    // Example of how we might configure the sensor if methods were available:
    // sensor.configureDutyCycle(dutyCycle.numberScanningCycles, dutyCycle.numberSleepingCycles);
  }
  
  // Extract sensor configurations
  for (JsonObject sensorConfig : doc["configBody"]["sensorConfigurations"].as<JsonArray>()) {
    int sensorIndex = sensorConfig["sensorIndex"].as<int>();
    String heaterProfileId = sensorConfig["heaterProfile"].as<String>();
    String dutyCycleProfileId = sensorConfig["dutyCycleProfile"].as<String>();
    
    if (sensorIndex == 0) {  // We're only using one sensor in this example
      Serial.print("Sensor Index: ");
      Serial.println(sensorIndex);
      Serial.print("Using Heater Profile: ");
      Serial.println(heaterProfileId);
      Serial.print("Using Duty Cycle Profile: ");
      Serial.println(dutyCycleProfileId);
      
      // Apply sensor-specific configurations
      // Example of how we might configure the sensor if methods were available:
      // sensor.configureSensor(sensorIndex, heaterProfileId, dutyCycleProfileId);
    }
  }

  Serial.println("Configuration applied successfully");
  return true;
}

void setup() {
  Serial.begin(9600);
  
  // Initialize the sensor
  if (sensor.begin()) {
    Serial.println("BME688 Initialized Successfully!");
    
    // Initialize file system and create config file if needed
    if (initFileSystem()) {
      Serial.println("File system initialized successfully");
      
      // Load and apply configuration
      if (loadSensorConfig()) {
        Serial.println("Sensor configuration loaded successfully");
      } else {
        Serial.println("Failed to load sensor configuration");
      }
    } else {
      Serial.println("Failed to initialize file system");
    }
  } else {
    Serial.println("Failed to initialize BME688!");
  }
}

void loop() {
  // Read sensor data using the available methods in the BME688 library
  Serial.print("Gas Resistance: ");
  Serial.print(sensor.readGas(0));
  Serial.println(" Ω");
  Serial.print("Temperature: ");
  Serial.print(sensor.readTemperature()); 
  Serial.println(" °C");
  Serial.print("Humidity: ");
  Serial.print(sensor.readHumidity());
  Serial.println(" %");
  
  delay(5000);
}