#!/usr/bin/env python

import sys
import time

while True:
    messages_an = [
        'announce route 1.1.1.0/24 next-hop self',
        'announce route 2.2.2.0/24 next-hop self',
        'announce route 3.3.3.0/24 next-hop self',
    ]

    messages_with = [
        'withdraw route 1.1.1.0/24 next-hop self',
        'withdraw route 2.2.2.0/24 next-hop self',
        'withdraw route 3.3.3.0/24 next-hop self',
    ]


    while messages_an:
        message = messages_an.pop(0)
        sys.stdout.write( message + '\n')
        sys.stdout.flush()
        time.sleep(2)

    while messages_with:
        message = messages_with.pop(0)
        sys.stdout.write( message + '\n')
        sys.stdout.flush()
        time.sleep(2)

    time.sleep(2)
