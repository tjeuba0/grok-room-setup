# Grok Room Setup

Cấu hình bốn vai Grok chạy qua **Paseo official** (`getpaseo/paseo`), không qua fork Paseo.

```text
Paseo (grok-supervisor | grok-lead | grok-peer | grok-review)
  -> ~/.local/bin/grok-room <role>
  -> grok-room-sync
  -> ~/.grok-runtime/<role>
  -> grok agent stdio
```

Repo này **không** sở hữu `~/.grok`. Mỗi người tự cài và đăng nhập Grok. Sync chỉ copy `auth.json` sang bốn home riêng rồi sinh profile/config.

Bố cục overlay/script tham khảo setup room cũ; runtime hiện tại là Grok + Paseo official.

## Người clone cần gì

- macOS (hoặc Unix) với Bash, Python 3, Git, Node, npm, `jq`
- Grok CLI đã cài và **đã login** (`grok` trên `PATH`)
- SSH GitHub đọc được `git@github.com:getpaseo/paseo.git`
- `~/.local/bin` nằm trên `PATH`

Mặc định Paseo được clone tới `~/projects/supervisors/paseo-grok-room`. Đổi trong `paseo/source.toml` **trước** khi chạy `install-paseo-fork` nếu máy bạn khác path đó.

## Cài

```bash
git clone git@github.com:tjeuba0/grok-room-setup.git grok-room-setup
cd grok-room-setup

./scripts/doctor
./scripts/install                 # dry-run
./scripts/install --apply         # backup rồi cài overlay, launcher, template Paseo
./scripts/install-paseo-fork      # clone Paseo official, nhánh local grok-room, link CLI
./scripts/sync-all                # sinh ~/.grok-runtime/{supervisor,lead,peer,review}
./scripts/verify
./scripts/verify --live           # daemon 127.0.0.1:6767 phải đang chạy
```

`install-paseo-fork` giữ tên lệnh cũ; nó **không** cài fork Paseo. Nó clone official, checkout commit đã pin trong `paseo/source.toml`, link:

```text
~/.local/bin/paseo
  -> ~/projects/supervisors/paseo-grok-room/packages/cli/bin/paseo
```

File bị ghi đè được backup tại `~/.codex-room-backups/install-<UTC>/`. Installer không ghi `~/.grok` và không ghi `~/.codex`.

Sau khi có checkout Paseo:

```bash
paseo daemon start
paseo daemon status
```

`paseo-local-update` kéo Paseo, build, thay Desktop app, restart daemon. Chỉ chạy khi không có agent đang làm việc.

## Thế nào là xong

- `./scripts/verify` và `./scripts/verify --live` in `VERIFY_OK`
- Paseo có bốn provider: `grok-supervisor`, `grok-lead`, `grok-peer`, `grok-review`
- CLI `paseo` trỏ vào `paseo-grok-room`
- Tạo **seat Lead mới**: thinking mặc định **High**; Review **Medium**

Seat cũ không nhận thinking mới. Đổi overlay/config xong phải `sync-all`, `paseo daemon reload` (hoặc restart khi không có agent), rồi tạo seat mới.

## Vai

| Vai | Model | Thinking | `create_agent` Paseo |
| --- | --- | --- | --- |
| Supervisor | `grok-4.6` | high | có |
| Lead | `grok-4.6` | high | có |
| Peer | `grok-4.6` | high | không |
| Review FAST | `grok-4.6` | medium | không |

Nhãn model (“Grok 4.6 High”) chỉ là chữ. Mức suy nghĩ là chip thinking / `thought_level`.

Native Grok subagent bị tắt trong `grok-room` (`--no-subagents`, `--disallowed-tools Agent`), không phải Paseo. Paseo chỉ tắt `create_agent` cho Peer/Review qua `paseoTools.enabled`. Review vẫn có shell; đó không phải sandbox tuyệt đối. Chi tiết: [docs/architecture.md](docs/architecture.md).

## File được cài

| Trong repo | Trên máy |
| --- | --- |
| `home/.config/codex-room/` | `~/.config/codex-room/` (tên thư mục cũ, nội dung Grok Room) |
| `home/.local/bin/grok-room` | `~/.local/bin/grok-room` |
| `home/.local/bin/grok-room-sync` | `~/.local/bin/grok-room-sync` |
| `home/.paseo/config.json.template` | `~/.paseo/config.json` |

`@@HOME@@` được thay lúc install. Session, log, auth, keypair, worktree, backup **không** vào Git.

Launcher `codex-room*` còn trong repo để rollback, không phải provider đang chạy.

## Thao tác thường dùng

```bash
# Sửa overlay xong, sinh lại runtime
./scripts/sync-all

# Chỉ kiểm tra source, chưa cần runtime đã cài
./scripts/verify --source

# Có daemon Paseo
./scripts/verify --live

# Sau khi sửa ~/.paseo/config.json
paseo daemon reload
```

Đổi overlay: [docs/operations.md](docs/operations.md).  
Path và quyền sở hữu: [docs/paths-and-ownership.md](docs/paths-and-ownership.md).  
Paseo official: [docs/paseo-fork.md](docs/paseo-fork.md).
