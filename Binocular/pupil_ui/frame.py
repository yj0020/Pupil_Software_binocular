class Frame():
    def __init__(self, frame, timestamp, frame_count, phase = None, stimuli_no = None):
        self.frame = frame
        self.timestamp = timestamp
        self.frame_count = frame_count
        self.od = None
        self.od_rect = None
        self.od_circles = None
        self.phase = phase
        self.stimuli_no = stimuli_no   