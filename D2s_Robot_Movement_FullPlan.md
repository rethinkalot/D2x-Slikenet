# D2s Robot Movement Full Plan

## Current
- shortpos, 1/4 smoothing
- cadence TBD

## Target
- quaternionpos (40 bytes)
- blend cache + multi_blend_robot_positions
- LERP pos factor 0.15, SLERP orient 0.15
- zero velocity on stale
- skip local-owned

## Values
- Blend factor 0.15: lower=smoother/lag, higher=snappy
- Cadence 30ms: lower=more updates/bandwidth
- Precision quaternionpos vs shortpos

## Checklist
1. Convert send/receive to quaternionpos
2. Add blend cache
3. Implement multi_blend_robot_positions
4. Call in ai.c
5. Tune and test
