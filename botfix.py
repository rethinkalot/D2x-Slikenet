import os
import re

def absolute_restore_multibot(absolute_path):
    if not os.path.exists(absolute_path):
        print(f"[ERROR] Target file path not found: {absolute_path}")
        return

    with open(absolute_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Perfect implementation layout for the function block
    restored_function_code = """void
multi_do_robot_position(const ubyte *buf)
{
	// Process robot movement sent by another player

	short botnum, remote_botnum;
	char pnum;
	int loc = 1;
#ifdef WORDS_BIGENDIAN
	shortpos sp;
#endif

	pnum = buf[loc];										loc += 1;

	remote_botnum = GET_INTEL_SHORT(buf + loc);
	botnum = objnum_remote_to_local(remote_botnum, (sbyte)buf[loc+2]); loc += 3;

	if ((botnum < 0) || (botnum > Highest_object_index)) {
		return;
	}

	if ((Objects[botnum].type != OBJ_ROBOT) || (Objects[botnum].flags & OF_EXPLODING)) {
		return;
	}
		
	if (Objects[botnum].ctype.ai_info.REMOTE_OWNER != pnum)
	{	
		if (Objects[botnum].ctype.ai_info.REMOTE_OWNER == -1)
		{
			// Robot claim packet must have gotten lost, let this player claim it.
			if (Objects[botnum].ctype.ai_info.REMOTE_SLOT_NUM > 3) {
				Objects[botnum].ctype.ai_info.REMOTE_OWNER = pnum;
				Objects[botnum].ctype.ai_info.REMOTE_SLOT_NUM = 0;
			}
			else
				Objects[botnum].ctype.ai_info.REMOTE_SLOT_NUM++;
		}
		else
		{
			return;
		}
	}

#ifndef WORDS_BIGENDIAN
	{
		vms_vector client_pos = Objects[botnum].pos;
		vms_matrix client_orient = Objects[botnum].orient;
		
		// Reset velocity accumulator variables before new location updates
		if (Objects[botnum].ctype.ai_info.REMOTE_OWNER != Player_num)
		{
			Objects[botnum].mtype.phys_info.velocity.x = 0;
			Objects[botnum].mtype.phys_info.velocity.y = 0;
			Objects[botnum].mtype.phys_info.velocity.z = 0;
		}

		extract_shortpos(&Objects[botnum], (shortpos *)(buf+loc), 0);
		
		if (Objects[botnum].ctype.ai_info.REMOTE_OWNER != Player_num)
		{
			vms_vector pos_error;
			vm_vec_sub(&pos_error, &Objects[botnum].pos, &client_pos);
			
			if (vm_vec_mag_quick(&pos_error) > F1_0 * 15) {
				update_object_seg(&Objects[botnum]);
			} else {
				vms_matrix target_orient = Objects[botnum].orient;
				Objects[botnum].pos = client_pos;
				
				// Smoothly blend look vectors (Forward, Up, Right) to clear rotation snap
				Objects[botnum].orient.fvec.x = client_orient.fvec.x + ((target_orient.fvec.x - client_orient.fvec.x) >> 2);
				Objects[botnum].orient.fvec.y = client_orient.fvec.y + ((target_orient.fvec.y - client_orient.fvec.y) >> 2);
				Objects[botnum].orient.fvec.z = client_orient.fvec.z + ((target_orient.fvec.z - client_orient.fvec.z) >> 2);
				
				Objects[botnum].orient.uvec.x = client_orient.uvec.x + ((target_orient.uvec.x - client_orient.uvec.x) >> 2);
				Objects[botnum].orient.uvec.y = client_orient.uvec.y + ((target_orient.uvec.y - client_orient.uvec.y) >> 2);
				Objects[botnum].orient.uvec.z = client_orient.uvec.z + ((target_orient.uvec.z - client_orient.uvec.z) >> 2);
				
				Objects[botnum].orient.rvec.x = client_orient.rvec.x + ((target_orient.rvec.x - client_orient.rvec.x) >> 2);
				Objects[botnum].orient.rvec.y = client_orient.rvec.y + ((target_orient.rvec.y - client_orient.rvec.y) >> 2);
				Objects[botnum].orient.rvec.z = client_orient.rvec.z + ((target_orient.rvec.z - client_orient.rvec.z) >> 2);
				
				vm_vec_normalize_quick(&Objects[botnum].orient.fvec);
				vm_vec_normalize_quick(&Objects[botnum].orient.uvec);
				vm_vec_normalize_quick(&Objects[botnum].orient.rvec);

				// Apply predictive velocity thrust vector
				Objects[botnum].mtype.phys_info.velocity.x = (pos_error.x * 4);
				Objects[botnum].mtype.phys_info.velocity.y = (pos_error.y * 4);
				Objects[botnum].mtype.phys_info.velocity.z = (pos_error.z * 4);
				
				update_object_seg(&Objects[botnum]);
			}
		}
	}
#else
	memcpy((ubyte *)(sp.bytemat), (ubyte *)(buf + loc), 9);		loc += 9;
	memcpy((ubyte *)&(sp.xo), (ubyte *)(buf + loc), 14);
	extract_shortpos(&Objects[botnum], &sp, 1);
#endif"""
}

    # Uses a resilient regex boundary pattern to capture everything between clean anchors
    robust_pattern = r'(Objects\[botnum\]\.ctype\.ai_info\.REMOTE_SLOT_NUM\s*=\s*0;.*?\}[\s\n]*)(.*?)([\s\n]*void[\s\n]*multi_do_robot_fire)'
    
    modified, count = re.subn(robust_pattern, r'\1' + restored_function_code + r'\n\n\3', content, flags=re.DOTALL)
    
    if count > 0:
        with open(absolute_path, 'w', encoding='utf-8') as f:
            f.write(modified)
        print(f"[SUCCESS] Repaired file structural alignment in {absolute_path}!")
    else:
        print("[ERROR] Base signature bounds altered. Check source integrity.")

ROOT_DIR = "C:/Games/D2s"  
MULTIBOT_C_PATH = os.path.join(ROOT_DIR, "main/multibot.c")

absolute_restore_multibot(MULTIBOT_C_PATH)
