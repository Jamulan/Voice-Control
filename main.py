# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from vosk import Model, KaldiRecognizer
from queue import Queue
import threading
import os
import pyaudio

numWorkers = 2

inputQueue = Queue()
inputQueueLock = threading.RLock()

outputQueue = Queue()
outputQueueLock = threading.RLock()


def worker():
    inputQueueLock.acquire()
    while True:
        # get an item
        item = inputQueue.get()
        inputQueueLock.release()
        # process item



        output = item
        # send out the output
        outputQueueLock.acquire()
        outputQueue.put(output)
        outputQueueLock.release()
        # mark item as processed
        inputQueueLock.acquire()
        inputQueue.task_done()


def driver():  # enqueues stuff
    if not os.path.exists("model"):
        print(
            "Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current "
            "folder.")
        exit(1)

    model = Model("model")
    rec = KaldiRecognizer(model, 16000)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    while True:
        data = stream.read(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            inputQueue.put(rec.Result())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    d = threading.Thread(target=driver, name="driver", daemon=True)
    workers = []
    for _ in range(numWorkers):
        workers.append(threading.Thread(target=worker, name="worker", daemon=True))
    for w in workers:
        w.start()
    d.start()

    while True:
        print(outputQueue.get())