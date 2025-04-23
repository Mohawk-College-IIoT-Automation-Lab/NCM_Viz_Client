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
- 
