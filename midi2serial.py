#!/usr/bin/env python
__author__    = 'Dimitri Lizzi'
__copyright__ = 'Copyright 2014, Dimitri Lizzi'
__license__   = 'GPLv2'
__version__   = '0.1'
__status__    = 'Prototype'


import argparse
import pygame.midi
import serial
import threading
import sys
import time


def init_arg_parser():
    """Initializes the argument parser"""
    # Create the argument parser with a short description of the program
    arg_parser = argparse.ArgumentParser(description='Transmits MIDI messages to serial')
    # Add arguments to the parser
    arg_parser.add_argument('--mididevice','-m', help='MIDI input device', metavar='PORT', required=True, type=int)
    arg_parser.add_argument('--serialport','-s', help='Serial port', metavar='PORT', required=True, type=str)
    arg_parser.add_argument('--baudrate','-b', help='Serial baud rate', metavar='RATE', default=9600, type=int)
    arg_parser.add_argument('--quiet','-q', help='Disable serial messages printing', action='store_true')

    return arg_parser

def init_midi_input(port):
    """Initializes pygame.midi and the MIDI input with the given port, returns the MIDI input"""
    pygame.init()
    pygame.midi.init()
    return pygame.midi.Input(port)

def init_serial(port=0,baudrate=9600):
    """Initializes the serial port, returns the serial object"""
    return  serial.Serial(port=port,baudrate=baudrate)

def serialize_midi_event(midi_event):
    """Transforms the give MIDI event to a byte array (timestamp will be ignored), returns the bytes"""
    return bytes(midi_event[0])

def bytes_to_string(bytes, separator=' '):
    """Transforms the given bytes to a string containing hex code of each bytes, returns the string"""
    output_string = ''
    for byte in bytes:
        output_string += hex(byte)
        output_string += separator
    return output_string

def serial_read(ser, rate, quiet, stop_event):
    """Reads the serial input at the given rate and stops when the stop event is set. Intended to be ran as a thread"""
    # While a thread stop event is not received...
    while (not stop_event.is_set()):
        # Reads serial input data (4 bytes max, the rest stays in the queue)
        data = ser.read(4)
        # If data has been read
        if len(data) > 0:
            if not quiet:
                # Print the data
                print("Serial input:  {}".format(bytes_to_string(data)))
                sys.stdout.flush()
        # Waits during the given time
        stop_event.wait(rate)

def midi_to_serial(midi_input, ser, quiet, stop_event):
    """Reads the midi input and send messages to serial and prints sent messages. Intended to be ran as a thread"""
    # While a thread stop event is not received...
    while (not stop_event.is_set()):
            # If midi messages are in queue
            if midi_input.poll():
                # Read the message(s)
                midi_events = midi_input.read(10)
                # For each message received
                for midi_event in midi_events:
                    # Write the message bytes to serial
                    midi_event_bytes = serialize_midi_event(midi_event)
                    ser.write(midi_event_bytes)

                    if not quiet:
                        # Print the message bytes in hexadecimal
                        print("Serial output: {}".format(bytes_to_string(midi_event_bytes)))
                        sys.stdout.flush()


if __name__ == "__main__":
    # Initialize and get the arguments
    arg_parser = init_arg_parser()
    args = arg_parser.parse_args()

    #Initialize midi and serial with the arguments
    ser = init_serial(args.serialport, args.baudrate)
    midi_input = init_midi_input(args.mididevice)

    # Initialize serial reading thread
    serial_read_thread_stop = threading.Event()
    serial_read_thread = threading.Thread(target=serial_read,
                                          args=(ser, 0.001, args.quiet, serial_read_thread_stop))

    # Initialize midi to serial thread
    midi_to_serial_thread_stop = threading.Event()
    midi_to_serial_thread = threading.Thread(target=midi_to_serial,
                                             args=(midi_input, ser, args.quiet, midi_to_serial_thread_stop))

    #Start threads
    serial_read_thread.start()
    midi_to_serial_thread.start()

    # Sleep until there's a keyboard interrupt
    while 1:
        try:
            time.sleep(.1)
        except KeyboardInterrupt:
            break

    # Stop threads
    serial_read_thread_stop.set()
    midi_to_serial_thread_stop.set()
    print('Waiting for threads to stop.')
    time.sleep(1)

    # Close MIDI and serial handlers
    midi_input.close()
    ser.close()