# ece303
This repository contains teaching material for ECE303.
_This API is subject to change and expansion!_

`channelsimulation.py` contains a simple API for a mock connection over an unreliable channel. `sender.py` and `receiver.py` are mock sender and receivers that use this unreliable channel. These are examples that do not properly handle the bit errors in the channel.

The channel simulator will simulate random bit errors, packet loss, and packet duplication.

## Assignment
The goal of this project is to develop a transport layer protocol that can successfully and quickly transmit bits over this unreliable channel. The protocol will be implemented in your versions `sender.py` and `receiver.py`. Your implementations should inherit from the Bogo{Receiver,Sender} classes in from this repository and override the receive() and send() methods.

### Requirements
The submitted sender and receiver implementations must be able to:
* Sucessfully transfer data over the noisy channel
* Be fast
* Keep channelsimulator.py unchanged in any submitted code.  You can play around with it while testing, but submissions will be rejected if you submit a changed channelsimulator.py  
 
## Grading
The grading policy for this project is as follows:
* Competitive performance (35%): protocol performance will be determined relative to a reference implementation and to the class.
* Minimum functionality (60%): protocol must be able to transmit and acknowledge receipt of data packets through the unreliable channel.
* Implementation documentation (5%): Basic code comments for complicated areas of code.

## Due Date
This project will be due May 16th before noon for Seniors and May 18th before noon for Juniors and Sophomores.
Please submit files in an archive via email, or provide a link to a public repository.

## Test Run
To run your code, you just have to use "make test" and to check if works, you can either diff the fiies or run "make diff".

Also, I am using "base64 /dev/urandom | head -c 100000 |tr -d '\n' > file_1.txt" to generate my input files.  Will be testing 10 MB, 25 MB, and 100MB files.  I provide a 1 MB  file and a 4B file in the repo that you can use to test. 


