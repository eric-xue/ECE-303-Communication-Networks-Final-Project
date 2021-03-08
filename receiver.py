# Written by S. Mevawala, modified by D. Gitzel

import logging

import channelsimulator
import utils
import sys
import socket

class Receiver(object):

    def __init__(self, inbound_port=50005, outbound_port=50006, timeout=2, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.rcvr_setup(timeout)
        self.simulator.sndr_setup(timeout)

    def receive(self):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class BogoReceiver(Receiver):

    def __init__(self):
        super(BogoReceiver, self).__init__()

    def receive(self):
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        curr_ACK = 1
        timeout_count = 0
        validation_size = 10
        checksum_size = 9
        while True:
            #   rdt3.0
            #   Receive data
            #       Generate checksum and check if matches sent checksum
            #           Checksum dont match: sender resend
            #           Checksum matches: check req ACK num
            #       Check ack num:
            #           Expected ack: decode data and create packet w/ ack
            #           Wrong ack: sender resend

            try:
                 Packet_logged = False
                 ACK_DATA = bytes(curr_ACK)
                 data = self.simulator.u_receive()  # receive data
                 if data == bytes("DONE"):
                    break
                 real_data = data[:len(data)-validation_size]
                 validation_data = data[len(data)-validation_size:]
                 validation_checksum = validation_data[:-1]
                 validation_ack = validation_data[-1]
                 #Simple checksum w/ stackoverflow method to convert to bytes and keep @ constant 9 length
                 checksum = sum(real_data)
                 checksum = ('%%0%dx' % (checksum_size << 1) % checksum).decode('hex')[-checksum_size:]

                 #Deal w/ dropped/corrupted ACK
                 if checksum == validation_checksum and curr_ACK > validation_ack:
                    self.simulator.u_send(bytes(validation_ack))
                    self.logger.info("Got ACK {} instead of {} Dropping packet".format(validation_ack,curr_ACK))
                    timeout_count = 0
                 elif checksum == validation_checksum and curr_ACK == validation_ack:
                    if not Packet_logged:
                        self.logger.info("Got data from socket: {}".format(
                            real_data.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                        self.logger.info("Replying with ACK: {}".format(curr_ACK))
                        # Attempt at fix for issue where this loop or the sender packet sending occurred twice (from checking logs seems like sender would double send w/o w8ing for u_receive)
                        #   which would result in a packet being duplicated in output
                        sys.stdout.write(real_data)
                        Packet_logged = True
                    self.simulator.u_send(bytes(curr_ACK))  # send ACK
                    self.logger.info("Data logged")
                    curr_ACK += 1
                    if curr_ACK > 256:
                        curr_ACK = 1
                    timeout_count = 0
                 else:
                    self.logger.info("Error: Received {} instead of {}".format(validation_ack,curr_ACK))
                    self.logger.info("Replying with ACK: NotSame")
                    self.simulator.u_send(bytes("NotSame"))
            except socket.timeout: #Dropped packet/connection, request resend or assume connection dropped and exit
                self.simulator.u_send(bytes("Timeout"))
                timeout_count += 1
                if timeout_count == 2:
                    sys.exit()
            except UnicodeDecodeError: #Issue w/ decoding, request resend
                self.logger.info("Error: Unicode error")
#Debug                sys.stdout.write("Error: Resend b/c decode error with ACK=")
                self.simulator.u_send(bytes("Unicode"))
                continue
            except:
                pass

if __name__ == "__main__":
    # test out BogoReceiver
    rcvr = BogoReceiver()
    rcvr.receive()
