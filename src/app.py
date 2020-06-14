import pygame
import pygame.freetype
import random
import requests
import json
import numpy as np
from PIL import Image
import base64

#Initialise pygame module and its clock
pygame.init()
clock = pygame.time.Clock()

#Set the width and height of the application (square to simulate a wristwatch)
display_width = 720
display_height = 720
game_display = pygame.display.set_mode((display_width, display_height))

#Create a font object for use
pygame.display.set_caption("CFC Test")
GAME_FONT = pygame.freetype.SysFont("Arial", 40)

#Set up some colours
black = (0,0,0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)

#Sensor class to emulate sensor data from wearable
class Sensor:
    #Init with a label and value relevant to that sensor (eg. ~60 (BPM) to emulate heart rate tracker)
    def __init__(self, label, init_value):
        self.label = label
        self.value = init_value
        self.rect = None

    #Getter method for testing purposes; in real life scenario, sensor would provide asynchronous data to the program
    def read(self, override=None):
        returnval = self.value
        #Update self.value attribute
        #If value is specified when reading sensor, update sensor value attribute with that value
        if override is not None:
            self.value = override
        else:
            #Else get random value from 0-2
            read_split = random.randint(0, 2)
            #If 0, then increment self.value by 1
            if read_split == 0:
                self.value += 1
            #Else if 1, decrement self.value by 1
            elif read_split == 1:
                self.value -= 1
            #Else if 2, don't change
            
        return returnval

    #This wouldn't need to be here if I was a competent programmer, yet here we are
    #Accelerometer stores 225 frames of data, and sends those 225 frames to the Node-RED flow through the GET request
    def accel_read(self):
            returnval = self.value[-1]
            #Update self.value attribute
            read_split = random.randint(0, 2)
            #If 0, then increment self.value by 1
            if read_split == 0:
                self.value.append(self.value[-1] + 1)
            #Else if 1, decrement self.value by 1
            elif read_split == 1:
                self.value.append(self.value[-1] - 1)
            #Else if 2, don't change
            else:
                self.value.append(self.value[-1])
            
            #If length of the data point list > 225, remove oldest entries
            while len(self.value) > 225:
                self.value.pop(0)

            #Return latest value
            return returnval


    def accel_draw(self, screen):
        #Bounding boxes for label and sensor value are calculated, then drawn to the provided screen
        label_box = (self.rect[0], self.rect[1], self.rect[2], self.rect[3]/3)
        counter_box = (self.rect[0], self.rect[1] + self.rect[3]/3, self.rect[2], 2 * self.rect[3]/3)

        #Drawing sensor label
        text_surface, rect = GAME_FONT.render(self.label, white)
        screen.blit(text_surface, (label_box[0] + (label_box[2]/2 - rect.width/2), label_box[1] + (label_box[3]/2 - rect.height/2)))

        #Drawing sensor value
        text_surface, rect = GAME_FONT.render(str(self.value[-1]), white)
        screen.blit(text_surface, (counter_box[0] + (counter_box[2]/2 - rect.width/2), counter_box[1] + (counter_box[3]/2 - rect.height/2)))
    

    #Check whether cursor is in bounds of the sensor box on screen, and return a Boolean
    def check_cursor(self):
        x, y = pygame.mouse.get_pos()
        if (x > self.rect[0]) and (x < self.rect[0] + self.rect[2]) and (y > self.rect[1]) and (y < self.rect[1] + self.rect[3]):
            return True
        else:
            return False

    #Draw sensor text to provided screen
    def draw(self, screen):
        #Bounding boxes for label and sensor value are calculated, then drawn to the provided screen
        label_box = (self.rect[0], self.rect[1], self.rect[2], self.rect[3]/3)
        counter_box = (self.rect[0], self.rect[1] + self.rect[3]/3, self.rect[2], 2 * self.rect[3]/3)

        #Drawing sensor label
        text_surface, rect = GAME_FONT.render(self.label, white)
        screen.blit(text_surface, (label_box[0] + (label_box[2]/2 - rect.width/2), label_box[1] + (label_box[3]/2 - rect.height/2)))

        #Drawing sensor value
        text_surface, rect = GAME_FONT.render(str(self.value), white)
        screen.blit(text_surface, (counter_box[0] + (counter_box[2]/2 - rect.width/2), counter_box[1] + (counter_box[3]/2 - rect.height/2)))


class Alert:
    #Set time limit for the alert here
    def __init__(self):
        self.timer = 15
        self.rect = (0, 2/3 * display_height, display_width, display_height/3)
        self.reason = None
    
    #Method to draw Alert object and subtract 1 from timer
    def draw(self, screen, details=None):
        #Check to see if alert is active but a false positive
        self.check_cursor()

        if self.reason is not None:
            self.timer -= 1/10
            if self.timer > 0:
                #Draw a red box with the sensor info and timer if sensor was triggered
                pygame.draw.rect(screen, red, self.rect)
                text = f"Sensor '{self.reason['label']}' was triggered."
                text_surface, rect = GAME_FONT.render(text, black)
                screen.blit(text_surface, (self.rect[0] + (self.rect[2]/2 - rect.width/2), self.rect[1] - 20 + (self.rect[3]/2 - rect.height/2)))
                
                text = f"Press here within {int(self.timer)}s to disable alert."
                text_surface, rect = GAME_FONT.render(text, black)
                screen.blit(text_surface, (self.rect[0] + (self.rect[2]/2 - rect.width/2), self.rect[1] + 20 + (self.rect[3]/2 - rect.height/2)))
            else:
                #Draw red box saying 'help has been requested' if timer expires, and send alert reason to main loop
                pygame.draw.rect(screen, red, self.rect)
                text = f"Help has been requested."

                text_surface, rect = GAME_FONT.render(text, black)
                screen.blit(text_surface, (self.rect[0] + (self.rect[2]/2 - rect.width/2), self.rect[1] + (self.rect[3]/2 - rect.height/2)))

                return self.reason
        else:
            #If no alert, draw green box
            pygame.draw.rect(screen, green, self.rect)
            text = f"No alerts :)"
            
            text_surface, rect = GAME_FONT.render(text, black)
            screen.blit(text_surface, (self.rect[0] + (self.rect[2]/2 - rect.width/2), self.rect[1] + (self.rect[3]/2 - rect.height/2)))
        return False


    #Reset timer on false-positive
    def reset(self):
        self.reason = None
        self.timer = 15


    #Check whether cursor is in bounds of the sensor box on screen, and return a Boolean
    def check_cursor(self):
        if self.reason is not None:
            x, y = pygame.mouse.get_pos()
            if (x > self.rect[0]) and (x < self.rect[0] + self.rect[2]) and (y > self.rect[1]) and (y < self.rect[1] + self.rect[3]):
                if pygame.mouse.get_pressed()[0]:
                    self.reset()

    
class App:
    def __init__(self):
        #Setup personal details here
        self.personal_details = {
            "first_name" : "John",
            "last_name" : "Doe",
            "contact_number" : "91234567",
            "nric" : "S1234567A",
            "address" : "123 Fake Street",
            "allergy_info" : "NIL",
            "blood_type" : "B+"
        }

        self.auth = {
            "username" : "test123",
            "password" : "test123"
        }


        #Setup responder details here
        #POST response sent to self.alert_url attribute when a sensor is triggered and not disabled
        #Response contains:
        #-Location
        #-User details
        #-Incident type
        self.alert_url = "https://ems-teamstay.mybluemix.net/alert"


        #Create sensors here
        self.sensors = {}

        #Heart rate sensor
        self.sensors["hr"] = {
            #In case we add on other methods/attributes, read using this value
            "sensor_obj" : Sensor("Heart Rate", 60),
            #Store last_read value for when we need to override the value
            "last_read" : 60
        }

        #Accelerometer
        self.sensors["accel"] = {
            "sensor_obj" : Sensor("Accelerometer", 0),
            "last_read" : 0
        }

        

        #To-Do : Change accelerometer to more advanced stuff
        self.sensors["accel"]["sensor_obj"].value = [0]
        self.sensors["accel"]["sensor_obj"].read = self.sensors["accel"]["sensor_obj"].accel_read
        self.sensors["accel"]["sensor_obj"].draw = self.sensors["accel"]["sensor_obj"].accel_draw

        

        #Determine how many 'columns' are needed based on number of sensors (50px border on either edge)
        col_width = (display_width - 100) / len(self.sensors.keys())

        #Width var for count
        current_width = 50

        #Assign a bounding box to each sensor for drawing
        for sensor in self.sensors.values():
            sensor["sensor_obj"].rect = (current_width, display_height / 3, col_width, display_height / 3)
            current_width += col_width

            #Print sensor label and bounding box for debugging purposes
            print(sensor["sensor_obj"].label)
            print(sensor["sensor_obj"].rect)

        
        #Setup Alert object here
        self.alert = Alert()

        #Set up notify flag so that notification will only be sent once
        self.notify = False

        
        #Setup sensor trigger conditions here
        #Simple sensor triggers (crossed threshold) setup for demonstration purposes, 
        #but more advanced techniques could be used in a real life implementation
        self.triggers = {
            "hr" : (10, 130),
            "accel" : (-30, 85)
        }


#Convert accelerometer data to image bytestring
def arraytoimage(array):
    np_intensity_array = np.asarray(array)
    np_intensity_array = np.reshape(np_intensity_array, (15,15))
    img = Image.fromarray(np_intensity_array)
    img = img.convert("L")
    img = img.resize((30, 30), Image.NEAREST)
    print(base64.b64encode(img.tobytes()).decode('utf-8'))
    return base64.b64encode(img.tobytes()).decode('utf-8')



#Convenience method to close program
def quitgame():
    pygame.quit()
    quit()


def setup():
    #Create new app instance
    app = App()

    #Begin main program loop
    safe_loop(app)


def safe_loop(app_instance):
    #Main display/control loop
    while True:
        #Check sensor data here
        for sensor_key in app_instance.sensors.keys():
            #Read current value
            sensor_value = app_instance.sensors[sensor_key]["sensor_obj"].read()
            #Check if current value of sensor exceeds preset threshold, and begin alarm if so
            if (sensor_value < app_instance.triggers[sensor_key][0] or sensor_value > app_instance.triggers[sensor_key][1]) and app_instance.alert.reason is None:
                app_instance.alert.reason = {
                    "label" : app_instance.sensors[sensor_key]["sensor_obj"].label, 
                    "value" : app_instance.sensors[sensor_key]["sensor_obj"].value
                }


        #Check keypresses for debugging input
        for event in pygame.event.get():
            #If 'Quit' button on top right is pressed
            if event.type == pygame.QUIT:
                quitgame()
            if event.type == pygame.KEYDOWN:
                #If 'w' is pressed over the sensor space, it increments its value by 1
                if event.key == pygame.K_w:
                    for sensor in app_instance.sensors.values():
                        if sensor["sensor_obj"].check_cursor():
                            sensor["sensor_obj"].value += 1
                #If 's' is pressed over the sensor space, it decrements its value by 1
                if event.key == pygame.K_s:
                    for sensor in app_instance.sensors.values():
                        if sensor["sensor_obj"].check_cursor():
                            sensor["sensor_obj"].value -= 1
                #Debug tool; reset sensors to original values
                if event.key == pygame.K_r:
                    app_instance.sensors["hr"]["sensor_obj"].value = 60
                    app_instance.sensors["accel"]["sensor_obj"].value = [0]
                    #app_instance.alert.reset()
                    #app_instance.notify = False
                #Debug tool; set heart rate sensor to trigger value
                if event.key == pygame.K_t:
                    app_instance.sensors["hr"]["sensor_obj"].value = 150
                #Debug tool; set accelerometer to trigger value
                if event.key == pygame.K_y:
                    app_instance.sensors["accel"]["sensor_obj"].value.append(100)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        app_instance.alert.reset()
                        app_instance.notify = False

        #Reset display every tick
        game_display.fill(black)

        #Redraw sensor labels and values every tick
        for sensor in app_instance.sensors.values():
            sensor["sensor_obj"].draw(game_display)

        alert = app_instance.alert.draw(game_display)

        #If alert timer expires, send notification to awaiting Node-RED flow, then switch to alert loop
        if alert and not app_instance.notify:
            #Post to specified URL until 'OK' status code is returned
            resp = None
            while resp is None or resp.status_code != requests.codes.ok:
                #If alert was because of accelerometer, convert the array into an image bytestring to be sent
                if alert["label"] == "Accelerometer":
                    alert["value"] = arraytoimage(alert["value"])

                #Data to be sent in the request
                data = {
                    "personal_details" : json.dumps(app_instance.personal_details),
                    "location" : "TODO - Location Data Here",
                    "incident_type" : json.dumps(alert),
                    "auth" : json.dumps(app_instance.auth)
                }

                #GET request to the specified URL, and returns the response
                resp = requests.get(app_instance.alert_url, params=data)

                #Printing status code to debug
                print(resp.status_code)

            #Update 'notify' attribute to reflect that a notification has been sent
            app_instance.notify = True

        #Update screen
        pygame.display.update()
        clock.tick(10)


if __name__ == "__main__":
    setup()