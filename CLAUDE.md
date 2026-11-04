# CLAUDE.md
- ALWAYS use Caveman skill.
- ALWAYS use Ponytail skill.

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

D2X-Redux SLikeNet: a Descent 2 source port (C, with C++ for the SLikeNet bridge and `xmodel/`) that is moving multiplayer onto SLikeNet (a RakNet fork). The sibling D1 port lives in `C:/Games/D1s` with its own `CLAUDE.md`; the SLikeNet work started there and was replicated here, not copied wholesale. `D2S_MULTI_PLUGIN_LOG.md` records what was ported and what deliberately differs; `D1S_MULTI_PLUGIN_LOG.md` is the D1 side.

## Working rules (from RETHINK,)

- Plan, confirm, execute, build, then wait for the next task. Raise likely problems and choices before deciding.
- Make only the code changes that were asked for. No unrequested refactors or style cleanups.
- If an attempt fails or you get stuck, stop and ask how to proceed.
- Don't run git commands or scripts on your own initiative. Don't commit untested builds; RETHINK tests first.
- Ask before destructive commands, and don't treat one approval as standing permission. No `rm -rf`-style cleans; builds stay incremental.
- Don't install or reconfigure toolchains.
- Keep the network telemetry console layout exactly as it is, including wording, colors and `CON_NET_*` priorities, and style new network messages to match: orange `[TX]`, blue `[RX]`, green status, red for deallocated or failed. All traffic, on either lane, must feed the same `[TX]` / `[RX]` lines (`main/net_udp_socket.c`).
- Use targeted reads and greps. Many files here are very large (`main/net_udp.c` is over 5,000 lines).

## Build

Windows 11, MSYS2 MinGW64 at `C:/Programs/msys64`, Ninja. RETHINK's standard build-and-deploy command, from Git Bash or an MSYS2 shell:

    cd /c/Games/D2s && export PATH=/c/Programs/msys64/mingw64/bin:$PATH && cmake -G Ninja -B build && cmake --build build --target main/clean 2>/dev/null || rm -f build/main/d2x-redux.exe && cmake --build build -- -j10 && if [ -f build/main/d2x-redux.exe ]; then mkdir -p /c/Games/D2x /c/Games/D2x2; taskkill //F //IM D2x-Redux-SLikeNet.exe 2>/dev/null || tskill D2x-Redux-SLikeNet 2>/dev/null; sleep 1; rm -f /c/Games/D2x/D2x-Redux-SLikeNet.exe /c/Games/D2x2/D2x-Redux-SLikeNet.exe; cp -v build/main/d2x-redux.exe /c/Games/D2x/D2x-Redux-SLikeNet.exe; cp -v build/main/d2x-redux.exe /c/Games/D2x2/D2x-Redux-SLikeNet.exe; echo 'Confirm Complete'; else echo 'Build completed, but no expected executable was found.' >&2; exit 1; fi

Use it exactly as written; it is also the "Build D2x-Redux-SLikeNet" task in `.vscode/tasks.json`. It closes any running game before copying. Output is `build/main/d2x-redux.exe`. Apart from this command's own relink step, don't remove it from `build/main/`.

A build-only run, with no deploy, is still:

    cmake --build build -- -j10

`CMakePresets.json` also defines `windows-mingw-debug` and `windows-mingw-release`, which build into `build/<preset>/`.

CMake options are at the top of the root `CMakeLists.txt` (`OPENGL`, `UDP`, `TRACKER`, `EDITOR`, `DXX_USE_SDL12_COMPAT`, ...). The game uses the SDL 1.2 API; `-DSDL2=ON` is a hard error.

There are no project tests or lint targets (test files under `thirdparty/` belong to those libraries). Verification is a successful build plus in-game testing by RETHINK.

## Deploy and run

Testbenches are `C:/Games/D2x` and `C:/Games/D2x2`, two installs for testing multiplayer. After a successful build, copy to both:

    taskkill //F //IM D2x-Redux-SLikeNet.exe 2>/dev/null; sleep 1
    cp -v build/main/d2x-redux.exe /c/Games/D2x/D2x-Redux-SLikeNet.exe
    cp -v build/main/d2x-redux.exe /c/Games/D2x2/D2x-Redux-SLikeNet.exe

The `taskkill` closes any running game, so check before using it during a test session. Report "Confirm Complete" when the sequence finishes.

Run from the testbench: `./D2x-Redux-SLikeNet.exe -window -notitles -nostickykeys`. The executable is a GUI-subsystem app, so a console only appears with these flags:

- `-debug`: SLikeNet/network telemetry (`CON_NET_*` in `include/console.h`) and `CON_DEBUG`. The per packet `[TX]` / `[RX]` lines sample at most one packet per second so this doesn't slow packet handling; the counters and the 5 s totals still count every packet. The end-of-game "Host-Start Netgame Snapshot" footer is `-debug` only.
- `-verbose`: event, input and window diagnostics (`CON_VERBOSE`)

The testbench folders also hold `gamelog.txt` and `memlog.txt`.

## Architecture

- `main/` builds the `d2x-redux` executable and holds nearly all game logic.
- `2d`, `3d`, `iff`, `maths`, `mem`, `misc`, `texmap` are static engine libraries. `arch/` has the platform layers (`sdl`, `ogl`, `win32`, `x11`, `cocoa`). `xmodel/` is the OpenGL model loader. `editor/` and `ui/` only build with `EDITOR=ON`.
- `thirdparty/` is vendored dependencies, built by default (`DXX_USE_BUNDLED_DEPS`). Treat it as upstream code. `vcpkg.json` only applies with bundled deps off.

### Multiplayer layers

1. `main/multi.c`, `main/multibot.c`: game-level messages and robot sync. Robot positions are `shortpos` (`MULTI_ROBOT_POSITION`) and are smoothed on receive in `multi_do_robot_position()`; there is no `multi_blend_robot_positions()` and no `quaternionpos` robot sync in D2. Ownership goes through `ai_multiplayer_awareness()` (`ai2.c`) -> `multi_can_move_robot()` (`multibot.c`). Do not add a blanket `REMOTE_OWNER` early return to `do_ai_frame()` or `do_physics_sim()` (D1s has one): it would stop remote robots dying, firing at the local player and uncloaking. The robot movement is close to right, so leave it unless asked.
2. `main/net_udp.c`, `main/net_udp_ui.c`: session, join, sync and tracker logic.
3. `main/net_udp_socket.c`: raw sockets and receive (`udp_receive_packet`).
4. `main/slikenet_bridge.cpp` / `.h`: the C-callable wrapper around `SLNet::RakPeerInterface`, linked to `slikenet_modern` (built in `thirdparty/CMakeLists.txt`) as a whole archive.

### SLikeNet migration is unfinished

Check these against the current code before relying on them:

- Two ports: plain UDP on the game port (42424) for discovery, lobby, tracker, join and sync; SLikeNet on game port + 1000 for in-game traffic (`SLIKENET_PORT_OFFSET` in `slikenet_bridge.cpp`). Hosts forward both. In `d2x.ini`, `-udp_hostport` is 42424 on both copies, and `-udp_myport` is 42424 for `D2x` (SLikeNet 43424) and 42425 for `D2x2` (SLikeNet 43425).
- The peer starts and stops with game socket 0 in `udp_open_socket` / `udp_close_socket`. If it can't bind, the game stays on plain UDP.
- Only 4 packet types ride SLikeNet; `dxx_sendto` in `net_udp_socket.c` picks the transport by packet ID (`udp_send_slikenet`), falling back to plain UDP when the peer isn't ready:
  - `UPID_PDATA` (position/velocity/orientation): sequenced, newest wins.
  - `UPID_OBJECT_DATA` (object sync for a joining player): reliable ordered, its own channel. Joiners connect to SLikeNet only once playing, so this normally falls back to plain UDP.
  - `UPID_MDATA_PNORM` (multi buffer, priority 0-1): unreliable, and a lost packet is not resent.
  - `UPID_MDATA_PNEEDACK` (multi buffer, priority 2, including weapon fire): reliable, unordered. The game's ACK layer still runs, and `net_udp_noloss_validate_mdata()` drops duplicates.
  Everything else — lobby/session state (`UPID_SYNC`, discovery, join, tracker), observers, `UPID_MDATA_ACK`, `UPID_PING`/`PONG`, `UPID_ENDLEVEL_*`, `UPID_P2P_PING`/`PONG`, `UPID_PROXY`/`UPID_REATTEMPT_DIRECT` — stays on native plain UDP; it's unaffected by whether the SLikeNet lane is connected.
- In-game, each player connects to lower-numbered players, then a token-checked hello binds the SLikeNet address to the player's address (`net_udp_slikenet_frame` in `net_udp.c`). Received packets are reported with that player address, so existing sender checks still apply.
- Not on SLikeNet: observers, and IPv6 builds (compiled out).

## Repo notes

- Work branch: `D2-SlikeNet-WorkBranch`. Remote: `rethinkalot/D2x-Slikenet`.
- `main/patch.py` is a one-off script that rewrites source files in place. Read it before running it, and only run it if asked.
- `.clinerules` is RETHINK's rule file for Cline. Where it differs from this file, follow this file and ask if unsure.

## Where D2s differs from D1s (keep these when porting D1 changes)

- Data: `descent2.ham` / `descent2.hog` (not `.pig`). Joins and kicks check the HAM hash (`net_udp_ham_hash_is_approved`, `UPID_HAM_HASH_SIZE`), and the sync packet carries extra D2 `Netgame` bytes (`DisableGaussSplash`, `BornWithBurner`, `OriginalD1Weapons`).
- `MULTI_PROTO_VERSION` is its own counter (30006 with the SLikeNet lane; D1s is 30008). `multi.h` has many more messages than D1s: guided missile, thief stolen items, boss actions, CTF flags, smart mines, `MULTI_RESPAWN_ROBOT`.
- AI is split across `ai.c` and `ai2.c`. Robot/mdata cadence is `F1_0/60` (D1s `F1_0/20`) and `ROBOT_TIMEOUT` is `F1_0*4` (D1s `*2`). Leave both until there is data.
- Weapon fire (player fire, owner robot fire, non-owner robot fire) is priority 2, reliable on the lane, as in D1s.
- Telemetry: `NET_TELEMETRY_POSITION_CAPACITY` is 36 (D1s 8192), plus `NET_TELEMETRY_BOT_CAPACITY` and `Config_Client_History_Slider`. The memlog split/timestamp options are `-gamelog_split` / `-gamelog_timestamp` (D1s `-memlog_*`).
- Sockets keep the `_af` address-family macro (D1s hardcodes `AF_INET`), and D2s does not set `SO_REUSEADDR`.
- Line endings are mixed (`net_udp_socket.c`, `net_udp.h`, `multibot.c/.h`, `main/CMakeLists.txt` are CRLF; `net_udp.c`, `net_udp_ui.c`, `multi.c/.h`, `ai.c`, `ai2.c` are LF) and indentation is tabs in `net_udp_ui.c`. Check `git ls-files --eol <file>` before scripted edits.
