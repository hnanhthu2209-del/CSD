class Song:
    def __init__(self, song_id, name, artist, genre, duaration):
        self.song_id = song_id
        self.name = name
        self.artist = artist
        self.genre = genre
        self.duaration = duaration

    def __str__(self):
        return f"{self.name} - {self.artist} ({self.duaration})"

class SongNode:
    def __init__(self, song):
        self.data = song
        self.next = None
        self.prev = None

class CircularDoublyLinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def append(self, song):
        new_node = SongNode(song)
        if self.size == 0:
            self.head = new_node
            new_node.next = new_node
            new_node.prev = new_node
            self.size += 1
            return True

        self.head.prev.next = new_node
        new_node.prev = self.head.prev
        new_node.next = self.head
        self.head.prev = new_node
        self.size += 1
        return True

    def append_at_position(self, song, pos):
        new_node = SongNode(song)
        if self.size == 0:
            self.head = new_node
            new_node.next = new_node
            new_node.prev = new_node
            self.size += 1
            return True

        if pos < 0 or pos > self.size:
            return False
        elif pos == 0:
            tail = self.head.prev
            new_node.next = self.head
            new_node.prev = tail
            tail.next = new_node
            self.head.prev = new_node
            self.head = new_node
            self.size += 1
            return True
   
        current = self.head
        for _ in range(pos):
            current = current.next
        current.prev.next = new_node
        new_node.prev = current.prev
        new_node.next = current
        current.prev = new_node
        self.size += 1
        return True

    def remove_by_id(self, id):
        if self.size == 0:
            return False

        elif self.size == 1:
            if self.head.data.song_id != id: 
                return False
            removed = self.head
            self.head = None
            self.size -= 1
            return removed.data

        if self.head.data.song_id == id:
            tail = self.head.prev
            removed = self.head
            tail.next = self.head.next
            self.head = self.head.next
            self.head.prev = tail
            self.size -= 1
            return removed.data

        current = self.head.next
        for _ in range(self.size - 1):
            if current.data.song_id == id:
                current.prev.next = current.next
                current.next.prev = current.prev
                self.size -= 1
                return current.data
            current = current.next
        return False

    def find_song_by_id(self, id):
        current = self.head
        for _ in range(self.size):
            if current.data.song_id == id:
                return current
            current = current.next
        return None

    def swap_song(self, id1, id2):
        if id1 == id2:
            return False
        node1 = self.find_song_by_id(id1)
        node2 = self.find_song_by_id(id2)
        if node1 is None or node2 is None:
            return False
        node1.data, node2.data = node2.data, node1.data
        return True
        
    def find_song_by_name(self, keyword):
        if keyword is None:
            return []
        keyword = keyword.strip().lower()
        if keyword == "":
            return []

        current = self.head
        result = []
        for _ in range(self.size):
            check = current.data.name.lower()
            if keyword in check:
                result.append(current.data)
            current = current.next
        return result

    def find_song_by_artist(self, artist_name):
        if artist_name is None:
            return []
        artist_name = artist_name.strip().lower()
        if artist_name == "":
            return []

        current = self.head
        result = []
        for _ in range(self.size):
            artist_check = current.data.artist.lower()
            if artist_name in artist_check:
                result.append(current.data)
            current = current.next
        return result

    def total_duaration(self):
        current = self.head
        tong = 0
        for _ in range(self.size):
            tong += current.data.duaration
            current = current.next
        return tong

    def to_list(self):
        result = []
        current = self.head
        for _ in range(self.size):
            result.append(current.data)
            current = current.next
        return result

    def to_list_reverse(self):
        if self.size == 0:
            return []
        result = []
        current = self.head.prev
        for _ in range(self.size):
            result.append(current.data)
            current = current.prev
        return result

    def display(self):
        if self.size == 0:
            print("Empty Playlist")
            return
        for i, song in enumerate(self.to_list(), start=1):
            print(f"{i}. {song}")

class HistoryStack:
    def __init__(self, capacity=20):
        self.capacity = capacity
        self.size = 0
        self.elements = []

    def _is_full(self):
        return self.size == self.capacity

    def _is_empty(self):
        return self.size == 0

    def push(self, song):
        if self._is_full():
            self.elements.pop(0)
        else:
            self.size += 1
        self.elements.append(song)
        return True

    def pop(self):
        if self._is_empty():
            return False
        result = self.elements[self.size - 1]
        self.elements.pop()
        self.size -= 1
        return result

    def peek(self):
        if self._is_empty():
            return False
        return self.elements[self.size - 1]

    def to_list(self):
        return self.elements[::-1]

    def clear(self):
        self.elements = []
        self.size = 0


        
        

        
    

    




