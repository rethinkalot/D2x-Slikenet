import os

file_path = r"main/net_udp.h"

if os.path.exists(file_path):
    with open(file_path, "r") as f:
        content = f.read()
    
    # Update to a precise 10-second window at 60 PPS
    old_macro = "#define NET_TELEMETRY_POSITION_CAPACITY 8192"
    new_macros = (
        "#define NET_TELEMETRY_POSITION_CAPACITY 600\n"
        "#define NET_TELEMETRY_BOT_CAPACITY      1024"
    )
    
    if old_macro in content:
        updated_content = content.replace(old_macro, new_macros)
        with open(file_path, "w") as f:
            f.write(updated_content)
        print("[SUCCESS] Adjusted NET_TELEMETRY_POSITION_CAPACITY to 600 (10 seconds at 60 PPS).")
    else:
        print("[WARN] Macro definition not found or already updated.")
else:
    print(f"[ERROR] Could not locate file at: {file_path}")
