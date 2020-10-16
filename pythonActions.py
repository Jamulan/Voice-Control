from time import sleep
import json
import os
import subprocess

class Actions:
    database: dict
    keyword: str
    commands: dict
    responses: dict
    pythonActions: dict
    path = "interactionDatabase.json"

    def timer(self, secs):
        sleep(secs)
        return "timer done"

    def loadDatabase(self, x):
        if not os.path.exists(self.path):
            path = "interactionDatabase.json"
        with open(self.path, 'r') as f:
            self.database = json.loads(f.read())
            self.keyword = str(self.database['keyword'])
            self.commands = self.database['commands']
            self.responses = self.database['responses']
            self.pythonActions = self.database['python actions']
            self.path = self.database['path']
        return "database loaded"

    def count(self, x):
        output = ""
        for i in range(x[0], x[1]):
            output += str(i+1) + " "
        return output