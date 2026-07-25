from solomon_os.kernel import SolomonModule
import threading
import time

class SchedulingModule(SolomonModule):
    def start(self):
        super().start()
        # Start a background tick thread
        self.tick_thread = threading.Thread(target=self._tick_loop, daemon=True)
        self.tick_thread.start()

    def _tick_loop(self):
        while self.state == "RUNNING":
            if self.kernel:
                self.kernel.publish('TICK_1S', self.name, {"timestamp": time.time()})
            time.sleep(1)
