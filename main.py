import io
import os
import sys
import textwrap
 
from data_structure import Song, CircularDoublyLinkedList
from player import Player, RepeatMode
 
# Đảm bảo console Windows hiển thị đúng ký tự tiếng Việt và khung viền Unicode
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
 
SONGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "songs.txt")
IS_TTY = sys.stdin.isatty() and sys.stdout.isatty()
 
LEFT_W = 64
RIGHT_W = 68
GAP = "   "
TOTAL_W = LEFT_W + len(GAP) + RIGHT_W  # 135 ký tự (Gọn gàng, vừa tầm mắt)
 
 
def _init_wide_console():
    """Kích hoạt ANSI và tự động đặt kích thước cửa sổ Console vừa vặn."""
    if not IS_TTY:
        return
    if os.name == "nt":
        os.system("")
    try:
        sys.stdout.write("\x1b[8;38;140t")
        sys.stdout.flush()
    except Exception:
        pass
 
 
def load_songs(path):
    """Đọc songs.txt (định dạng: id|name|artist|genre|duration) thành {song_id: Song}."""
    songs = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) != 5:
                    continue
                try:
                    song_id = int(parts[0])
                    duration = int(parts[4])
                except ValueError:
                    continue
                songs[song_id] = Song(song_id, parts[1], parts[2], parts[3], duration)
    except FileNotFoundError:
        print(f"Không tìm thấy file {path}")
    return songs
 
 
library = load_songs(SONGS_FILE)
playlist = CircularDoublyLinkedList()
player = Player(playlist)
 
 
def _clear_screen():
    if IS_TTY:
        os.system("cls" if os.name == "nt" else "clear")
 
 
def _fmt_time(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d} ({seconds}s)"
 
 
def _box_line(text, width):
    inner = width - 4
    clipped = text[:inner]
    return f"│ {clipped:<{inner}} │"
 
 
def _box_top(title, width):
    inner = width - 2
    t = f" {title} "
    pad_left = (inner - len(t)) // 2
    pad_right = inner - len(t) - pad_left
    return "┌" + ("─" * pad_left) + t + ("─" * pad_right) + "┐"
 
 
def _box_bottom(width):
    return "└" + ("─" * (width - 2)) + "┘"
 
 
def show(song):
    if song is None:
        print("■ TRẠNG THÁI: Đã dừng phát (Stopped)")
    else:
        info = f"[ID:{song.song_id}] {song.name} - {song.artist} ({song.genre}, {_fmt_time(song.duration)})"
        print(f"► Đang phát: {info}")
 
 
def ask_int(msg):
    """Hỏi một số nguyên, gõ sai thì trả None thay vì sập."""
    raw = input(msg).strip()
    try:
        return int(raw), raw
    except ValueError:
        print("Phải nhập số nha")
        return None, raw
 
 
def render_library_table():
    """Hiển thị Thư viện bài hát dàn ngang 2 cột gọn gàng."""
    songs_list = list(library.values())
    half = (len(songs_list) + 1) // 2
    left_songs = songs_list[:half]
    right_songs = songs_list[half:]
 
    lines = []
    sep_line = "╟────┼─────────────────────────┼────────────────┼────────┼────────╫────┼─────────────────────────┼────────────────┼────────┼────────╢"
    title = f" THƯ VIỆN BÀI HÁT (songs.txt — {len(songs_list)} BÀI) "
    lines.append("╔" + title.center(len(sep_line) - 2, "═") + "╗")
    hdr_col = f"{'ID':>2} │ {'Tên bài hát':<23} │ {'Nghệ sĩ':<14} │ {'Loại':<6} │ {'Giây':<6}"
    lines.append(f"║ {hdr_col} ║ {hdr_col} ║")
    lines.append(sep_line)
 
    for i in range(half):
        ls = left_songs[i]
        l_mark = "√" if playlist.find_song_by_id(ls.song_id) else " "
        l_str = f"{ls.song_id:>2} │ {ls.name:<23.23} │ {ls.artist:<14.14} │ {ls.genre:<6.6} │ {ls.duration:>4}s{l_mark}"
 
        if i < len(right_songs):
            rs = right_songs[i]
            r_mark = "√" if playlist.find_song_by_id(rs.song_id) else " "
            r_str = f"{rs.song_id:>2} │ {rs.name:<23.23} │ {rs.artist:<14.14} │ {rs.genre:<6.6} │ {rs.duration:>4}s{r_mark}"
        else:
            r_str = " " * len(l_str)
 
        lines.append(f"║ {l_str} ║ {r_str} ║")
 
    lines.append("╚════╧═════════════════════════╧════════════════╧════════╧════════╩════╧═════════════════════════╧════════════════╧════════╧════════╝")
    return "\n".join(lines)
 
 
def pick_from_library():
    print("\n" + render_library_table())
    id_range = f"{min(library)}-{max(library)}" if library else "thư viện trống"
    sid, raw = ask_int(f"  ► Nhập ID bài hát ({id_range}): ")
    return library.get(sid), raw
 
 
def is_current(song_id):
    song = player.get_current_song()
    return song is not None and song.song_id == song_id
 
 
def _render_playlist(reverse=False):
    """Hiển thị bảng Playlist theo chiều thuận (to_list) hoặc chiều ngược (to_list_reverse)."""
    if playlist.size == 0:
        playlist.display()  # in "Empty Playlist"
        return
    current_song = player.get_current_song()
    songs = playlist.to_list_reverse() if reverse else playlist.to_list()
    mode_title = "DUYỆT NGƯỢC (to_list_reverse: Cuối → Đầu)" if reverse else "DUYỆT THUẬN (to_list: Đầu → Cuối)"
    print(f"╔══════════════════════════════════════ BẢNG PLAYLIST — {mode_title:<43} ══════════════════════════════════════╗")
    print(f"║ {'STT':>4} │ {'ID':>4} │ {'Tên bài hát':<38} │ {'Nghệ sĩ':<28} │ {'Thể loại':<12} │ {'Thời lượng':<22} ║")
    print("╟──────┼──────┼────────────────────────────────────────┼──────────────────────────────┼──────────────┼────────────────────────╢")
    for i, song in enumerate(songs, start=1):
        marker = "►" if (current_song and current_song.song_id == song.song_id) else " "
        dur_str = _fmt_time(song.duration)
        print(
            f"║ {marker}{i:>3} │ {song.song_id:>4} │ {song.name:<38.38} │ {song.artist:<28.28} │ {song.genre:<12.12} │ {dur_str:<22} ║"
        )
    print("╟──────┴──────┴────────────────────────────────────────┴──────────────────────────────┴──────────────┴────────────────────────╢")
    total_sec = playlist.total_duration()
    summary = f"Tổng số bài: {playlist.size} bài   │   Tổng thời lượng (total_duration): {_fmt_time(total_sec)}"
    print(f"║ {summary:<123} ║")
    print("╚═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")
 
 
def _build_cdll_lines(max_width):
    if playlist.size == 0:
        return [
            "  (Đang trống — head = None, size = 0 bài)",
            "",
        ]
    curr = player.current
    nodes_str = []
    for s in playlist.to_list():
        short_name = s.name if len(s.name) <= 10 else s.name[:8] + ".."
        if curr and curr.data.song_id == s.song_id:
            nodes_str.append(f"«►{s.song_id}:{short_name}»")
        else:
            nodes_str.append(f"[{s.song_id}:{short_name}]")
 
    row1 = "  ↔ "
    row2_items = []
    for idx, token in enumerate(nodes_str):
        sep = " ↔ " if idx > 0 else ""
        if not row2_items and len(row1) + len(sep) + len(token) + 3 <= max_width:
            row1 += sep + token
        else:
            row2_items.append(token)
 
    if not row2_items:
        return [row1 + " ↔", ""]
    row1 += " ↔"
    row2 = "    " + " ↔ ".join(row2_items) + " ↔"
    return [row1[:max_width], row2[:max_width]]
 
 
def _build_shuffle_line(max_width):
    if not player.shuffle_on:
        return "  (Đang TẮT — Phát tuần tự theo vòng CDLL)"
    if playlist.size == 0 or not player.shuffle_order:
        return "  (Shuffle: BẬT — Playlist đang trống)"
    tokens = []
    for idx, node in enumerate(player.shuffle_order):
        s = node.data
        short_name = s.name if len(s.name) <= 8 else s.name[:7] + "."
        is_active = (player.current is not None and idx == player.shuffle_index and player.current is node)
        if is_active:
            tokens.append(f"«►{s.song_id}:{short_name}»")
        else:
            tokens.append(f"[{s.song_id}:{short_name}]")
    line = "  ~ " + " → ".join(tokens)
    return line[:max_width]
 
 
def _build_dashboard_columns(cmd_trace="", log_text=""):
    """Dựng 2 cột song song cao đúng 18 dòng, gọn gàng, không chi tiết thừa."""
    curr = player.get_current_song()
    shuf_str = "BẬT (Fisher-Yates)" if player.shuffle_on else "TẮT (Tuần tự)"
    rep_map = {
        RepeatMode.OFF: "OFF (Không lặp)",
        RepeatMode.ALL: "ALL (Lặp vòng)",
        RepeatMode.ONE: "ONE (Lặp 1 bài)",
    }
    rep_str = rep_map.get(player.repeat_mode, player.repeat_mode.value.upper())
 
    # ----- CỘT TRÁI (18 DÒNG, RỘNG 64 KÝ TỰ) -----
    left_lines = []
    # Khối 1: Trình phát nhạc (5 dòng)
    left_lines.append(_box_top("1. TRÌNH PHÁT NHẠC (PLAYER)", LEFT_W))
    if curr:
        left_lines.append(_box_line(f"► ĐANG PHÁT: [ID:{curr.song_id}] {curr.name} - {curr.artist}", LEFT_W))
        left_lines.append(_box_line(f"• Thông tin: Thể loại: {curr.genre.upper()} │ Thời lượng: {_fmt_time(curr.duration)}", LEFT_W))
    else:
        left_lines.append(_box_line(f"■ TRẠNG THÁI: DỪNG PHÁT / CHƯA CHỌN BÀI (Playlist: {playlist.size} bài)", LEFT_W))
        left_lines.append(_box_line("• Thông tin: Thể loại: --- │ Thời lượng: 00:00 (0s)", LEFT_W))
    left_lines.append(_box_line(f"• Chế độ: Shuffle: {shuf_str} │ Repeat: {rep_str}", LEFT_W))
    left_lines.append(_box_bottom(LEFT_W))
 
    # Dòng trống ngăn cách (1 dòng)
    left_lines.append(" " * LEFT_W)
 
    # Khối 3: Bảng điều khiển Menu đầy đủ 16 chức năng (12 dòng)
    left_lines.append(_box_top("3. BẢNG ĐIỀU KHIỂN (MENU CHỨC NĂNG)", LEFT_W))
    left_lines.append(_box_line("[1] Phát ngay bài hát       [9]  Xem Playlist ngược (prev)", LEFT_W))
    left_lines.append(_box_line("[2] Thêm bài vào cuối       [10] Next (Qua bài tiếp theo)", LEFT_W))
    left_lines.append(_box_line("[3] Chèn bài vào vị trí pos [11] Back (Lùi bài từ Stack)", LEFT_W))
    left_lines.append(_box_line("[4] Xoá bài theo ID         [12] Shuffle (Bật/Tắt trộn)", LEFT_W))
    left_lines.append(_box_line("[5] Đổi chỗ 2 bài hát       [13] Repeat (OFF → ALL → ONE)", LEFT_W))
    left_lines.append(_box_line("[6] Tìm bài theo Tên        [14] Xem Lịch sử nghe (Stack)", LEFT_W))
    left_lines.append(_box_line("[7] Tìm bài theo Nghệ sĩ    [15] Nạp nhanh dữ liệu mẫu", LEFT_W))
    left_lines.append(_box_line(f"[8] Xem Playlist & Tổng giờ [16] Xem Thư viện ({len(library)} bài)", LEFT_W))
    left_lines.append(_box_line("────────────────────────────────────────────────────────────", LEFT_W))
    left_lines.append(_box_line("[0] Thoát chương trình      • Nhập số 0 - 16 rồi nhấn Enter", LEFT_W))
    left_lines.append(_box_bottom(LEFT_W))
 
    # ----- CỘT PHẢI (18 DÒNG, RỘNG 68 KÝ TỰ) -----
    right_lines = []
    # Khối 2: Cấu trúc dữ liệu Live (10 dòng)
    right_lines.append(_box_top("2. CẤU TRÚC DỮ LIỆU (CDLL & STACK LIVE)", RIGHT_W))
    right_lines.append(_box_line(f"• Chuỗi vòng CDLL ({playlist.size} bài │ Tổng giờ: {_fmt_time(playlist.total_duration())}):", RIGHT_W))
    cdll_r1, cdll_r2 = _build_cdll_lines(RIGHT_W - 4)
    right_lines.append(_box_line(cdll_r1, RIGHT_W))
    right_lines.append(_box_line(cdll_r2, RIGHT_W))
 
    if player.current:
        p_node = player.current.prev.data
        c_node = player.current.data
        n_node = player.current.next.data
        ptr_line = (
            f"  prev=[{p_node.song_id}:{p_node.name[:8]}] ◄─ "
            f"curr=«{c_node.song_id}:{c_node.name[:8]}» ─► "
            f"next=[{n_node.song_id}:{n_node.name[:8]}]"
        )
    else:
        ptr_line = "  prev = None  ◄──  current = None  ──►  next = None"
    right_lines.append(_box_line("• Con trỏ Node (Doubly Linked Pointers):", RIGHT_W))
    right_lines.append(_box_line(ptr_line, RIGHT_W))
    right_lines.append(_box_line("• Hàng đợi trộn Fisher-Yates (Shuffle Queue):", RIGHT_W))
    right_lines.append(_box_line(_build_shuffle_line(RIGHT_W - 4), RIGHT_W))
 
    if player.history.size == 0:
        hist_line = "• HistoryStack (LIFO): Trống (0/20 bài)"
    else:
        top_items = [f"[{n.data.song_id}:{n.data.name[:9]}]" for n in reversed(player.history.elements[-3:])]
        hist_line = f"• HistoryStack ({player.history.size}/20): Đỉnh → " + " → ".join(top_items)
    right_lines.append(_box_line(hist_line, RIGHT_W))
    right_lines.append(_box_bottom(RIGHT_W))
 
    # Dòng trống ngăn cách (1 dòng)
    right_lines.append(" " * RIGHT_W)
 
    # Khối 4: Bằng chứng Thao tác & Kết quả (7 dòng)
    right_lines.append(_box_top("4. THAO TÁC VỪA BẤM & KẾT QUẢ PHẢN HỒI", RIGHT_W))
    trace_str = cmd_trace if cmd_trace else "(Chưa bấm phím — Màn hình khởi tạo)"
    right_lines.append(_box_line(f"► Thao tác: {trace_str}", RIGHT_W))
 
    wrapped_log = []
    if log_text.strip():
        for raw_line in log_text.strip().splitlines():
            clean = raw_line.strip()
            if not clean or clean.startswith(("╔", "╟", "╚", "║")):
                continue
            for wline in textwrap.wrap(clean, width=RIGHT_W - 6) or [""]:
                wrapped_log.append("  " + wline)
    else:
        wrapped_log = ["  Sẵn sàng nhận lệnh từ bàn phím (0 - 16)."]
 
    for i in range(4):
        line_val = wrapped_log[i] if i < len(wrapped_log) else ""
        right_lines.append(_box_line(line_val, RIGHT_W))
 
    right_lines.append(_box_bottom(RIGHT_W))
 
    return left_lines, right_lines
 
 
def _render_dashboard(cmd_trace="", log_text="", extra_bottom_table=""):
    title = "♫  MUSIC STREAMING PLAYLIST MANAGER — CSD203 (NHÓM 4)  ♫"
    print("  ╔" + ("═" * (TOTAL_W - 2)) + "╗")
    print("  ║" + f"{title:^{TOTAL_W - 2}}" + "║")
    print("  ╚" + ("═" * (TOTAL_W - 2)) + "╝")
 
    left_lines, right_lines = _build_dashboard_columns(cmd_trace, log_text)
    for l_row, r_row in zip(left_lines, right_lines):
        print(f"  {l_row}{GAP}{r_row}")
 
    if extra_bottom_table.strip():
        print()
        for line in extra_bottom_table.rstrip().splitlines():
            print(f"  {line}")
 
 
if __name__ == "__main__":
    _init_wide_console()
    last_cmd = ""
    last_output = ""
    extra_table = ""
 
    while True:
        _clear_screen()
        _render_dashboard(last_cmd, last_output, extra_table)
        extra_table = ""
 
        choice = input("\n  ► Chọn chức năng (0-16): ").strip()
 
        if choice == "1":  # Phát ngay bài hát (play_immediately)
            song, raw_id = pick_from_library()
            last_cmd = f"Phím [1] Phát ngay → Nhập ID = '{raw_id}'"
            with io.StringIO() as tmp:
                old_stdout = sys.stdout
                if IS_TTY:
                    sys.stdout = tmp
                try:
                    if song is None:
                        print("Không có bài này")
                    else:
                        played = player.play_immediately(song)
                        show(played)
                finally:
                    sys.stdout = old_stdout
                last_output = tmp.getvalue()
 
        elif choice == "2":  # Thêm bài vào cuối (append)
            song, raw_id = pick_from_library()
            last_cmd = f"Phím [2] Thêm vào cuối → Nhập ID = '{raw_id}'"
            with io.StringIO() as tmp:
                old_stdout = sys.stdout
                if IS_TTY:
                    sys.stdout = tmp
                try:
                    if song is None:
                        print("Không có bài này")
                    elif playlist.find_song_by_id(song.song_id):
                        print("Bài này đã có trong playlist")
                    else:
                        playlist.append(song)
                        player.playlist_changed()
                        print(f"Đã thêm vào cuối Playlist: [ID:{song.song_id}] {song}")
                finally:
                    sys.stdout = old_stdout
                last_output = tmp.getvalue()
 
        elif choice == "3":  # Chèn bài vào vị trí pos (append_at_position)
            song, raw_id = pick_from_library()
            pos, raw_pos = ask_int(f"  ► Nhập vị trí pos muốn chèn (0 đến {playlist.size}): ")
            last_cmd = f"Phím [3] Chèn vị trí → ID = '{raw_id}', pos = '{raw_pos}'"
            with io.StringIO() as tmp:
                old_stdout = sys.stdout
                if IS_TTY:
                    sys.stdout = tmp
                try:
                    if song is None:
                        print("Không có bài này")
                    elif playlist.find_song_by_id(song.song_id):
                        print("Bài này đã có trong playlist")
                    elif pos is None or not playlist.append_at_position(song, pos):
                        print(f"Vị trí chèn pos={raw_pos} không hợp lệ (hợp lệ: 0..{playlist.size})")
                    else:
                        player.playlist_changed()
                        print(f"Đã chèn [ID:{song.song_id}] {song.name} vào vị trí pos={pos}")
                finally:
                    sys.stdout = old_stdout
                last_output = tmp.getvalue()
 
        elif choice == "4":  # Xoá bài theo ID (remove_by_id)
            song_id, raw_id = ask_int("  ► ID bài muốn xoá: ")
            last_cmd = f"Phím [4] Xoá bài theo ID → Nhập ID = '{raw_id}'"
            with io.StringIO() as tmp:
                old_stdout = sys.stdout
                if IS_TTY:
                    sys.stdout = tmp
                try:
                    if playlist.size == 0:
                        playlist.display()
                        print("Không có bài này trong playlist")
                    elif is_current(song_id):
                        print("Không xoá bài đang phát nha, Next qua bài khác trước")
                    else:
                        removed = playlist.remove_by_id(song_id)
                        if removed:
                            player.playlist_changed()
                            print(f"Đã xoá khỏi Playlist: [ID:{removed.song_id}] {removed}")
                        else:
                            print("Không có bài này trong playlist")
                finally:
                    sys.stdout = old_stdout
                last_output = tmp.getvalue()
 
        elif choice == "5":  # Đổi chỗ 2 bài hát (swap_song)
            id1, raw1 = ask_int("  ► ID bài thứ nhất: ")
            id2, raw2 = ask_int("  ► ID bài thứ hai: ")
            last_cmd = f"Phím [5] Đổi chỗ 2 bài → ID1 = '{raw1}', ID2 = '{raw2}'"
            with io.StringIO() as tmp:
                old_stdout = sys.stdout
                if IS_TTY:
                    sys.stdout = tmp
                try:
                    if is_current(id1) or is_current(id2):
                        print("Không đổi chỗ bài đang phát nha")
                    elif playlist.swap_song(id1, id2):
                        player.playlist_changed()
                        print(f"Đã đổi chỗ thành công bài ID={id1} và ID={id2}")
                    else:
                        print("ID không hợp lệ")
                finally:
                    sys.stdout = old_stdout
                last_output = tmp.getvalue()
 
        elif choice == "6":  # Tìm bài theo Tên (find_song_by_name)
            kw = input("  ► Nhập từ khoá Tên bài hát cần tìm: ").strip()
            last_cmd = f"Phím [6] Tìm theo Tên → Từ khoá = '{kw}'"
            with io.StringIO() as tmp:
                old_stdout = sys.stdout
                if IS_TTY:
                    sys.stdout = tmp
                try:
                    found = playlist.find_song_by_name(kw)
                    if not found:
                        print(f"Không tìm thấy bài hát nào có tên chứa '{kw}' trong Playlist")
                    else:
                        print(f"Tìm thấy {len(found)} bài theo tên '{kw}':")
                        for s in found:
                            print(f"• [ID:{s.song_id}] {s.name} - {s.artist} ({_fmt_time(s.duration)})")
                finally:
                    sys.stdout = old_stdout
                last_output = tmp.getvalue()
 
        elif choice == "7":  # Tìm bài theo Nghệ sĩ (find_song_by_artist)
            kw = input("  ► Nhập tên Nghệ sĩ cần tìm: ").strip()
            last_cmd = f"Phím [7] Tìm theo Nghệ sĩ → Từ khoá = '{kw}'"
            with io.StringIO() as tmp:
                old_stdout = sys.stdout
                if IS_TTY:
                    sys.stdout = tmp
                try:
                    found = playlist.find_song_by_artist(kw)
                    if not found:
                        print(f"Không tìm thấy bài hát nào của nghệ sĩ '{kw}' trong Playlist")
                    else:
                        print(f"Tìm thấy {len(found)} bài của nghệ sĩ '{kw}':")
                        for s in found:
                            print(f"• [ID:{s.song_id}] {s.name} - {s.artist} ({_fmt_time(s.duration)})")
                finally:
                    sys.stdout = old_stdout
                last_output = tmp.getvalue()
 
        elif choice == "8":  # Xem Playlist chiều thuận & Tổng giờ (to_list, total_duration)
            last_cmd = "Phím [8] Xem Playlist thuận & Tổng giờ"
            with io.StringIO() as tmp:
                old_stdout = sys.stdout
                if IS_TTY:
                    sys.stdout = tmp
                try:
                    _render_playlist(reverse=False)
                finally:
                    sys.stdout = old_stdout
                val = tmp.getvalue()
                if playlist.size == 0:
                    last_output = val
                else:
                    total_sec = playlist.total_duration()
                    last_output = (
                        f"Duyệt thuận (to_list): {playlist.size} bài.\n"
                        f"Tổng thời lượng (total_duration): {_fmt_time(total_sec)}"
                    )
                    extra_table = val
 
        elif choice == "9":  # Xem Playlist duyệt ngược (to_list_reverse)
            last_cmd = "Phím [9] Xem Playlist ngược (to_list_reverse)"
            with io.StringIO() as tmp:
                old_stdout = sys.stdout
                if IS_TTY:
                    sys.stdout = tmp
                try:
                    _render_playlist(reverse=True)
                finally:
                    sys.stdout = old_stdout
                val = tmp.getvalue()
                if playlist.size == 0:
                    last_output = val
                else:
                    rev_ids = [s.song_id for s in playlist.to_list_reverse()]
                    last_output = (
                        f"Duyệt ngược bằng con trỏ prev (to_list_reverse):\n"
                        f"Thứ tự ID từ cuối về đầu: {rev_ids}"
                    )
                    extra_table = val
 
        elif choice == "10":  # Next (chuyển bài tiếp theo)
            last_cmd = "Phím [10] Next — Chuyển sang bài tiếp theo"
            with io.StringIO() as tmp:
                old_stdout = sys.stdout
                if IS_TTY:
                    sys.stdout = tmp
                try:
                    before = player.get_current_song()
                    after = player.next()
                    if before and after:
                        print(f"» Đã chuyển Next: '[ID:{before.song_id}] {before.name}' ──► '[ID:{after.song_id}] {after.name}'")
                    elif after:
                        print(f"► Bắt đầu phát bài đầu tiên: '[ID:{after.song_id}] {after.name}'")
                    elif playlist.size == 0:
                        print("! Playlist đang trống (0 bài)! Không thể chuyển bài.")
                    else:
                        print("■ Đã đi hết bài cuối cùng trong Playlist (Repeat đang là OFF).")
                    show(after)
                finally:
                    sys.stdout = old_stdout
                last_output = tmp.getvalue()
 
        elif choice == "11":  # Back (quay lại bài cũ từ HistoryStack)
            last_cmd = "Phím [11] Back — Quay lại bài từ HistoryStack"
            with io.StringIO() as tmp:
                old_stdout = sys.stdout
                if IS_TTY:
                    sys.stdout = tmp
                try:
                    song = player.back()
                    if song is None:
                        print("Chưa có bài trước đó trong HistoryStack (Stack đang rỗng 0/20)")
                    else:
                        print(f"« Đã lấy từ đỉnh HistoryStack quay về: '[ID:{song.song_id}] {song.name}'")
                        show(song)
                finally:
                    sys.stdout = old_stdout
                last_output = tmp.getvalue()
 
        elif choice == "12":  # Shuffle (bật/tắt trộn bài Fisher-Yates)
            last_cmd = "Phím [12] Shuffle — Bật/Tắt trộn Fisher-Yates"
            with io.StringIO() as tmp:
                old_stdout = sys.stdout
                if IS_TTY:
                    sys.stdout = tmp
                try:
                    on = player.toggle_shuffle()
                    print("Shuffle:", "BẬT" if on else "TẮT")
                    if on:
                        order_names = [f"[ID {n.data.song_id}:{n.data.name}]" for n in player.shuffle_order]
                        print("Thứ tự trộn Fisher-Yates:", " → ".join(order_names) if order_names else "(Playlist trống)")
                finally:
                    sys.stdout = old_stdout
                last_output = tmp.getvalue()
 
        elif choice == "13":  # Repeat (đổi chế độ lặp OFF -> ALL -> ONE)
            last_cmd = "Phím [13] Repeat — Chuyển chế độ (OFF→ALL→ONE)"
            with io.StringIO() as tmp:
                old_stdout = sys.stdout
                if IS_TTY:
                    sys.stdout = tmp
                try:
                    modes = list(RepeatMode)
                    i = modes.index(player.repeat_mode)
                    player.set_repeat_mode(modes[(i + 1) % len(modes)])
                    print("Repeat:", player.repeat_mode.value)
                finally:
                    sys.stdout = old_stdout
                last_output = tmp.getvalue()
 
        elif choice == "14":  # Xem danh sách Lịch sử nghe (get_history)
            last_cmd = "Phím [14] Xem Lịch sử nghe (HistoryStack)"
            with io.StringIO() as tmp:
                old_stdout = sys.stdout
                if IS_TTY:
                    sys.stdout = tmp
                try:
                    songs = player.get_history()
                    if not songs:
                        print("Lịch sử nghe đang trống")
                    else:
                        stack_ids = [n.data.song_id for n in reversed(player.history.elements)]
                        print(f"Lịch sử nghe: Đang lưu {player.history.size}/20 bài trong Stack.")
                        print(f"Thứ tự ID trong Stack (Mới → Cũ): {stack_ids}")
                finally:
                    sys.stdout = old_stdout
                last_output = tmp.getvalue()
 
        elif choice == "15":  # Công cụ nạp dữ liệu mẫu nhanh trên giao diện
            print(f"\n  Chọn chế độ nạp mẫu: [1] Nạp 5 bài HIT mẫu (ID 5..9)  │  [2] Nạp {len(library)} bài & nghe 25 lượt (Test tràn Stack 20)")
            sub = input("  ► Chọn (1/2): ").strip()
            with io.StringIO() as tmp:
                old_stdout = sys.stdout
                if IS_TTY:
                    sys.stdout = tmp
                try:
                    if not library:
                        last_cmd = "Phím [15] Nạp mẫu"
                        print("Thư viện đang trống (thiếu songs.txt?) nên không nạp mẫu được.")
                    elif sub == "2":
                        last_cmd = f"Phím [15]->[2] Nạp {len(library)} bài & chạy 25 lượt Next"
                        playlist.head = None
                        playlist.size = 0
                        for sid in sorted(library.keys()):
                            playlist.append(library[sid])
                        player.playlist_changed()
                        player.set_repeat_mode(RepeatMode.ALL)
                        player.play_immediately(library[min(library)])  # bài có ID nhỏ nhất
                        for _ in range(25):
                            player.next()
                        oldest_id = player.history.elements[0].data.song_id
                        newest_id = player.history.peek().data.song_id
                        print("Đã phát qua 25 bài liên tiếp trên HistoryStack(capacity=20).")
                        print(f"Stack giữ đúng {player.history.size}/20 bài mới nhất (Đáy cũ nhất: ID={oldest_id}, Đỉnh mới nhất: ID={newest_id}).")
                    else:
                        last_cmd = "Phím [15]->[1] Nạp 5 bài HIT mẫu (ID 5..9)"
                        sample_ids = [5, 6, 7, 8, 9]
                        for sid in sample_ids:
                            s = library.get(sid)
                            if s and not playlist.find_song_by_id(sid):
                                playlist.append(s)
                        added = [sid for sid in sample_ids if library.get(sid)]
                        if not added:
                            print("Thư viện không có bài nào ID 5..9 nên không nạp mẫu được.")
                        else:
                            player.playlist_changed()
                            player.play_immediately(library[added[0]])
                            player.set_repeat_mode(RepeatMode.ALL)
                            print(f"Đã nạp bài HIT ID {added}, phát bài ID={added[0]} & bật Repeat ALL.")
                finally:
                    sys.stdout = old_stdout
                last_output = tmp.getvalue()
 
        elif choice == "16":  # Xem bảng Thư viện 22 bài (songs.txt)
            last_cmd = f"Phím [16] Xem Thư viện {len(library)} bài (songs.txt)"
            last_output = f"Đã đọc thành công {len(library)} bài hát từ file songs.txt vào bộ nhớ."
            extra_table = render_library_table()
 
        elif choice == "0":
            print("\n  Bye!\n")
            break
        else:
            last_cmd = f"Nhập mã Menu = '{choice}' (Ngoài phạm vi 0 - 16)"
            with io.StringIO() as tmp:
                old_stdout = sys.stdout
                if IS_TTY:
                    sys.stdout = tmp
                try:
                    print("Lựa chọn không hợp lệ")
                finally:
                    sys.stdout = old_stdout
                last_output = tmp.getvalue()
 