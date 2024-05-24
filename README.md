# FFS - First Functioning Software

Policumbent's on board Raspberry Pi's software (modules) which will manage:
- ANT+ sensors
- Video and digital camera
- CAN Bus communications and logging

## General understanding

Since the Raspberry Pi manages both the digital screen (with the Raspberry Pi
Camera Module) and data gathering (via ANT+ and CAN bus), we need a software
that takes care of all of that.

## Modules communication

Since FFS is made up by three modules (`ant`, `can`, `video`) which communicate
with each other with OS FIFOs.

### FIFO messages

#### ANT module

| Sends         | Sensor Name  |
|---------------|--------------|
| ANT Speed     | ant_speed    |
| ANT Distance  | ant_distance |
| Power         | power        |
| Cadence       | cadence      |
| Heartrate     | heartrate    |

It does not receive anything from the other modules.

#### CAN module

| Sends             | Sensor Name       |
|-------------------|-------------------|
| Gear              | gear              |
| GNSS Speed        | gnss_speed        |
| GNSS Displacement | gnss_displacement |

| Receives  | Sensor Name |
|-----------|-------------|
| Power     | power       |
| Cadence   | cadence     |
| Heartrate | heartrate   |

#### Video module

| Receives          | Sensor Name       |
|-------------------|-------------------|
| ANT Speed         | ant_speed         |
| ANT Distance      | ant_distance      |
| Power             | power             |
| Cadence           | cadence           |
| Heartrate         | heartrate         |
| Gear              | gear              |
| GNSS Speed        | gnss_speed        |
| GNSS Displacement | gnss_displacement |