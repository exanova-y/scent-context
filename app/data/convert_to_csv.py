import os
import re
import csv
import datetime

def parse_sensor_data(file_path):
    """Parse sensor data from text file into structured format."""
    try:
        # Read file with proper encoding
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        readings = []
        i = 0
        
        # Process in groups of 3 lines
        while i < len(lines) - 2:
            # Extract values using regex with more flexible pattern matching
            gas_line = lines[i].strip()
            temp_line = lines[i+1].strip()
            humidity_line = lines[i+2].strip()
            
            # Use more robust regex patterns
            gas_match = re.search(r'Gas Resistance:\s*([\d\.]+)', gas_line)
            temp_match = re.search(r'Temperature:\s*([\d\.]+)', temp_line)
            humidity_match = re.search(r'Humidity:\s*([\d\.]+)', humidity_line)
            
            if gas_match and temp_match and humidity_match:
                try:
                    gas = float(gas_match.group(1))
                    temp = float(temp_match.group(1))
                    humidity = float(humidity_match.group(1))
                    
                    readings.append({
                        'gas_resistance': gas,
                        'temperature': temp,
                        'humidity': humidity
                    })
                except ValueError as ve:
                    print(f"Error converting values: {ve}")
            else:
                print(f"Failed to match pattern at line {i}")
            
            i += 3  # Move to next group
        
        print(f"Found {len(readings)} readings in {file_path}")
        return readings
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return []

def save_to_csv(readings, output_file, scent_name):
    """Save readings to CSV file with timestamp and scent name."""
    # Create CSV file with headers
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['timestamp', 'scent', 'gas_resistance', 'temperature', 'humidity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Add timestamp for each reading
        timestamp = datetime.datetime.now()
        time_increment = datetime.timedelta(seconds=5)  # Assume 5 seconds between readings
        
        for reading in readings:
            row = {
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'scent': scent_name,
                'gas_resistance': reading['gas_resistance'],
                'temperature': reading['temperature'],
                'humidity': reading['humidity']
            }
            writer.writerow(row)
            timestamp += time_increment

def main():
    # Define input and output files
    # Use the script's directory as the base path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = script_dir  # The text files are in the same directory as the script
    input_files = {
        'lavender': os.path.join(data_dir, 'lavender.txt'),
        'lemongrass': os.path.join(data_dir, 'lemongrass.txt'),
        'orange': os.path.join(data_dir, 'orange.txt'),
        'street-air': os.path.join(data_dir, 'street-air.txt')
    }
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(data_dir, 'csv_output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each file and save to individual CSVs
    all_readings = []
    
    for scent, file_path in input_files.items():
        print(f"\nProcessing {scent} data from {file_path}...")
        readings = parse_sensor_data(file_path)
        
        if readings:
            # Save to individual CSV
            output_file = os.path.join(output_dir, f'{scent}.csv')
            save_to_csv(readings, output_file, scent)
            print(f"Saved {len(readings)} readings to {output_file}")
            
            # Add to combined data with scent label
            for reading in readings:
                reading['scent'] = scent
            all_readings.extend(readings)
        else:
            print(f"No valid readings found in {file_path}")
    
    # Save combined data
    if all_readings:
        combined_output = os.path.join(output_dir, 'combined_scents.csv')
        with open(combined_output, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'scent', 'gas_resistance', 'temperature', 'humidity']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Add timestamp for each reading
            timestamp = datetime.datetime.now()
            time_increment = datetime.timedelta(seconds=5)  # Assume 5 seconds between readings
            
            for reading in all_readings:
                row = {
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'scent': reading['scent'],
                    'gas_resistance': reading['gas_resistance'],
                    'temperature': reading['temperature'],
                    'humidity': reading['humidity']
                }
                writer.writerow(row)
                timestamp += time_increment
        
        print(f"\nSaved combined data with {len(all_readings)} readings to {combined_output}")
    else:
        print("\nNo readings found in any files. Combined CSV not created.")

if __name__ == "__main__":
    main()
