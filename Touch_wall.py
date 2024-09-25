# You can directly use this code when your lidar is on (0,0)(at upper left corner) coordinate of screen
# All the distances are in MM

import serial
import struct
import mouse as ms

import math
from screeninfo import get_monitors



def extract_frames(data, header, bytes_to_read):
    frames = []
    current_frame = []
    header_encountered = False
    bytes_read_after_header = 0
    
    for byte in data:
        if byte == header:
            if header_encountered:
                if current_frame:
                    frames.append(current_frame)
                current_frame = []
                bytes_read_after_header = 0
            header_encountered = True
        if header_encountered:
            if bytes_read_after_header < bytes_to_read:
                current_frame.append(byte)
                bytes_read_after_header += 1
            else:
                header_encountered = False

    # Add the last frame if it exists
    if current_frame:
        frames.append(current_frame)
         
    return frames


def parse_lidar_data(data_packet):
    # Parse the Start Angle (2 bytes, little-endian)
    
    start_angle = struct.unpack('<H', data_packet[4:6])[0]
    start_angle_degrees = start_angle / 100.0
    
    # Parse the End Angle (2 bytes, little-endian)
    end_angle = struct.unpack('<H', data_packet[-5:-3])[0]
    end_angle_degrees = end_angle / 100.0
    
    
    # Parse the distances and intensities
    distances = []
    object_data = data_packet[6:-5]  # Exclude the header, verLen, speed, angles, timestamp, and CRC check

    # Each measurement point consists of 2 bytes for distance and 1 byte for intensity
    for i in range(0, len(object_data), 3):
        if i + 2 < len(object_data):
            distance = struct.unpack('<H', object_data[i:i+2])[0]
            distances.append(distance)
    
    # Calculate angles for each point
    angle_increment = (end_angle_degrees - start_angle_degrees) / (len(distances) - 1)
    angles = [start_angle_degrees + i * angle_increment for i in range(len(distances))]

    # Return distances in meters and angles
    distances_meters = [d for d in distances]
    return distances_meters, angles

               
                
# Initialize the serial connection


def main():
    
    # Configure baudrate as per your requirement
    ser = serial.Serial("COM10", 921600, timeout=None)

    header = 0x54  # Header byte to identify the start of a frame
    bytes_to_read_after_header = 47

    try:
        while True:
            flag = True
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                
                frames = extract_frames(data, header, bytes_to_read_after_header)

                for frame in frames:
                    if len(frame) == 47:
                        # Convert frame to hexadecimal string
                        hex_frame = ' '.join(f"{byte:02X}" for byte in frame)
                        
                        distances, angles = parse_lidar_data(bytes.fromhex(hex_frame))
                        for distance, angle in zip(distances, angles):
                         

                         distance = int(distance)

                        # To find objects at particulare angle
                         if 1 < angle < 89 and flag:

                        # To find objects at perticular distance  
                          if 0 < distance < 1000 : 
                            print(f"Distance:{distance}, Angle:{angle}")
                           
                        
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
