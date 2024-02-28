import watchdog.events
import watchdog.observers
import time
from pathlib import Path

SRC_PATH = Path('D:/portable/Civilization III/Conquests/Saves/Auto')
TGT_PATH = Path('D:/portable/Civilization III/Conquests/Saves')
LOG_PATH = Path('D:/portable/Civilization III/Conquests/civ3_auto_saves_backup_log.txt')

def now():
    import pendulum
    return pendulum.now('UTC').format('YYYY-MM-DD_HH-mm-ss_SSS')

def wait_file(p, time_limit=30):
  import os
  init_size = -1
  for i in range(time_limit):
    current_size = os.path.getsize(p)
    if current_size == init_size:
      break 
    else:
      init_size = os.path.getsize(p)
      time.sleep(1)

class Handler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self, tgt_path, logfile=None):
        watchdog.events.PatternMatchingEventHandler.__init__(self, patterns=['*.SAV'], ignore_directories=True, case_sensitive=False)
        self.logfile = logfile
        self.tgt_path = tgt_path

    def log(self, s):
        if self.logfile is None:
            print(s)
        else:
            with open(self.logfile, 'a', encoding='utf8') as f:
                f.write(s + '\n')
 
    def on_created(self, event):
        self.log(now() + " Watchdog received created event - % s." % event.src_path)
        # https://stackoverflow.com/a/66066297/19383164
        wait_file(event.src_path)
        path_from = Path(event.src_path)
        path_to = Path(self.tgt_path, now() + '__' + path_from.name)
        path_to.write_bytes(path_from.read_bytes())
 
    def on_modified(self, event):
        self.log(now() + " Watchdog received modified event - % s." % event.src_path)

    def on_deleted(self, event):
        self.log(now() + " Watchdog received deleted event - % s." % event.src_path)

    def on_moved(self, event):
        self.log(now() + " Watchdog received moved event - % s." % event.src_path)
 
 
if __name__ == '__main__':
    event_handler = Handler(TGT_PATH, LOG_PATH)
    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path=SRC_PATH, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
