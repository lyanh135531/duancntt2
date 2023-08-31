import matplotlib.pyplot as plt

class Plotter:
    def __init__(self, rank, TFWID_time, TFWIT_time, TFWIN_time, TFWINPLUS_time, TFWID_memories_used, TFWIT_memories_used, TFWIN_memories_used, TFWINPLUS_memories_used):
        self.rank = rank
        self.TFWID_time = TFWID_time
        self.TFWIT_time = TFWIT_time
        self.TFWIN_time = TFWIN_time
        self.TFWINPLUS_time = TFWINPLUS_time
        self.TFWID_memories_used = TFWID_memories_used
        self.TFWIT_memories_used = TFWIT_memories_used
        self.TFWIN_memories_used = TFWIN_memories_used
        self.TFWINPLUS_memories_used = TFWINPLUS_memories_used

    def draw_time_plot(self):
        # Draw time plot
        plt.plot(self.rank, self.TFWID_time, marker='s', label='TFWID')
        plt.plot(self.rank, self.TFWIT_time, marker='s', label='TFWIT')
        plt.plot(self.rank, self.TFWIN_time, marker='s', label='TFWIN')
        plt.plot(self.rank, self.TFWINPLUS_time, marker='s', label='TFWINPLUS')

        # Name y axis and x axis
        plt.xlabel('Rank')
        plt.ylabel('Time used')
        plt.title('Thời gian')
        plt.legend()
        # Save image
        plt.savefig('time.png')

        # Show chart
        #plt.show()

    def draw_memory_plot(self):
        # Draw memories used
        plt.plot(self.rank, self.TFWID_memories_used, marker='s', label='TFWID')
        plt.plot(self.rank, self.TFWIT_memories_used, marker='s', label='TFWIT')
        plt.plot(self.rank, self.TFWIN_memories_used, marker='s', label='TFWIN')
        plt.plot(self.rank, self.TFWINPLUS_memories_used, marker='s', label='TFWINPLUS')

        # Name y axis and x axis
        plt.xlabel('Rank')
        plt.ylabel('Memory used')
        plt.title('Bộ nhớ')
        plt.legend()
        # Save image
        plt.savefig('memory.png')

        # Show chart
        #plt.show()