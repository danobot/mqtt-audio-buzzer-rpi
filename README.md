# Audio Buzzer

Simple Python MQTT Audio Buzzer packaged in a Docker container. Image available on Docker Hub as `danobot/buzz`. For use case and more information check out [the associated post on my blog](https://danielha.tk/2018/07/24/python-docker-mqtt-audio-buzzer.html).

## Hardware Requirements
* Connect a small buzzer-type speaker to a pin on the Raspberry Pi. (Again, [blog post](https://danielha.tk/2018/07/24/python-docker-mqtt-audio-buzzer.html) goes into more detail)

## Configuration Options
* Command line parameters to script (for script use)
* environment variables (for Docker and other applications)

## Command line

See gpio.py for command line options to override default values.

## Getting started
Add the following entry to your docker compose file. Uncomment and overwride the environment variables as necessary. These will be used as defaults.

```
buzz:
  image: danobot/buzz
  container_name: buzz_ha
  environment:
    MQTT_TOPIC: "/buzz"
    MQTT_HOST: "10.1.1.130"
    # GPIO_PIN: 18
    # BUZZER_REPS: 1
    # BUZZER_PAUSE: 1
    # BUZZER_LENGTH: 20
    # BUZZER_COUNT: 1
  devices:
    - /dev/gpiomem
```

### Cloning the repository
You may clone the repository and bulid the image yourself for your particular architecture. 

## Features

|Topic|Feature|
|---|---|
|<MQTT_TOPIC>|Will produce sound according to default options. If MQTT payload is supplied, default options will be overwritten.|
|<MQTT_TOPIC>/short|Produces single short beep|
|<MQTT_TOPIC>/long|Produces single long beep|
|<MQTT_TOPIC>/alarm|Produces alarm|

MQTT Payload Example format:
```
{
  "reps": 3,
  "pause": 0.6,
  "length":20,
  "count":3
}
```

The `pause` value is in seconds, `length` is the duration of the audio tone and measured in milliseconds.

# Home Assistant Integration
I created scripts that can be triggered in automations to encapsulate these MQTT messages.

```yaml
buzz_short:
  alias: Buzz Short
  sequence:
    - service: mqtt.publish
      data:
        topic: "/buzz/short"

buzz_long:
  alias: Buzz Long
  sequence:
    - service: mqtt.publish
      data:
        topic: "/buzz/short"

buzz_alarm:
  alias: Buzz Alarm
  sequence:
    - service: mqtt.publish
      data:
        topic: "/buzz/alarm"

buzz_custom:
  alias: Buzz custom
  sequence:
    - service: mqtt.publish
      data:
        topic: "/buzz"
        payload: >
          {
            "reps": 2,
            "pause": 0.6,
            "length": 10,
            "count": 3
          }
```

You can call them in automations using:

```yaml
- service: script.buxx_short
```
