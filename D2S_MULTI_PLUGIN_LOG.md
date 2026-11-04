# D2s SLikeNet — Multiplayer Change Log (hand-off, mirrors D1S_MULTI_PLUGIN_LOG.md)

Builds clean; not yet play-tested. `MULTI_PROTO_VERSION` is 30006 (was 30005), so older D2 builds can't join.

## SLikeNet transport (2026-11-03)

Replicated from D1s, not copied wholesale. The bridge is generic and is identical to D1s; everything around it was adapted to D2.

- **Ports:** plain UDP on 42424 (discovery, lobby, tracker, join, sync); SLikeNet on game port + 1000 (43424 / 43425 for the two testbenches). Hosts forward both.
- `main/slikenet_bridge.cpp` / `.h`: same as D1s. Constants checked against D2: `UPID_MAX_SIZE` 1024, `MAX_PLAYERS` 8 + `MAX_OBSERVERS` 16 = 24 peers, `CON_NET_STATUS` -6, `CON_NET_DEALLOC` -7.
- `main/net_udp_socket.c`: `udp_send_slikenet()` sends exactly `UPID_PDATA` (sequenced), `UPID_OBJECT_DATA` (reliable ordered), `UPID_MDATA_PNORM` (unreliable) and `UPID_MDATA_PNEEDACK` (reliable) over the lane when the peer is ready, else plain UDP. The `#error` pin on those four UPID values is kept. Peer starts/stops with socket 0. Kept D2's `_af` socket code (D1s hardcodes `AF_INET`). Did not port D1s' `SO_REUSEADDR`.
- `udp_count_received()` is new in D2 (was inline in `dxx_recvfrom`) so the lane drain feeds the same `[RX]` line.
- `main/net_udp.c`: hello/connect handshake (`net_udp_slikenet_frame/_process_hello/_listen`), drains in `net_udp_flush()` and `net_udp_listen()`, `SLikeNet lane:` totals line in memlog, and the PDATA timer now steps by the exact interval (D1s feffd182). All under `#ifndef IPv6`.
- `main/net_udp_ui.c`: game list no longer opens the extra default-port socket, and re-requests the game list every 5 s off the default port (D1s fc9c6e4e).
- `main/CMakeLists.txt`: `slikenet_bridge.cpp` added, `slikenet_modern` linked as `$<LINK_LIBRARY:WHOLE_ARCHIVE,...>` (needs CMake 3.24+).
- Deleted the dummy `include/BitStream.h` (D1s did the same in 6825d859).

## Guards added on top of D1s

- `Netgame.PacketsPerSec` is clamped to 10..90 when read from the sync packet (`net_udp.c`, next to the read). It was unvalidated and is divided into in several send timers (zero would crash).
- The multi packet number is now read as 32 bits in `net_udp_process_mdata` (two sites). It was read as 16 bits while the sender writes 32, so after 65,535 priority-2 packets in one session the ACKs would stop matching and players would time out. **Same bug exists in D1s** (`net_udp.c`, `GET_INTEL_SHORT(&data[6])` in `net_udp_process_mdata`); not yet fixed there.

## Weapon fire reliability (matches D1s)

Player fire (`multi.c` `multi_send_fire`), the owner's robot fire (`multibot.c` `multi_send_robot_frame`) and non-owner robot fire (`multibot.c` `multi_send_robot_fire`, was priority 0) now all go out at priority 2, i.e. reliable on the lane. These are the same three sites D1s changed.

## Readouts (-debug / -verbose / -safelog), aligned with D1s

- `-safelog` code was already identical; no change.
- `CON_NET_SESSION` removed from `console.h` / `console.c`. The end-of-game snapshot is now `CON_NET_STATUS` (so `-debug` only), titled "SLikeNet Host-Start Netgame Snapshot (debug footer)", with D1s wording ("Start time", "Players at start") and D1s trailing line. D2's extra "Player scores at leave" block and the joiner snapshot are kept; D1s now has them too.
- The 10 PHYSFS messages in `physfsx.c` and the "Axis Movement detected" line moved from `CON_DEBUG` to `CON_VERBOSE` (they show under `-verbose`, as in D1s).
- Per-packet `[TX]`/`[RX]` lines are limited to one sample per second (D2 already did this; D1s now does too). The counters still count every packet. The 5 s summary uses per-second math and also prints D2's `PData x/y updates/s` line, now in D1s as well.
- Not carried over: D1s' two spawn-weighting `CON_VERBOSE` lines (D2 has no such feature). D2-only verbose lines (buddy bot, HAM selection) stay.

## Robot movement: deliberately NOT changed

D2's robot movement is close to right, so it was left alone. D1s' robot gates were not ported because they break D2:

- A top-of-`do_ai_frame` authority gate would stop remote robots firing at the local player (`multi_can_move_robot` lets `ROBOT_FIRE_AGITATION` through for other players' robots), skip `do_any_robot_dying_frame` (remote robots would never finish their death roll or explode), freeze boss cloak expiry and the flinch/`SKIP_AI_COUNT` cleanup, and stop animation and awareness timers. D2 already blocks non-owner movement via `ai_multiplayer_awareness()` -> `multi_can_move_robot()`.
- A `do_physics_sim` gate would skip death-roll tumble, morph spin and robot-side collisions (damage, steal, kamikaze).
- D1s' `multi_do_robot_position` blend overshoots (pos is already at the network position when the error is added) and its `multi_blend_robot_positions()` only calls `update_object_seg`; the blend described in D1S_MULTI_PLUGIN_LOG.md is not in D1s' HEAD.

Open items noticed while reviewing (not changed, no data yet): D2 `ROBOT_TIMEOUT` is 4 s (D1s 2 s); mdata/robot cadence is 60 Hz (D1s 20 Hz); `multibot.c` opens `robotinfo.txt` on every owner robot send (debug leftover); observers return from `do_ai_frame` before `do_any_robot_dying_frame`; `NET_TELEMETRY_POSITION_CAPACITY` is 36 (D1s 8192), which empties the memlog RX-gap stats; `MULTI_INTERP_SAMPLES` is defined twice in `multi.c`.

## Testing notes

- Both testbench inis have `;-debug` commented out. Enable it on at least one copy to see the telemetry.
- `C:/Games/D2x2/Data` is empty and `descent2.ham` is renamed `1descent2.ham`; check that copy launches before a two-copy test.
- Expect: `SLikeNet Lane is ACTIVE on port 43424` (D2x) / `43425` (D2x2), `Peer READY`, orange `[TX]` / blue `[RX]` lines (one sample per second plus the 5 s totals), and a non-zero `SLikeNet lane:` line in `memlog.txt` after a game.

## Observer, menu and demo alignment with D1s (2026-11-03)

Builds clean and is deployed; not yet play-tested. Findings came from a read-only comparison of D1s and D2s.

**Observer (custom binds are the user-configurable Prev/Next/Cycle camera binds; the stock Ctrl binds are untouched)**
- D1s only: `handle_observer_control_event` had lost its Prev/Next branch, so the custom Next/Previous player binds did nothing. Restored in D1s. D2s already had it.
- D2s: `multi_process_data` dropped `MULTI_SHIP_STATUS`, `MULTI_POSITION` and `MULTI_TYPING_STATE` on every observer node, so an observer never saw the watched player's energy, ammo or weapons. It also dropped any message whose second byte was 8 or more, which hits messages that carry a segment number there (door open). Now only those three telemetry types are checked, and only for a bad or observer sender id.
- D2s: `MULTI_SHIP_STATUS` sent the weapon flags as one byte, losing Phoenix and Omega (primary bits 8-9) and Mercury and Earthshaker (secondary bits 8-9). The high bits now ride in the top bits of the laser level byte; packet size stays 43.
- D2s: picking up Super Laser or the Ammo Rack now sends ship status, as the other powerups do.
- D2s: "Cycle camera" now cycles first person, third person, free (D1s behaviour), and the bind row is labelled "Cycle camera".
- D2s: observer camera uses D1s' raw-position compare and clamped blend (`Real_raw_pos`, `Real_raw_orient`), which stops the third-person camera restarting its timer every frame.
- D2s: with Observer Chat off, F8 no longer enters a typing mode that can't be left.
- D2s: Gauss muzzle flash is no longer hidden by "Hide energy weapon muzzle"; super laser levels now group as "super laser" in the damage breakdown.

**Remote ships and demos**
- D2s remote-ship smoothing (`multi_interp_update_remote`) is switched off. D1s' version has an index bug and a sequence-filter bug that freeze it after 128 packets, so D1s really runs the newest packet plus physics. D2s now does the same. The history is still recorded.
- D2s demo rewind and fast-forward scale with the max fps like D1s, and the HUD follows the recorded player during playback. D2-only demo events, `DEMO_VERSION` 15 and the afterburner/guided/boss data are untouched.

**Menus**
- D2s advanced netgame options set `ShortPackets` from the Difficulty slider (`opt_shortpack` was never set). It is now 0, the default. **The same bug exists in D1s** (`net_udp_ui.c:273`) and is not fixed there.
- D2s Misc menu: the "Show D2-style Prox. Bomb Gauge" toggle did nothing in D2, so its row is now blank. Graphics menu array is 22 (it already used 20 of 20).
- `max_numobservers` read from a preset is clamped to `MAX_OBSERVERS`.

**Found, not changed** (see the reports): D1s `do_obs_menu` exits on "Switch Game Mode" and "Share Settings" because of `if (i < 0) break;`, and discards edits on ESC; D1s `multi.c:2217` is missing the `[mode]` index on `ObsChat`; D2 observers see a fixed Omega charge (the observed player's charge is not sent); the D2 energy-to-shield converter does not send ship status; D2 `ROBOT_TIMEOUT` and 60 Hz cadence are unchanged.

## Follow-ups from the 2026-11-04 tests (D2s and D1s)

Builds clean and deployed to both testbenches; not yet play-tested.

- **Scores at leave** (footer and memlog) now print `score`, `kills` and `deaths`; Anarchy only counts kills. Same change in D1s.
- **Bridge** (`slikenet_bridge.cpp`, identical in both repos): the fallback counter ignores addresses that are not lane peers (observers), an unanswered hello is resent at most once a second, a hello can't take over a player whose lane is still connected on another address, and a failed `Connect()` logs a red line.
- **Handshake log**: "Requested update to address..." and "not updated" lines are only logged when the address really changes (they printed every second before). Both repos.
- **Omega charge for observers (D2s)**: `MULTI_SHIP_STATUS` grew from 43 to 44 bytes (one byte of charge); `Multi_omega_charge[]` holds it per player, the three gauge spots use `omega_charge_for(pnum)`, and the owner sends status while charge changes (rate limited). `MULTI_PROTO_VERSION` was not bumped again (builds are not released).
- **Memlog window (D2s)**: position samples are recorded for 10 seconds starting when a second player is in the game; capacity is 1024 per player (was 36). D1s still records continuously.
- **D1s observer menu**: only ESC (-1) leaves the menu now, so Switch Game Mode and Share Settings work; `ObsChat` is indexed by game mode in `multi_do_obs_message`.
- **ShortPackets** left as is in both repos (D2s sets it to 0 after the Advanced menu; D1s untouched), as decided.

## Fixes from the 4-instance test (2026-11-04, D2s and D1s)

- **Client-to-client lane never became ready**: `net_udp_slikenet_process_hello` checked `Netgame.players[pnum].connected`, which a client never sets for someone who joined after it did. It now checks `Players[pnum].connected`. Both repos.
- `UPID_OBSQUIT` no longer logs "unknown packet type 30" (the host handles it earlier in `net_udp_process_packet`). Both repos.
- gamelog timestamp file names used `tm_mon` without +1 (October in November). Both repos (`console.c`).
- D2s: removed the leftover `robotinfo.txt` write on every robot send (`multibot.c`).
- D2s: `net_udp_telemetry_record_fire` is now called from `multi_send_fire` and `multi_do_fire`, as in D1s, so the memlog fire-event counts work.
- Host-start settings are written to `gamelog.txt` without `-debug` and to `memlog.txt` for every player who leaves (both repos).

## Robot movement, Stage 1 (2026-11-04, D2s)

Robot/mdata send cadence is now 20 Hz like D1s (`net_udp_do_frame`). `multi_do_robot_position` (non-owner branch) now follows D1s' receive recipe: validate the packet segment, zero velocity, clear `PF_LEVELLING | PF_TURNROLL`, `extract_shortpos`, rebuild the orientation with `vm_vector_2_matrix`, `update_object_seg`; no position restore or velocity servo. A robot in its death roll (`ai_info.dying_start_time`) ignores position packets so its local tumble finishes. `do_ai_frame` and `do_physics_sim` are deliberately unchanged: D1s' early returns would stop remote robots dying, firing at the local player and uncloaking in D2s. Stage 2 (cache + per-frame ease/dead reckoning) is planned after RETHINK's tests. Not yet play-tested.
