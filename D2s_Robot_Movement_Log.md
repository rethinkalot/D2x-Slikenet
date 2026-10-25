# D2s Robot Movement Change Log

## Current source state
- multibot.c uses quaternionpos (Phase C) for send/receive.
- Cadence macro MIN_ROBOT_COM_GAP not present in live source; timing via ROBOT_TIMEOUT = F1_0*1.
- Blend core from Phase A (D1) not yet ported to D2s (verify multi_blend_robot_positions).

## Planned Phase B
1. Raise send cadence (adjust robot_last_send_time / pending logic).
2. Confirm precision payload (quaternionpos 40 bytes) in both endian paths.
Build complete 4.2MB

## multibot.c factor breakdown
- MIN_ROBOT_COM_GAP: cadence gap (if present)
- robot_last_send_time: last send timestamp per slot
- ROBOT_TIMEOUT: stale threshold (F1_0*1)
- extract_shortpos: decodes shortpos into object
- smoothing >>2: 1/4 position blend
- multi_do_robot_position: receive + claim logic
- multi_send_robot_position: send pending
- multi_blend_robot_positions: stub (not implemented)
