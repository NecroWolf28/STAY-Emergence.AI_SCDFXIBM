# STAY-Emergence.AI_SCDFXIBM
Just a group of students stuck at home during COVID-19 :/

Our team consists of Sean, Timothy, Alex and Yew Meng, and our initials form the word STAY, hence our group name. In this current climate, we thought it was apt since all of us are required to STAY home.

# The Problem and Our Solution
The problem we are tackling is focused on the elderly, especially those who live alone or in a secluded area. If these elderly were to collapse at home or suffer from a cardiac arrest or heart attack, they may be incapacitated and be unable to move to their home phone or mobile phone to make an emergency call. This gave us the idea to utilise wearables with sensors to detect their heart rate as well as accelerometers to detect a fall. There are many of these wearables widely available, from brands such as FitBit. We decided to write a program that will send relevant important data to SCDF (wearer's name, location, incident, etc.) and ensure that the elderly will be provisioned help as soon as possible, and by doing so, greatly increase the chance of survival in these incidents.

# [Our Video Pitch](https://youtu.be/O6f9p4rbXM4)

# Architecture
![Architecture Flow Chart](https://github.com/NecroWolf28/STAY-Emergence.AI_SCDFXIBM/blob/master/resources/architecture.jpeg "Architecture Flow Chart")
![Architecture Flow Chart](https://github.com/NecroWolf28/STAY-Emergence.AI_SCDFXIBM/blob/master/resources/app_flow.png "Architecture Flow Chart")
1. Sensor data from device is sent to Node-RED Server App
2. Data is sent to IBM Watson Visual Recognition for categorization
3. Response is sent back to Node-RED as positive or negative case
4. Device may send cancellation order in case of false positive
5. Emergency alert sent to SCDF

# [Our Detailed Solution](https://docs.google.com/presentation/d/1iO-BQS5iraRGK70F51y7vvYXo1Ny9nYJ-yu_r1TuJtg/edit?usp=sharing)

# Getting Started
The .exe file that would be the software for the wearable can be found in the repo, along with its commented source code.

The Node-RED flow can be found [here](https://ems-teamstay.mybluemix.net/red/#flow/cdae95e1.ea0468), or can be imported into your own Node-RED environment with the JSON file included in the repo (keep in mind that you'll need to change the EMS URL attribute in the App class).

To run the wearable software, simply open the .exe file, or run the app.py file in the source folder.

Once the app is loaded, there are several debugging commands:
* r - Resets the sensors to their starting values
* t - Triggers the heart rate alert
* y - Triggers the accelerometer alert
While hovering over either sensor, press:
* w - Increments sensor reading by 1
* s - Decrements sensor reading by 1

When the alert is triggered, click within the red box to cancel the alert.
If the alert is allowed to trigger, press [r] then [Return] when presented with the 'Help has been requested text' to return to the safe state.

When the alert has been triggered, the personal details preloaded in the software should show up in the Node-RED debug log as the message payload.

# What We Used to Build Our Solution
We used IBM Cloud's Node-RED as an event-driven, non-blocking solution to bridge our software and SCDF's services.
In addition, we managed to train a Watson Visual Recognition Model to help filter out false positives in our results, but failed to properly implement it into our Node-RED flow.

