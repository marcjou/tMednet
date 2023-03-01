#Class used to access the log file and modify it
class LogWriter:
    LOG_PATH = '../src/tmednet_log.txt'
    def __init__(self, site, new_log_line):
        self.data = []
        self.open_file()
        self.insert_data(site, new_log_line)
        self.write_file()

    def __str__(self):
        return "<LogWriter object>"

    def open_file(self):
        with open(LogWriter.LOG_PATH, 'r') as file:
            self.data = file.readlines()

    def insert_data(self, site, new_log_line):
        if type(new_log_line) == str:
            new_log_line = [new_log_line]
        lookfor = '****Site code: {}****\n'.format(site)
        separator = self.data[0]
        # Find the last line of the site on the log to write new information
        insert_index = self.data.index(lookfor) + self.data[self.data.index(lookfor):].index(separator) - 2
        count = 0
        for line in new_log_line:
            self.data.insert(insert_index + count, '-' + line + '\n')
            count = count + 1

    def write_file(self):
        with open(LogWriter.LOG_PATH, 'w') as file:
            file.writelines(self.data)

    def get_data(self):
        return self.data

    @classmethod
    def get_path(cls):
        return cls.LOG_PATH
