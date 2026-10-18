from data_structure import Song, CircularDoublyLinkedList
from player import Player, RepeatMode

# ----- Thư viện bài hát có sẵn: {song_id: Song} -----
library = {
    1: Song(1, "Bai 1", "Ca si A", "pop", 200),
    2: Song(2, "Bai 2", "Ca si B", "ballad", 180),
    3: Song(3, "Bai 3", "Ca si C", "rap", 240),
    4: Song(4, "Bai 4", "Ca si D", "pop", 210),
}

playlist = CircularDoublyLinkedList()    
player = Player(playlist)


def show(song):
    if song is None:
        print("⏹  Dừng phát")
    else:
        print(f"▶  Đang phát: {song}")


def ask_int(msg):
    """Hỏi một số nguyên, gõ sai thì trả None thay vì sập."""
    try:
        return int(input(msg))
    except ValueError:
        print("Phải nhập số nha")
        return None


def pick_from_library():
    for song in library.values():
        print(f"  {song.song_id}. {song}")
    return library.get(ask_int("ID bài: "))     # không có thì None


def is_current(song_id):
    song = player.get_current_song()
    return song is not None and song.song_id == song_id


while True:
    print("\n[1] Phát bài  [2] Thêm vào playlist  [3] Xoá khỏi playlist  [4] Đổi chỗ  [5] Xem playlist")
    print("[6] Next  [7] Back  [8] Shuffle  [9] Repeat  [0] Thoát")
    choice = input("Chọn: ").strip()

    if choice == "1":                                   # phát ngay, tự tạo playlist nếu rỗng
        song = pick_from_library()
        if song is None:
            print("Không có bài này")
        else:
            show(player.play_song(song))

    elif choice == "2":
        song = pick_from_library()
        if song is None:
            print("Không có bài này")
        elif playlist.find_node_by_id(song.song_id):
            print("Bài này đã có trong playlist")
        else:
            playlist.append(song)
            player.playlist_changed()
            print("Đã thêm:", song)

    elif choice == "3":
        playlist.display()
        song_id = ask_int("ID bài muốn xoá: ")
        if is_current(song_id):
            print("Không xoá bài đang phát nha, Next qua bài khác trước")
        else:
            removed = playlist.remove_by_id(song_id)
            if removed:
                player.playlist_changed()
                print("Đã xoá:", removed)
            else:
                print("Không có bài này trong playlist")

    elif choice == "4":
        playlist.display()
        id1 = ask_int("ID bài thứ nhất: ")
        id2 = ask_int("ID bài thứ hai: ")
        if is_current(id1) or is_current(id2):
            print("Không đổi chỗ bài đang phát nha")
        elif playlist.swap_songs(id1, id2):
            player.playlist_changed()
            print("Đã đổi chỗ")
        else:
            print("ID không hợp lệ")

    elif choice == "5":
        playlist.display()

    elif choice == "6":
        show(player.next())
    elif choice == "7":
        song = player.back()
        if song is None:
            print("Chưa có bài trước đó")
        else:
            show(song)
    elif choice == "8":
        on = player.toggle_shuffle()
        print("Shuffle:", "BẬT" if on else "TẮT")
    elif choice == "9":
        modes = list(RepeatMode)
        i = modes.index(player.repeat_mode)
        player.set_repeat_mode(modes[(i + 1) % 3])
        print("Repeat:", player.repeat_mode.value)

    elif choice == "0":
        print("Bye 👋")
        break
    else:
        print("Lựa chọn không hợp lệ")