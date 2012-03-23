import os
import pyinotify
import re
import time
import traceback

watches = []
ii_path = ''

class Event(object):
    def __init__(self, when, user, message, channel):
        self.when, self.user, self.message, self.channel = when, user, message, channel

    def respond(self, message):
       self.send('%s: %s' % (self.user, message))

    def send(self, message, channel=None):
        global ii_path
        channel = channel or self.channel
        in_path = os.path.join(ii_path, channel, 'in')
        with open(in_path, 'w') as f:
            f.write(message + '\n')

def observe(pattern='(.*)', channel='.*'):
    def decorate(func):
        watches.append({ 'pattern': pattern, 'channel': channel, 'callback': func })
        return func
    return decorate

def handle(iev, f, channel):
    line = f.readline()
    while len(line) > 0:
        match = re.match('(\d{4}-\d\d-\d\d \d\d:\d\d) <([^>]+)> (.*)', line)
        if match is not None:
            when, user, message = match.groups()
            when = time.strptime(when, '%Y-%m-%d %H:%M')
            e = Event(when, user, message, channel)
            for watch in watches:
                match = re.match(watch['pattern']+'$', message)
                if match and re.match(watch['channel']+'$', channel):
                    watch['callback'](e, *match.groups())
        line = f.readline()

def run(path, channels):
    global ii_path
    ii_path = path
    wm = pyinotify.WatchManager()
    for channel in channels:
        with open(os.path.join(path, 'in'), 'a') as f:
            f.write('/j %s\n' % channel)
        out_path = os.path.join(path, channel, 'out')
        open(out_path, 'a').close() # make sure the file exists
        f = open(out_path, 'r')
        f.seek(0, os.SEEK_END)
        def handler(iev):
            handle(iev, f, channel)
        wm.add_watch(out_path, pyinotify.IN_CLOSE_WRITE, handler)

    notifier = pyinotify.ThreadedNotifier(wm, None)
    while True:
        try:
            notifier.run()
        except KeyboardInterrupt:
            return
        except:
            traceback.print_exc()
