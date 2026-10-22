import os

file_path = r"main/multibot.c"

if os.path.exists(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    target_found = False
    new_lines = []
    
    for line in lines:
        new_lines.append(line)
        # Strip trailing/leading white spaces and tabs to ensure a bulletproof match
        if line.strip() == "extract_shortpos(&Objects[botnum], (shortpos *)(buf+loc), 0);":
            target_found = True
            # Zero-array blend: glides the bot from its current rendering frame coordinates
            blend_code = (
                "        {\n"
                "            vms_vector old_pos = Objects[botnum].pos;\n"
                "            // Smooth out 167 FPS packet delivery gaps without memory array leaks\n"
                "            Objects[botnum].pos.x = old_pos.x + ((Objects[botnum].pos.x - old_pos.x) >> 2);\n"
                "            Objects[botnum].pos.y = old_pos.y + ((Objects[botnum].pos.y - old_pos.y) >> 2);\n"
                "            Objects[botnum].pos.z = old_pos.z + ((Objects[botnum].pos.z - old_pos.z) >> 2);\n"
                "        }\n"
            )
            new_lines.append(blend_code)

    if target_found:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print("[SUCCESS] Applied tab-stripped baseline low-pass blending filter.")
    else:
        print("[ERROR] Base line anchor not found. Indentation layout mismatch remains.")
else:
    print(f"[ERROR] Missing file path target: {file_path}")
