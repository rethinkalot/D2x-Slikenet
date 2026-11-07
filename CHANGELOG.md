# D2X-Redux SLikeNet: Changelog

Everything since the clean baseline (tag `D2-SlikeNet-clean-baseline`, 2026-10-10). D2s tracks D1s feature for feature, except where noted.

## Multiplayer and networking

- SLikeNet carries in-game traffic (ship positions, combat actions) on the game port, alongside plain UDP. Both share one socket on port 42424 by default (`main/slikenet_bridge.cpp`, `main/net_udp_socket.c`).
- Datagram filter on the receive thread: SLikeNet takes its own packets and queues the game's plain datagrams (128 slots) for the game.
- Token-checked hello handshake. Joiners dial lower-numbered players and the host; observers dial the host only. Per-peer fallback to plain UDP until a peer finishes the handshake.
- No plain-UDP fallback if the lane cannot bind: 10 retries at 50 ms, then host or join fails.
- Packets Per Second up to 90 (co-op interpolation assumes 60). Frame rates up to 360 FPS.
- HUD link status at match start: "SLikeNet Peer Link Success" or "SLikeNet Peer Link Failure" per player.
- Handshake diagnostics in the console: `SLikeNet Handshake OUT` on each connect attempt, `SLikeNet Handshake IN` every 5 s while handshakes arrive. Lane totals added to `memlog.txt`.
- The 15 s no-packet player timeout is disabled (`net_udp_timeout_check` returns early). The 15 s unacknowledged-packet kick in `net_udp_noloss_process_queue` is commented out for players and observers. A full reliable-packet queue still dumps a non-acknowledging player.
- Multiplayer protocol version raised from 30005 to 30006 ("Redux 1.1 + SLikeNet in-game transport", commit `4c4c860c`). Builds from the baseline cannot join games from this version.

## Running several copies on one PC

- `proxy.cfg` with `bind_ip=<ipv4>` binds that copy's game and broadcast sockets to one local address, so several copies share port 42424 (ported from D1s).
- Windows 11 EcoQoS opt-out (`arch/sdl/timer.c`): a window behind another one is no longer slowed down.

## Ships

- Remote ships are drawn between two real updates (`multi_interp_update_remote`), now also re-applied after physics each frame. A ship that crosses a segment boundary mid-interval no longer snaps to its newest pose; it only snaps when the interpolated point lands in a third segment.
- Robot smoothing is not ported to D2s yet.

## Observers

- Camera update moved to run after the network and physics step, with a rigid third-person follow. This fixes the ship jolting in third person.
- Own custom controls, wall-aware free-fly camera, ships near the camera fade out.

## Demos

- Recorded and played back at your frame rate, with live `FPS` and recorded `DEMO` rate on the playback HUD.
- Afterburner states are recorded and replayed.

## HUD and options

- HUD messages stay 1.5x longer: single message 4.5 s (was 3 s), stacked 3 s each (was 2 s), repeats reset to 3 s (`main/hud.c`).
- Speedrun timers RTA and IGT, toggled in the Misc menu. Timer issues fixed.
- "Suppress HUD Messages (SP)", graphics/texture/model toggles, client-side reduced flash, optional velocity meter.
- Original D1 weapons toggle for single-player.
- Power-ups: fixed 3D model orientation and rotation.

## Build and repository

- Release build (about 5.8 MB), SLikeNet linked with `--whole-archive`.
- Removed stray root files (`.clinerules`, `Checklist.txt`) and the workspace `skills/` copies; Ponytail and caveman now come from user-level plugins.
