# Written by S. Mevawala, modified by D. Gitzel

import logging
import socket
import math

import channelsimulator
import utils
import sys

class Sender(object):

    def __init__(self, inbound_port=50006, outbound_port=50005, timeout=2, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.sndr_setup(timeout)
        self.simulator.rcvr_setup(timeout)

    def send(self, data):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class BogoSender(Sender):

    def __init__(self):
        super(BogoSender, self).__init__()

    def send(self, data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        #ack_received = False
        # rdt3.0
        # Initial: Ack not received so send and start timeout
        # Subsequent:
        #       ACK not received: wait
        #          - Timeout: resend
        #          - Ack arrives: check if ACK matches what is expected [0 or 1]
        #               ACK diff = resend
        #               ACK same = check checksum
        #                   - Checksum diff = packet corrupted, resend
        #                   - Checksum same = packet ok, send next

        #Break sent data into smaller chunks so easier to fix corrupted data
        n = 1000
        data_chunks = [data[i * n:(i + 1) * n] for i in range((len(data) + n - 1) // n)]
        expect_ACK = 1
        timeout_count = 0
        resend = False
        for data_segment in data_chunks:
#Debug            sys.stdout.write("\nsending next chunk\n")
            self.logger.info("Sending next chunk\n")
            while True:
                try:
                    #If resending, just send what already have
                    if not resend:
                        #Simple checksum w/ stackoverflow solution to turn into bytes+maintain length 9
                        checksum = sum(data_segment)
                        length = 9
                        byte_checksum = ('%%0%dx' % (length << 1) %checksum).decode('hex')[-length:]
                        data_segment.extend((byte_checksum))
                        data_segment.extend(bytes(bytearray([expect_ACK])))
                    self.simulator.u_send(data_segment)  # send data
                    self.logger.info("Sent data from socket: {}".format(data_segment))
                    #Received ACK, check if correct
                    ack = self.simulator.u_receive()  # receive ACK
                    if ack == bytes(expect_ACK):
#Debug                        sys.stdout.write("ACK EQUAL\n")
                        self.logger.info("Got ACK from socket: {}".format(
                            ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                        expect_ACK += 1
                        if expect_ACK > 256:    #reset ACK
                            expect_ACK = 1
                        timeout_count = 0
                        resend= False
                        break
                    # If does not break, means ACKs dont match and should resend.
                    self.logger.info("Wrong ACK from socket: {} instead of {}".format(ack,expect_ACK))
                    resend = True
                #If packet dropped, resend
                except socket.timeout:
#Debug                    sys.stdout.write("Socket timed out\n")
                    timeout_count += 1
                    if timeout_count == 3:
                        sys.exit()
                    continue
#Debug        sys.stdout.write("DONE\n")
        self.simulator.u_send(bytes("DONE"))
        sys.exit()


if __name__ == "__main__":
    # test out BogoSender
    DATA = bytearray(sys.stdin.read())
    sndr = BogoSender()
    sndr.send(DATA)
