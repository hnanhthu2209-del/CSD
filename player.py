from data_structure import HistoryStack
from algorithms import shuffle
from enum import Enum

class RepeatMode(Enum):
    OFF = "off"
    ALL = "all"
    ONE = "one"

class Player:
    def __init__(self, playlist):
        self.playlist = playlist
        self.current = None
        self.history = HistoryStack()
        self.repeat_mode = RepeatMode.OFF
        self.shuffle_on = False
        self.shuffle_order = []
        self.shuffle_index = 0
        self.is_playing = False

    def _get_node(self):
        nodes = []
        current = self.playlist.head
        for _ in range(self.playlist.size): # playlist is linked list
            nodes.append(current)
            current = current.next
        return nodes

    def get_current_song(self):
        return None if self.current is None else self.current.data

    def get_history(self):
        songs = [node.data for node in self.history.to_list()]
        if self.current is not None:
            songs.insert(0, self.current.data)
        return songs

    def _start_shuffle(self): # only for shuffle and id update
        self.shuffle_order = shuffle(self._get_node())
        self.shuffle_index = 0

    def _reshuffle_keep_current(self):
        # shuffle nhưng giữ lại bài đầu
        self._start_shuffle()
        if self.current is None:
            self.current = self.shuffle_order[0]
        else:
            self.shuffle_order.remove(self.current) # remove node có cùng giá trị với self.current
            self.shuffle_order.insert(0, self.current)
    
    def toggle_shuffle(self):
        self.shuffle_on = not self.shuffle_on
        if self.shuffle_on and self.playlist.size > 0:
            self._reshuffle_keep_current()
        return self.shuffle_on
    
    def _next_shuffle(self):
        self.shuffle_index += 1
        if self.shuffle_index >= len(self.shuffle_order):
            if self.repeat_mode == RepeatMode.OFF: # trường hợp này shuffle bật và repeat tắt
                self.current = None
                return None
            self._start_shuffle()

        self.current = self.shuffle_order[self.shuffle_index]
        return self.current.data

    def set_repeat_mode(self, mode):
        if not isinstance(mode, RepeatMode):
            return False
        self.repeat_mode = mode
        return True

    def play_immediately(self, song):
        node = self.playlist.find_song_by_id(song.song_id)
        if node is None:
            self.playlist.append(song)
            node = self.playlist.head.prev
        if self.current is not None:
            self.history.push(self.current)
        self.current = node
        self.is_playing = True
        if self.shuffle_on:
            self._reshuffle_keep_current()
        return song

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

    def playlist_changed(self):
        self.history.clear()
        if self.shuffle_on and self.playlist.size > 0:
                self._reshuffle_keep_current()

    def next(self):
        if self.current is None:
            return self.play()
        self.history.push(self.current)
        if self.repeat_mode == RepeatMode.ONE:
            return self.current.data
        if self.shuffle_on:
            return self._next_shuffle()
        if self.repeat_mode == RepeatMode.OFF and self.current.next == self.playlist.head:
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