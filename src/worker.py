import os
from time import perf_counter, sleep
from celery import Celery
from celery.contrib.abortable import AbortableTask
import pandas as pd
import numpy as np

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(bind=True, base=AbortableTask)
def session(self: AbortableTask, filename: str):
    count = 0
    data = []
    t0 = perf_counter()
    while True:
        # Logic to read data
        e1, e2, e3 = np.random.rand(), np.random.rand(), np.random.rand()
        data.append([perf_counter() - t0, e1, e2, e3])
        if count == 1000:
            if self.is_aborted():
                pd.DataFrame(data.copy(), columns=["time", "y1", "y2", "y3"]).to_csv(f"static/{filename}", index=False)
                return "Finished"
            count = 0
        count += 1
        sleep(0.0025)
