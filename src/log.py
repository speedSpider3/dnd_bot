class Logger:
    def __init__(self):
        self.buffer_out = [] # sends data to file
        self.buffer_in = [] # sends data to user
        self.log = 'log.bot'

    def queue_data(self, *args):
        for data in args:
            self.buffer_out.append(data)

    def write(self):
        f = open(self.log,'a')
        for x in self.buffer_out:
            f.write(str(x) + '\n')
        f.close()
        self.dump_buffer_out()

    def read(self):
        f = open(self.log, 'r')
        for data in f:
            self.buffer_in.append(data)
        f.close()
        self.clean()
        logs = self.buffer_in
        self.dump_buffer_in()
        return logs

    def dump_buffer_in(self):
        self.buffer_in = []
    
    def dump_buffer_out(self):
        self.buffer_out = []

    def clean(self):
        f = open(self.log, 'w')
        f.write('')
        f.close()