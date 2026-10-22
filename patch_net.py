import os

file_udp_h = "main/net_udp.h"
file_multi_c = "main/multi.c"

# ---- Part 1: Update net_udp.h to 36 ----
if os.path.exists(file_udp_h):
    with open(file_udp_h, "r") as f:
        text_h = f.read()
    
    for val in ["600", "60", "240", "24"]:
        old_macro = f"#define NET_TELEMETRY_POSITION_CAPACITY {val}"
        if old_macro in text_h:
            text_h = text_h.replace(old_macro, "#define NET_TELEMETRY_POSITION_CAPACITY 36")
            break
            
    with open(file_udp_h, "w") as f:
        f.write(text_h)
    print("Successfully bumped net_udp.h telemetry bounds to 36.")

# ---- Part 2: Update multi.c to 36 ----
if os.path.exists(file_multi_c):
    with open(file_multi_c, "r") as f:
        content_c = f.read()

    # Replace our previous 24-frame macro injection with 36
    if "#define MULTI_INTERP_SAMPLES 24" in content_c:
        content_c = content_c.replace("#define MULTI_INTERP_SAMPLES 24", "#define MULTI_INTERP_SAMPLES 36")
        with open(file_multi_c, "w") as f:
            f.write(content_c)
        print("Successfully bumped multi.c interpolation structures to 36.")
