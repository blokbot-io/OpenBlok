''' OpenBlok | bloks | utils | stats.py '''


class Stats:
    ''' Running statistics '''

    def __init__(self):
        self.frame_time_log = []

    def add_frame_time(self, frame_time):
        '''
        Stores time stamps for 1 second of frames
        '''
        if self.frame_time_log:
            time_difference = frame_time - self.frame_time_log[0]

            if time_difference > 1:
                self.frame_time_log.pop(0)

        self.frame_time_log.append(frame_time)

    def fps(self):
        '''
        Calculate frames per second
        '''
        return len(self.frame_time_log)
