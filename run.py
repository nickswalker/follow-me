import time
import sys
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from follow_me.event_handler import EventHandler


def main():
    args = sys.argv[1:]
    observer = Observer()
    observer.schedule(EventHandler(), path=args[0] if args else '.')
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == '__main__':
    main()