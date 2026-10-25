# Diff Category List (with values)

## Timing
- MIN_CONTROL_TIME: F1_2*1 (check this )
- ROBOT_TIMEOUT: F1_3*1
- MIN_ROBOT_COM_GAP: not present

## State
- robot_controlled: array of objnums
- robot_send_pending: int array
- robot_fired: int array
- robot_agitation: int array
- robot_fire_buf: buffer
- Robot_info: struct array

## Network
- multi_send_data: function
- multi_send_robot_frame: function
- multi_send_robot_position: function
- multi_send_robot_position_sub: function
- multi_send_release_robot: function
- objnum_local_to_remote/remote_to_local: functions
- REMOTE_OWNER/REMOTE_SLOT_NUM: fields
- MULTI_ROBOT_PRIORITY: macro ((objnum+pnum)%(N_players-(host_is_obs?1:0)))
- multi_i_am_master: function

## Movement
- multi_add_controlled_robot: function
- multi_can_move_robot: function
- multi_delete_controlled_robot: function
- multi_do_claim_robot: function
- multi_drop_robot_powerups: function
- multi_dump_robots: function
- multi_explode_robot_sub: function
- multi_send_stolen_items: function
- MIN_TO_ADD: 60
- MAX_TO_DELETE: 61
- host_is_obs: Netgame flag

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


# WORKS and EFFECTS CURRENT BUILD
# EFFECTS CURRENT BUILD/ is Original and working.
# (none new)

# Effects current build/ is not original and working.
# (none)

# Can Work, But turned off.
- Dynamic PPS (commented)
- Telemetry (removed)
