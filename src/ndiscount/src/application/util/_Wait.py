from time import sleep

from application.model import TimeoutException


def wait(timeout=15):
    wait_time, rate, total = 0.250, 2, 0

    while total < timeout:
        wait_time = min(wait_time, timeout - total)
        sleep(wait_time)

        wait_time *= rate
        total += wait_time

        yield None

    raise TimeoutException()
