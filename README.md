[![Build Status](https://travis-ci.org/brianparry/pws.svg?branch=master)](https://travis-ci.org/brianparry/pws)

# Personal Weather Station Observer

The PWS Observer is a personal project that I decided to start for a few
reasons:

1. To give me a way to develop my Python skills
2. Because I was unsatisfied with available personal weather station
software options.
3. Because I like writing software and it seemed like it would be a fun
thing to do.

Most of the PWS software options I've tried have some limitation or another
that make them less than ideal for me.  Mainly, I wanted something that
would:

1. __Run as a daemon__.  My data is uploaded to Weather Underground and I use
www.wunderground.com as my user interface; I didn't want a minimized GUI 
sitting open all the time.  I also wanted to use a service manager to 
automatically start the daemon as well as restart it in the event of a crash.
2. __Recover from connection problems.__  There are two types of connection
problems that commonly plague my weather station.  The first is loss of USB
conenctivity (with three kids running around my house, cables have a tendency
to get unplugged often).  The second is loss of network connectivity which is 
less common but does occasionally happen.  Most of the software I tried
handled loss of network connectivity to at least some extent but nothing 
really handled loss of USB connection very well.  I want to be able to simply
plug the cable back in and automatically gather all of the measurements that
were missed while the cable was unplugged.

Most of this is still a work in progress and I'm not sure I'll ever finish
it, but for the moment the plan is to:

1. Get basic data collection and upload working - Done.
2. Develop setup and Ubuntu upstart scripts - Not started yet.
3. Work on better connection loss handling - Not started yet.
4. Add support for other OSes - Not started yet.

Eventually, I might even try running this on a Rasberry Pi so I don't need
to keep a PC running and consuming power all the time.

# Plugins

To allow the weather station software to be easily extended, I used a
plugin architecture based on Yapsy for "consoles" and "emitters".

The term console refers to the hardware used to interface with the weather 
station sensors.  Typically, consoles use a USB connection to communicate
with a host PC.  Using plugins allows additional weather station types to be 
added in the future without too much trouble.

Emitters are plugins that transmit weather observations to various sites such
as Weather Underground.

## Console Plugins

I have a Davis Vantage Vue weather station, so this is the only console
type currently implemented.  Others can be added using the existing davis
plugin as a template.  The basic requirements are:  

1. Create a new directory in the consoles directory.
2. Create three new files in this directory:
    1. Python source file for the plugin code.
    2. Python `__init.py__` file.
    3. yapsy-plugin file for plugin metadata.
3. Create a new class that inherits from yapsy.IPlugin.IPlugin.
3. Create a `@classmethod` called `discover()`
4. Create an instance method called `measure()`

The job of the discover method is to look for a connnected console and, if one
is found, return an instance of the plugin class.  The measure() method should
read data from the console and return a dictionary of key/value pairs
corresponding to each measured value.

Note that only the first console plugin that returns something other than `None`
will be used.  There is no support for connections to multiple consoles.

## Emitter Plugins

Only a Weather Underground Emitter is currently available.  Adding emitter
plugins is very similar to adding console plugins.  The only differences are:

1. Emitter plugins live in the emitters directory.
2. The two required methods are a `@classmethod` called `connect()` and an
instance method called `send()`.

The job of the connect() method is to connect to the remote site and return an
instance of the emitter class if successful.  The send(data) method takes a
dictionary as an argument, transforms this data into a format suitable for the
remote site, and transmits the data.

Unlike console plugins, many emitters can be used.  Data will be sent to each
emitter that returns an instance from its discover method.

## Quick Start Guide

In the near future, this section will have installation and usage instructions.
