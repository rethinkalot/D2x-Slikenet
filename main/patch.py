import os

def patch_multibot_jolts():
    file_path = r"C:/Games/D2s/build/main/multibot.c"
    if not os.path.exists(file_path):
        # Fallback tracking if target is relative to source folder structures
        file_path = "multibot.c"

    print(f"Opening memory stream for: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Locate the target tracking block within non-owner shortpos extraction
    target_block = """                Objects[botnum].orient.fvec.x = client_orient.fvec.x + ((target_orient.fvec.x - client_orient.fvec.x) >> 2);
                Objects[botnum].orient.fvec.y = client_orient.fvec.y + ((target_orient.fvec.y - client_orient.fvec.y) >> 2);
                Objects[botnum].orient.fvec.z = client_orient.fvec.z + ((target_orient.fvec.z - client_orient.fvec.z) >> 2);
                
                Objects[botnum].orient.uvec.x = client_orient.uvec.x + ((target_orient.uvec.x - client_orient.uvec.x) >> 2);
                Objects[botnum].orient.uvec.y = client_orient.uvec.y + ((target_orient.uvec.y - client_orient.uvec.y) >> 2);
                Objects[botnum].orient.uvec.z = client_orient.uvec.z + ((target_orient.uvec.z - client_orient.uvec.z) >> 2);
                
                Objects[botnum].orient.rvec.x = client_orient.rvec.x + ((target_orient.rvec.x - client_orient.rvec.x) >> 2);
                Objects[botnum].orient.rvec.y = client_orient.rvec.y + ((target_orient.rvec.y - client_orient.rvec.y) >> 2);
                Objects[botnum].orient.rvec.z = client_orient.rvec.z + ((target_orient.rvec.z - client_orient.rvec.z) >> 2);"""

    # Inject an inversion boundary checker that prevents internal matrix collapses
    replacement_block = """                // Slikenet: Guard matrix integrity during extreme cross-quadrant transitions behind objects
                fix dot_check = vm_vec_dot(&client_orient.fvec, &target_orient.fvec);
                int blend_shift = (dot_check < -F1_0 / 2) ? 1 : 2; // Accelerate tracking convergence on inversion thresholds

                Objects[botnum].orient.fvec.x = client_orient.fvec.x + ((target_orient.fvec.x - client_orient.fvec.x) >> blend_shift);
                Objects[botnum].orient.fvec.y = client_orient.fvec.y + ((target_orient.fvec.y - client_orient.fvec.y) >> blend_shift);
                Objects[botnum].orient.fvec.z = client_orient.fvec.z + ((target_orient.fvec.z - client_orient.fvec.z) >> blend_shift);
                
                Objects[botnum].orient.uvec.x = client_orient.uvec.x + ((target_orient.uvec.x - client_orient.uvec.x) >> blend_shift);
                Objects[botnum].orient.uvec.y = client_orient.uvec.y + ((target_orient.uvec.y - client_orient.uvec.y) >> blend_shift);
                Objects[botnum].orient.uvec.z = client_orient.uvec.z + ((target_orient.uvec.z - client_orient.uvec.z) >> blend_shift);
                
                Objects[botnum].orient.rvec.x = client_orient.rvec.x + ((target_orient.rvec.x - client_orient.rvec.x) >> blend_shift);
                Objects[botnum].orient.rvec.y = client_orient.rvec.y + ((target_orient.rvec.y - client_orient.rvec.y) >> blend_shift);
                Objects[botnum].orient.rvec.z = client_orient.rvec.z + ((target_orient.rvec.z - client_orient.rvec.z) >> blend_shift);"""

    if target_block in content:
        content = content.replace(target_block, replacement_block)
        with open(file_path, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(content)
        print("SUCCESS: Smooth matrix tracking patch applied successfully with CR/LF preservation.")
    else:
        print("ERROR: Target vector block not found. Code might already be altered or formatted differently.")

if __name__ == "__main__":
    patch_multibot_jolts()
