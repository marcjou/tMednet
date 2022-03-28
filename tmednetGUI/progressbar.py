
class Progress_bar:

    def __init__(self, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end='', console=False):
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.fill = fill
        self.print_end = print_end
        self.console = console
        self.print_progress_bar(0)

    def print_progress_bar(self, iteration):
        percent = ('{0:.' + str(self.decimals) + 'f}').format(100 * (iteration / float(self.total)))
        filledLength = int(self.length * iteration // self.total)
        bar = self.fill * filledLength + '-' * (self.length - filledLength)
        # TODO it freezes the console and it only updates after the loop which isn't useful at all, maybe raise a label?
        if self.console:
            self.console.delete('insert linestart', 'insert lineend')
            consolelen = int(self.length / 2)
            consolefillen = int(consolelen * iteration // self.total)
            consolebar = self.fill * consolefillen + '-' * (consolelen - consolefillen)
            self.console.insert("end", f'\r{self.prefix} |{consolebar}| {percent}% {self.suffix}')
            if iteration == self.total:
                self.console.insert("end", '\n')
        else:
            print(f'\r{self.prefix} |{bar}| {percent}% {self.suffix}', end=self.print_end)
            if iteration == self.total:
                print()
