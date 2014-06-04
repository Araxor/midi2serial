# Midi2Serial

A simple script that reads midi messages from a MIDI output, and retransmit it through a serial port.

## Dependencies

The script has been tested with:

- Python 3.3.5
- PyGame 1.9.2a0
- PySerial 2.7

## Arguments

```
usage: midi2serial.py [-h] --mididevice PORT --serialport PORT
                      [--baudrate RATE] [--quiet]

Transmits MIDI messages to serial

optional arguments:
  -h, --help            show this help message and exit
  --mididevice PORT, -m PORT
                        MIDI input device
  --serialport PORT, -s PORT
                        Serial port
  --baudrate RATE, -b RATE
                        Serial baud rate
  --quiet, -q           Disable serial messages printing
```

## Examples

Listens from MIDI output device 7 and repeat the messages to serial port COM1 at 9600 baud (default baud rate):
```
python midi2serial.py -m 7 -s COM1
```

Listens from MIDI output device 7 and repeat the messages to serial port COM1 at 38400 baud:
```
python midi2serial.py -m 7 -s COM1 -b 38400
```

Listens from MIDI output device 7 and repeat the messages to serial port COM1 without writing the transmitted messages
to stdout:
```
python midi2serial.py -m 7 -s COM1 -q
```


## License

This project is licensed under the terms of the GPL version 2 license.