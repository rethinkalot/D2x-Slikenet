# Categorized Full List

## Original/Old Implemented
- ROBOT_TIMEOUT F1_0*1
- GM_MULTI_ROBOTS enabled in coop
- extract_shortpos snap
- ROBOT_GEN_TIME F1_0*5
- MULTI_ROBOT_PRIORITY
- robot_last_send_time
- robot_send_pending
- robot_fired
- robot_controlled
- MAX_ROBOTS_CONTROLLED
- MIN_ROBOT_COM_GAP (if present)
- smoothing >>2 (removed)
- multi_do_robot_position
- multi_send_robot_position

## Original/Old Not Active/Stale
- (none active)

## New Implemented & Working
- Dynamic PPS (commented)
- Telemetry (removed)

## New Unfinished/Incomplete/Stale
- Blend cache
- Triangulation
- Telemetry
- Dynamic PPS
- quaternionpos 40 bytes
- blend cache + multi_blend_robot_positions
- LERP pos factor 0.15
- SLERP orient 0.15
- zero velocity on stale
- skip local-owned
- cadence 30ms
- peer broadcast
- small quaternionpos packets
- multi_blend_robot_positions stub
