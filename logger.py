class Logger:
    def __init__(self, log_file):
        self.log_file = open(log_file, 'a')

    def log(self, text):
        self.log_file.write(text)
