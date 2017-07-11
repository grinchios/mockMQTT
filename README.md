To run the software enter the command, python3 server.py <IPADDRESS>

On the client device run, python3 client.py <IPADDRESSOFSERVER>

It's important to distribute the program with util.py since this is the main structure
of running the scripts.

Subscribing is done through the first command in the format,
userid=<ID> topic=<TOPICNAME> qos=<QOS>

userid is an integer value corresponding to the predetermined nodeid
nodeid's cannot be the same or errors will arise, this shouldn't
happen if all the node's have their own id

messaging is done by typing your message or entering a full publish command
topic=<TOPICNAME> <PAYLOAD> qos=<QOS>

Topic can be changed whilst the program is running via the command
topic=<NEWTOPICNAME>

Userid can also be changed however it must be to a new value
this value is appened to userid00 so it can easily be determined which
node has published

exceptions are temp, hum or lum. These are resevered for the main distributers
they have their name as is and aren't appened.

To run tests, run the particular test file and then press enter on the terminal
the script will then send random values every 10 seconds
