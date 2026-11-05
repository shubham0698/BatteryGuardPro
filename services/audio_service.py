import winsound
import threading
import time

class AudioService:
    def __init__(self):
        self.is_playing = False
        self.thread = None

    def play_alarm(self, sound_type='digital', volume=80):
        self.stop_alarm()
        self.is_playing = True
        self.thread = threading.Thread(target=self._alarm_loop, args=(sound_type,), daemon=True)
        self.thread.start()

    def _alarm_loop(self, sound_type):
        while self.is_playing:
            try:
                if sound_type == 'siren':
                    for freq in range(500, 1200, 100):
                        if not self.is_playing: break
                        winsound.Beep(freq, 40)
                    for freq in range(1200, 500, -100):
                        if not self.is_playing: break
                        winsound.Beep(freq, 40)
                elif sound_type == 'chime':
                    winsound.Beep(523, 150) # C5
                    winsound.Beep(659, 150) # E5
                    winsound.Beep(784, 250) # G5
                    time.sleep(0.8)
                elif sound_type == 'pulse':
                    winsound.Beep(850, 100)
                    time.sleep(0.1)
                    winsound.Beep(850, 100)
                    time.sleep(0.5)
                else: # 'digital'
                    winsound.Beep(950, 120)
                    winsound.Beep(1250, 160)
                    time.sleep(0.6)
            except Exception:
                time.sleep(0.5)

    def stop_alarm(self):
        self.is_playing = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)
