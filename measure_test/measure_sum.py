"""Continuous Reading of Sensors

Make continuous readings from the sensors and begin
a take measurements function.

We Believe the Following:
Magnet x: 
Magnet y:
Magnet z:
Euler Heading: Dir w/ 0 being North 90 East, 180 South, 270 West
Euler Roll:
Euler Pitch: Angle up 
Accel x:
Accel y:
Accel z:
Euler x:
Euler y:
Euler z:
Thermometer: Temperature in Celcius
Left Encoder: Odometer of left wheel
Right Encoder: Odometer of right wheel
"""
from __future__ import print_function
from __future__ import division
import time
import pickle
from datetime import datetime, timedelta

from easygopigo3 import EasyGoPiGo3
from di_sensors.inertial_measurement_unit import InertialMeasurementUnit
from di_sensors.distance_sensor import DistanceSensor

import numpy as np
import math as math
# establish communication with the DistanceSensor
ds = DistanceSensor()

# set the sensor in fast-polling-mode
ds.start_continuous()
# Setup Sensors
imu = InertialMeasurementUnit(bus = "GPG3_AD1")
gpg = EasyGoPiGo3()
gpg.reset_encoders()


def print_reading():
    mag   = imu.read_magnetometer()
    gyro  = imu.read_gyroscope()
    euler = imu.read_euler()
    accel = imu.read_accelerometer()
    temp  = imu.read_temperature()
    encoder = gpg.read_encoders()
        
    string_to_print = "Magnetometer X: {:.1f}  Y: {:.1f}  Z: {:.1f} " \
                      "Gyroscope X: {:.1f}  Y: {:.1f}  Z: {:.1f} " \
                      "Accelerometer X: {:.1f}  Y: {:.1f} Z: {:.1f} " \
                      "Euler Heading: {:.1f}  Roll: {:.1f}  Pitch: {:.1f} " \
                      "Temperature: {:.1f}C " \
                      "Left Encoder: {:.1f} " \
                      "Right Encoder: {:.1f}".format(mag[0], mag[1], mag[2],
                                                  gyro[0], gyro[1], gyro[2],
                                                  accel[0], accel[1], accel[2],
                                                  euler[0], euler[1], euler[2],
                                                  temp, encoder[0], encoder[1])
    print(string_to_print)


def get_reading():
    mag   = imu.read_magnetometer()
    gyro  = imu.read_gyroscope()
    euler = imu.read_euler()
    accel = imu.read_accelerometer()
    temp  = imu.read_temperature()
    encoder = gpg.read_encoders()
    res = {
        "mag_x": mag[0],
        "mag_y": mag[1],
        "mag_z": mag[2],
        "gyro_x": gyro[0],
        "gyro_y": gyro[1],
        "gyro_z": gyro[2],
        "accel_x": accel[0], 
        "accel_y": accel[1],
        "accel_z": accel[2], 
        "euler_x": euler[0],
        "euler_y": euler[1],
        "euler_z": euler[2],
        # "temp": temp, 
        "left_enc": encoder[0],
        "right_enc": encoder[1],
    }
    
    return res

def get_position(right_prev,left_prev):

    euler = imu.read_euler()
    euler_x=euler[0]

    encoder = gpg.read_encoders()
    left_enc=encoder[0]
    right_enc= encoder[1]
    y_delta=left_enc-left_prev
    x_delta=right_enc-right_prev
    y=math.sin(euler_x*0.0174533)*y_delta
    x=math.cos(euler_x*0.0174533)*x_delta
    read_distance = ds.read_range_continuous()
    res = {

        "left_enc": left_enc,
        "right_enc": right_enc,
        "x": x,
        "y": y,
        "euler_x":euler_x,
        "read_distance":read_distance
        
    }
    ##print(res)
    return left_enc,right_enc,x,y,res



i=0
t1 = datetime.now()
data = []
right_prev=0
left_prev=0
x_total=0
y_total=0
while  i<100:
    # Execute
    ##print_reading()
    #data.append(get_reading())
    t2 = datetime.now()
    left_enc,right_enc,x,y,res=get_position(right_prev,left_prev)
    
    right_prev=right_enc
    left_prev=left_enc
    x_total=x_total+x
    y_total=y_total+y
    print("x= %8.2f y=%8.2f" % (x_total/44, y_total/44))
    print(imu.read_euler()[0])
    ##print("Duration: {}".format(t2 - t1))
    # print(timedelta(t2, t1))
    data.append(res)
    
    # Prepare for next iteration
    i += 1
    t1 = t2
    time.sleep(.1)
    

gpg.stop()

##print(imu.read_euler()[0]) 
distance_back=math.sqrt(x_total*x_total+y_total*y_total)
##print(distance_back)

#if x_total>0 and y_total>0: ### quadrant 1
#    direction_back=180+90-math.atan(x_total/y_total)*57.2958
#elif x_total<0 and y_total>0:### quadrant 4
#    direction_back=180+90-math.atan(x_total/y_total)*57.2958
#elif x_total<0 and y_total<0:### quadrant 3
#    direction_back=90-math.atan(x_total/y_total)*57.2958
#else: ### quadrant 2
#    direction_back=90-math.atan(x_total/y_total)*57.2958
##print(direction_back)
#print("Back direction= %8.2f dist=%8.2f" % (direction_back, distance_back/44))


## Try quarant 3 and 4
if x_total>0 and y_total>0: ### quadrant 1
    direction_back=180+90-math.atan(x_total/y_total)*57.2958
elif x_total<0 and y_total>0:### quadrant 4
    direction_back=180+90+math.atan(x_total/y_total)*57.2958
elif x_total<0 and y_total<0:### quadrant 3
    direction_back=90-math.atan(x_total/y_total)*57.2958
else: ### quadrant 2
    direction_back=90+math.atan(x_total/y_total)*57.2958
##print(direction_back)
print("Back direction= %8.2f dist=%8.2f" % (direction_back, distance_back/44))






angle=imu.read_euler()[0]
angle_delta=direction_back-angle
print("current= %8.2f delta=%8.2f" % (angle, angle_delta))
##while angle_delta>1:
  ##  angle=imu.read_euler()[0]
    ##angle_delta=direction_back-angle
  ##  gpg.right()
  ##  time.sleep(.1)
 ##   gpg.stop()
 ##   print("current= %8.2f delta=%8.2f" % (angle, angle_delta))
 
gpg.turn_degrees(angle_delta)
print("back inc= %8.2f back cm=%8.2f" % (distance_back/44, distance_back/44*2.54))
gpg.drive_cm(distance_back/44*2.54)  
gpg.stop()  
# Save Out
#with open('data.pkl', 'wb') as f:
    #pickle.dump(data, f)
# Save Out
with open('data.pkl', 'wb') as f:
    pickle.dump(data, f)
