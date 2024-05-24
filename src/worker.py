import os
from time import perf_counter

from celery import Celery
from celery.contrib.abortable import AbortableTask
import pandas as pd
from smbus2 import SMBus

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(bind=True, base=AbortableTask)
def session(self: AbortableTask, filename: str):
    count = 0
    data = []
    t0 = perf_counter()
    with SMBus(3) as bus:
        bus.pec = 1
        bus.read_i2c_block_data(0x42, 0, 24)
        while True:
            # Logic to read data
            msg = bytes(filter(lambda x:x != 255, bus.read_i2c_block_data(0x42, 0, 24))).decode("utf-8").split(",")
            data.append([perf_counter() - t0, *msg])
            if count == 1000:
                if self.is_aborted():
                    pd.DataFrame(data.copy(), columns=["time", "y1", "y2", "y3"]).to_csv(f"static/{filename}", index=False)
                    return "Finished"
                count = 0
            count += 1

