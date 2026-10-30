import os
import re

print("[INFO] Initiating Descent 2 multi-file type alignment pass...")

multi_path = "multi.c"
if not os.path.exists(multi_path):
    multi_path = r"C:/Games/D2s/main/multi.c"

net_path = "net_udp.c"
if not os.path.exists(net_path):
    net_path = r"C:/Games/D2s/main/net_udp.c"

# ----------------- STEP 1: ADD KICK FUNCTION TO NET_UDP.C -----------------
if os.path.exists(net_path):
    print(f"[INFO] Injecting net_udp_kick_all_observers into: {net_path}")
    with open(net_path, "r", encoding="utf-8") as f:
        net_content = f.read()

    # Target the bottom of net_udp.c to safely append our helper function
    kick_function = """
void net_udp_kick_all_observers(void)
{
    int i;
    for (i = 0; i < Netgame.max_numobservers; i++) {
        if (Netgame.observers[i].connected == 1) {
            net_udp_dump_player(Netgame.observers[i].protocol.udp.addr, 0, DUMP_KICKED);
        }
    }
}
"""
    if "net_udp_kick_all_observers" not in net_content:
        net_content += kick_function
        with open(net_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(net_content)
        print("[SUCCESS] net_udp_kick_all_observers added to net_udp.c.")
else:
    print("[ERROR] net_udp_c could not be resolved.")

# ----------------- STEP 2: UPDATE MULTI.C TO CALL THE NEW FUNCTION -----------------
if os.path.exists(multi_path):
    print(f"[INFO] Updating /noobs command routing in: {multi_path}")
    with open(multi_path, "r", encoding="utf-8") as f:
        multi_content = f.read()

    # Target the old broken loop inside the /noobs condition block
    old_noobs_block = """            for (int i = 0; i < Netgame.max_numobservers; i++) {
                if (Netgame.observers[i].connected == 1) {
                    net_udp_dump_player(Netgame.observers[i].addr, 0, DUMP_KICKED);
                }
            }"""
            
    # Alternative old block check if it still had the old protocol subfields
    old_noobs_block_alt = """            for (int i = 0; i < Netgame.max_numobservers; i++) {
                if (Netgame.observers[i].connected == 1) {
                    net_udp_dump_player(Netgame.observers[i].protocol.udp.addr, 0, DUMP_KICKED);
                }
            }"""

    new_noobs_block = """            extern void net_udp_kick_all_observers(void);
            net_udp_kick_all_observers();"""

    if old_noobs_block in multi_content:
        multi_content = multi_content.replace(old_noobs_block, new_noobs_block)
    elif old_noobs_block_alt in multi_content:
        multi_content = multi_content.replace(old_noobs_block_alt, new_noobs_block)
    else:
        # Fallback regex substitution to find and clean the block regardless of exact address spelling
        multi_content = re.sub(
            r"for\s*\(\s*int\s+i\s*=\s*0\s*;\s*i\s*<\s*Netgame\.max_numobservers\s*;\s*i\s*\+\+\s*\)\s*\{[\s\n]*if\s*\(\s*Netgame\.observers\[i\]\.connected\s*==\s*1\s*\)\s*\{.*?\n\s*\}\s*\n\s*\}",
            "extern void net_udp_kick_all_observers(void);\n            net_udp_kick_all_observers();",
            multi_content,
            flags=re.DOTALL
        )

    with open(multi_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(multi_content)
    print("[SUCCESS] multi.c redirected to use new network-safe kick function.")
else:
    print("[ERROR] multi.c could not be resolved.")
