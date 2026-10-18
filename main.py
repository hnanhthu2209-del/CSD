from data_structure import Song, CircularDoublyLinkedList
from player import Player

playlist = CircularDoublyLinkedList()
playlist.append(Song(1, "Bai 1", "Ca si A", "pop", 200))
playlist.append(Song(2, "Bai 2", "Ca si B", "ballad", 180))
playlist.append(Song(3, "Bai 3", "Ca si C", "rap", 240))
player = Player(playlist)

def show(song):
    if song is None:
        print(" ⏹  Dừng phát")
    else:
        print(f"▶  Đang phát: {song}")


while True:
    print("\n[1] Play  [2] Next  [3] Back  [4] Shuffle  [5] Repeat  [0] Thoát")
    choice = input("Chọn: ").strip()

    if choice == "1":
        show(player.play())
    elif choice == "2":
        show(player.next())
    elif choice == "3":
        song = player.back()
        if song is None:
            print("Chưa có bài trước đó")
        else:
            show(song)
    elif choice == "4":
        on = player.toggle_shuffle()
