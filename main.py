from data_structure import Song, CircularDoublyLinkedList
from player import Player, RepeatMode


def load_songs(path):
    songs = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line is None:
                    continue
                parts = line.split("|")
                if len(parts) != 5: # nếu thiếu thông tin thì bỏ qua
                    continue
                try:
                    song_id = int(parts[0])
                    duration = int(parts[4])
                except ValueError:
                    continue
                songs[song_id] = Song(song_id, parts[1], parts[2], parts[3], duration)

    except FileNotFoundError:
        print("File rỗng")
    return songs

# ----- Thư viện bài hát có sẵn: {song_id: Song} -----
library = load_songs("songs.txt")
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
    for song in library.values(): # tạo ra một cái list toàn là values của dict
        print(f"  {song.song_id}. {song}")
    return library.get(ask_int("ID bài: "))     # get là truyền vào key, trả ra value, không có thì None


def is_current(song_id):
    song = player.get_current_song()
    return song is not None and song.song_id == song_id


while True:
    print("\n[1] Phát bài  [2] Thêm vào playlist  [3] Xoá khỏi playlist  [4] Đổi chỗ  [5] Xem playlist")
    print("[6] Next  [7] Back  [8] Shuffle  [9] Repeat  [10] Xem lịch sử nghe  [0] Thoát")
    choice = input("Chọn: ").strip()

    if choice == "1":                                   # phát ngay, tự tạo playlist nếu rỗng
        song = pick_from_library()
        if song is None:
            print("Không có bài này")
        else:
            show(player.play_immediately(song))

    elif choice == "2":
        song = pick_from_library()
        if song is None:
            print("Không có bài này")
        elif playlist.find_song_by_id(song.song_id):
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
        elif playlist.swap_song(id1, id2):
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

    elif choice == "10":
        songs = player.get_history()
        if not songs:
            print("Lịch sử nghe đang trống")
        else:
            print("Lịch sử nghe: ")
            for i, song in enumerate(songs, 1):
                print(f"  {i}. {song}")

    elif choice == "0":
        print("Bye 👋")
        break
    else:
        print("Lựa chọn không hợp lệ")