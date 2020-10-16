# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from vosk import Model, KaldiRecognizer
from queue import Queue
from pythonActions import Actions
import threading
import os
import pyaudio
import json
import subprocess

numWorkers = 2

inputQueue = Queue()
inputQueueLock = threading.RLock()

outputQueue = Queue()
outputQueueLock = threading.RLock()

actions = Actions()

def worker():
    inputQueueLock.acquire()
    while True:
        # get an item
        item = inputQueue.get()
        inputQueueLock.release()
        # process item
        j = json.loads(item)
        words = []
        output = ''
        if 'result' in j.keys():
            for x in j['result']:
                words.append(x['word'])

        if actions.keyword in words:
            i = words.index(actions.keyword)
            tmp = ""
            for word in words[i + 1:]:
                tmp += word + " "
            tmp = tmp[:-1]  # get rid of the last space
            if tmp in actions.responses.keys():
                output = actions.responses[tmp]
            elif tmp in actions.commands.keys():
                output = str(subprocess.run(actions.commands[tmp], capture_output=True, encoding='utf-8').stdout)
            elif tmp in actions.pythonActions.keys():
                output = getattr(Actions, actions.pythonActions[tmp][0])(actions, actions.pythonActions[tmp][1])
            else:
                output = "unknown command: " + tmp
        else:
            output = "unknown string: " + str(j['text'])
            if 'text' in j.keys() and j['text'] == '':
                output = ''
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
    actions.loadDatabase(0)
    d = threading.Thread(target=driver, name="driver", daemon=True)
    workers = []
    for _ in range(numWorkers):
        workers.append(threading.Thread(target=worker, name="worker", daemon=True))
    for w in workers:
        w.start()
    d.start()

    while True:
        output = outputQueue.get()
        if output != '':
            print(output)
            subprocess.run(["flite", "-voice", "slt", "-t", output])
        outputQueue.task_done()
