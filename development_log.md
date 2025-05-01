### To do
 - [ ] Make a base object `M_QWidget` that has all of the built-in stuff I want
    - [x] Logging
    - [x] Basic signals & slots
    - [ ] Clean exit
	    - [ ] Close connections
    - [x] Mqtt
    - [x] Status bar printing
- [ ] Adapt all the current widgets in `custom_qt_widgets.py` to be `MW_QWidget`'s
- [ ] Build a basic `M_QMqtt` object that has all of the basic functionality I want
	- [ ] replace the current class in `custom_qt_mqtt.py` with class that are defined within the class that they are used. They would extend the `M_QMqtt` base class.
- [ ] Create the NIDaqmx process that does the actual data capture
- [ ] Finish building the widgets for the tabs for a basic MVP
	- [ ] Needs to start/stop the data capture
	- [ ] Needs to store the raw data in a tdms file
	- [ ] Needs to plot the data in real-time on the app
	- [ ] Needs to be able to recall and plot the raw-data

## 04-22-2025
- Reorganized some code
- Planned out my next couple steps to building the first release

## 04-23-2025
- Working on `M_QObject`
	- Setting up the logger
	- Setting up basic Mqtt
- Re-implemented my original mqtt objects with `M_QObjects`
- Re-organizing the file structure such that all the objects for each widget are in the same file
- Re-working the sensor plots
- updated `M_QObject` to have a defined `log()` function and a `emit_and_log()` function
- Made the graphs expand the fill the screen
- Fixed all of the multiple inheritance mess
- Adjusted the way that the status bar is handled, now it's passed as an object rather than as a signal. Less to remember
- Working on the tool bar for experiment control
- Working on developing out `M_ActionSignleton`

## 04-24-2025
- trying to setup the venv / dependencies better than before
	- using an install script and `requirements.txt` document
	- Finished building a nice install script
	- Also made an uninstaller
- Had to remove the singletonness of the actions for the time being
- It now compiles and runs on multiple desktop envs. I should also make an equivalent install script for Windows.
	- I'll get buddy gpt to do convert it later.
- I want to spend some time today and work on the ni-daqmx side of things

## 04-28-2025
- Created a logger singleton, rather than extending it. Now I am going to decouple the logger and make each object create a copy of the singleton.
- Creating a single for each Mqtt Client type 
	- Sensor data (done and needs to be tested)
	- Status lights (done and needs to be tested)
	- Experiment Control
	- Mould Control
- Working on decoupling mqtt from qt
- Made a logger and generic mqtt sub module
	- Created a non-singleton logger as well.
- Added elapsed time and experiment status lights to the alarms. Also made them have a min size
- Next is the experiment control actions I think
- Made the logger setable, and if it's not set it will default to logging in log.log
- It is 1500 right now and everything is currently compiling, next steps I think should be:
	1. Experiment control actions & mqtt
	2. Receiving mqtt commands in the daq process and doing something
	3. Making the graphs work and the experiment status stuff respond
	4. Making sure the data is logging correctly in the tdms
	5. Double checking general logging is working
- Refactoring further.
- Taking a break at 1530 until 1600
- refactoring further.
- Really getting into the weeds of the daq process, making it very configurable and a singleton, really hope it works so I don't have to redo it.
- Currently 1700, stopping for a snack, then back to it.


## 04-29-2025
- Goal: Make the DAQ process work!
- DAQ object has:
	- Load from config
	- Call backs
- Everything compiles right now and throws minimal errors, but all of the structure is there, it should work. It's time to test
- I noticed a weird behaviour in testing. Basically what is happening is that I init everything with a Log called "DAQ.log", but what is happening is that after the process is created (and likely after pickeling) it's overwriting it to default and creating a new log called "log.log" the default name
	- Fixed it, I wasn't correctly setting the log name
- I have a new weird behaviour now, it's creating a duplicate process.
	- So it's connecting and everything works, but there are 2. I may need to make the process a singleton
	- I figured it out with some help from buddy gpt.
- Current state, the process is a starts, stops safely, is a singleton
	- need to test full functionality
	- connect it to the gui
- adjusted main.py to start the daq process correctly and kill it correclty
- it's getting very close, tomorrow I should be able to complete everything and then start doing some testing.

### To-do - tomorrow:
- [ ] Full functionality test, either with mosquitto_pub/sub or the app
- [ ] Connect the data sources to each other
- [ ] Finish implementing all the graphs
- [ ] Let it run for a while
- [ ] Make a seperate file for SensorData & other base models
- [ ] Clean up and improve
- [ ] Figure out how to do make a start-up window that allows you to configure the DAQ and then start it.
- [ ] Start to look into the SEN stuff

## 04-30-2025
- Integrated David's logger into the `GenericMQTTeLogger` repo
- Working on adapting the rest of the code
	- Should be done, need to test
	- Found an issue with David's logger where:
		- Defualt level was set too high
		- Multiple set of handlers were being created and causing problems like duplicate messages
- Added safe start up and close down using multiprocessing.Event
- Logging is working and everything starts!
- Made a logger and daq config and moved the base models
- turning all the mqtt stuff into singletons and adapting the configs
	- Actions
	- SensorsMQTT
	- StatusLightsMQTT
- Switching to absolute import and running with `python -m main.py`
- Fixed many bugs
- Adapted more or less everything to some sort of config file
- Everything starts up nicely, and seems to be working. Need to finish implementing actions so I can do full func testing.
- I setup the menu bar and it's working now, and fills the entire screen.

## 05-01-2025
- Setting up a config for the topic names for the different sections. 
- Chaning the static configs to be properly static for now. In the future we may want these to be configurable, but for now they will be static.
	- updated StatusLightsMqtt and QT_NCM_Status_Lights
	- upadted SensorsMqtt and QT_NCM_Sensrs
	- updated DAQ
- Testing everything
- Removed the exit action
- Fixing some things, I noticed that data is being published but nothing was being subbed to
	- I asked buddygpt and it suggested that I put the sub call backs in an on_connect
	- buddy is also suggesting I sub the add callbacks
- Callbacks are working now, now I need to fix the DAQ.
	- However things are looking good, it made a tdms file!!!
- Double checking that my broker is setup correctly, because I'm eeing some weirdness
	- In file `/etc/mosquitto/mosquitto.conf` added:
	```
	listener 1883
	bind_address 0.0.0.0
	allow_anonymous true
	```
	- allowing on firewall `sudo ufw allow 1883/tcp`
- buddy gpt pointed out an issue with having multiple clients on one machine, they need to have names
- so it's publishing but it's not receiving. Also the daq seems to be kinda responding. 
	- Taking a break to head home will continue from there.
- setup the mqtt broker on wsl, and it's working so far.
	- I'm still trying to debug why messages don't seem to be coming in
	- I'm curious if there is an outbound firewall issue or something like that
	- The bug I'm playing with rn is caused by MQTTv5
	- Also I was hanging the program by accident with `.loop_forever()`
- omg it worked kinda, the exp start and stop toggled the gui
- Okay so I tested the alarms and they work correctly, we just send a 1 or 0 to the corresponding topic and they go
