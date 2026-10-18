from data_structure import HistoryStack
from algorithms import shuffle

class Player:
    def __init__(self, playlist):
        self.playlist = playlist
        self.current = None
        self.history = HistoryStack()
        self.repeat_mode = "off"
        self.shuffle_on = False
        self.shuffle_order = []
        self.shuffle_index = 0

    def _get_node(self):
        nodes = []
        current = self.playlist.head
        for _ in range(self.playlist.size): # play list is linked list
            nodes.append(current)
            current = current.next
        return nodes

    def _start_shuffle(self): # only for shuffle and id update
        self.shuffle_order = shuffle(self._get_node())
        self.shuffle_index = 0

    def toggle_shuffle(self):
        self.shuffle_on = not self.shuffle_on
        if self.shuffle_on and self.playlist.size > 0:
            self._start_shuffle()
            self.current = self.shuffle_order[0]
        return self.shuffle_on

    def _next_shuffle(self):
        self.shuffle_index += 1
        if self.shuffle_index >= len(self.shuffle_order):
            if self.repeat_mode == "off": # trường hợp này shuffle bật và repeat tắt
                self.current = None
                return None
            self._start_shuffle()

        self.current = self.shuffle_order[self.shuffle_index]
        return self.current.data

    def play(self):
        if self.playlist.size == 0:
            return None
        if self.current is None:
            if self.shuffle_on: # boolean not string
                self._start_shuffle()
                self.current = self.shuffle_order[0]
            else:
                self.current = self.playlist.head
        return self.current.data

    def next(self):
        if self.current is None:
            return self.play()
        self.history.push(self.current)
        if self.repeat_mode == "one":
            return self.current.data
        if self.shuffle_on:
            return self._next_shuffle()
        if self.repeat_mode == "off" and self.current.next == self.playlist.head:
            self.current = None
            return None
        self.current = self.current.next
        return self.current.data

    def back(self):
        node = self.history.pop()
        if not node:
            return None
        self.current = node
        if self.shuffle_on and self.shuffle_index > 0:
            self.shuffle_index -= 1
        return node.data