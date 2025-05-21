class TokenCreator(object):
    #
    # M E S S A G E   T O K E N S
    #
    # TOKEN FORMAT (32 bits): 0xPGGXNNNN
    #    P  - message priority
    #    G  - message group
    #    X  - not used
    #    N  - message number
    #
    @staticmethod
    def create_token(priority, message_group, number):
        # type: (str, str, str) -> int
        while len(number) < 4:
            number = "0" + number

        while len(message_group) < 2:
            message_group = "0" + message_group

        return int("0x" + priority + message_group + "0" + number, 16)
