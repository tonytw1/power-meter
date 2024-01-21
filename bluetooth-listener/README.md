## Bluetooth listener

Passively listens for Bluetooth LE advertisements from our pulse counter.
Parses the payload and publishes it onto a MQTT channel.

Additional permissions required to run as non root.

```
sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/local/lib/python2.7/dist-packages/bluepy/bluepy-helper
```


### Install

To install as a systemd service:

```
sudo cp bluetooth-listener.service /etc/systemd/system/
sudo systemctl start bluetooth-listener
sudo systemctl enable bluetooth-listener
```
