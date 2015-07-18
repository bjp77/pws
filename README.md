# Personal Weather Station Observer

The PWS Obersver is an application written in Python that connects to a PWS
console, periodically samples console data, and then stores the data in a
Mongo database.  A plugin framework is used to allow support for additional
consoles to be added easily. It also provides support for "emitter" plugins
that can transform and send weather data to some remote source.

Overall goals of this project are:
1. To provide more access and control to the raw data.
2. To run in the background without a clumsy GUI.
3. To provide support for uploading data to a remote location such as Weather
   Underground.
3. To run on any platform (although it has only been tested with Ubuntu Server).
5. To cleanly recover from common failures such as loss of network connectivity
   and loss of PWS connectivity.
   
At this point most of these things are still a work in progress.

## Console Plugins

While at the moment, only Davis Vantage Vue and Pro2 weather stations are 
supported, plugins for any type of PWS console can be added.  

To add a console plugin:
1. Create a new python file in the consoles directory.
2. Create a class within this new file.
3. Create a @classmethod called discover()
3. Create an instance method called measure()

The job of the discover method is to look for a connnected console and, if one
is found, return an instance of the plugin class.  The measure() method should
read data from the console and return a dictionary of key/value pairs
corresponding to each measured value.

Note that only the first console plugin that finds something will be used.
There is no support for connections to multiple consoles.

## Emitter Plugins

Only a dummy plugin is supported at the moment, but a Wunderground emitter will
be available soon.

To add an emitter plugin:
1. Create a new python file in the emitters directory.
2. Create a class within this new file.
3. Create a @classmethod called connect()
3. Create an instance method called send(data)

Like the console plugins, two methods are required.  The job of the connect()
method is to connect to the remote site and return an instance of the
emitter class if successful.  The send(data) method takes a dictionary as an
argument, transforms this data into a format suitable for the remote site, and
transmits the data.

Unlike console plugins, many emitters are supported.  Data will be sent to each
emitter that returns an instance from its discover method.

