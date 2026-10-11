#include <stdio.h>
#include <stddef.h>

#include "xdescent.h"
#include "carray.h"
#include "tga.h"
#include "ase.h"
#include "submodel.h"
#include "xmodel.h"
#include "xmodelnames.h"
extern "C" {
#include "internal.h"
#include "../3d/globvars.h"
#undef FILENAME_LEN
#include "config.h"
#undef FILENAME_LEN
#include "polyobj.h"
#include "texmap.h"
#include "powerup.h"
}

struct CGameFolders gameFolders;
struct CGameStates gameStates;

struct vert {
	CFloatVector3 pos;
	tTexCoord2f tex;
};

struct render_model {
	ASE::CModel m;
	int *bmvertofs;
	int *bmvertcount;
	struct vert *verts;
	int vertcount;
	GLuint *bmtex;
	GLuint vbo;
	int glloaded;
};

void *xmodels[NUM_XMODELS];

// return -1 on error
int xmodel_load_gl(void *model) {
	#ifdef WIN32
	static int glew_loaded;
	if (!glew_loaded) {
		glewInit();
		glew_loaded = 1;
	}
	#endif

	render_model& rm = *(render_model *)model;
	int num_bitmaps = rm.m.m_textures.m_nBitmaps;
	glGenTextures(num_bitmaps, rm.bmtex);
	for (int i = 0; i < num_bitmaps; i++) {
		CBitmap& bm = rm.m.m_textures.m_bitmaps[i];
		if (!bm.Width() || (!rm.bmvertcount[i] && !bm.Team()))
			continue;
		glBindTexture(GL_TEXTURE_2D, rm.bmtex[i]);
		if (bm.BPP() == 4)
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
				bm.Width(), bm.Height(), 0, GL_RGBA, GL_UNSIGNED_BYTE,
				bm.Buffer());
		else
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
				bm.Width(), bm.Height(), 0, GL_RGB, GL_UNSIGNED_BYTE,
				bm.Buffer());
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
		glGenerateMipmap(GL_TEXTURE_2D);
	}

	glGenBuffers(1, &rm.vbo);

	glBindBuffer(GL_ARRAY_BUFFER, rm.vbo);
	glBufferData(GL_ARRAY_BUFFER, rm.vertcount * sizeof(rm.verts[0]), rm.verts, GL_STATIC_DRAW);
	glBindBuffer(GL_ARRAY_BUFFER, 0);

	rm.glloaded = 1;
	return 0;
}

void xmodel_free_gl(void *model) {
	render_model& rm = *(render_model *)model;
	if (!rm.glloaded)
		return;
	glDeleteTextures(rm.m.m_textures.m_nBitmaps, rm.bmtex);
	memset(rm.bmtex, 0, rm.m.m_textures.m_nBitmaps * sizeof(rm.bmtex[0]));
	glDeleteBuffers(1, &rm.vbo);
	rm.vbo = 0;
	rm.glloaded = 0;
}

void xmodel_free(void *model) {
	render_model* rmp = (render_model *)model;
	render_model& rm = *rmp;
	xmodel_free_gl(model);
	delete[] rm.verts;
	delete[] rm.bmvertcount;
	delete[] rm.bmvertofs;
	delete[] rm.bmtex;
	delete rmp;
}

// return NULL on error
void *xmodel_load(const char *filename) {
	render_model* rmp = new render_model();
	render_model& rm = *rmp;
	ASE::CModel& m = rm.m;
	int ret = m.Read(filename, 0, 0);
	if (!ret) {
		delete rmp;
		return NULL;
	}
	rm.glloaded = 0;
	int num_bitmaps = m.m_textures.m_nBitmaps;
	for (int i = 0; i < num_bitmaps; i++) {
		CBitmap& bm = m.m_textures.m_bitmaps[i];
		uint8_t *data = bm.Buffer();
		if (!data || bm.BPP() != 3)
			continue;
		int size = bm.Size();
		for (int j = 0; j < size; j += 3) {
			uint8_t x = data[j];
			data[j] = data[j + 2];
			data[j + 2] = x;
		}
	}
	int *bmvertcount = rm.bmvertcount = new int[num_bitmaps]();
	int i, v;
	ASE::CSubModel *sm;
	for (sm = m.m_subModels, i = 0; sm; sm = sm->m_next, i++) {
		if (ExcludeSubModel(sm, 0, -1, 0, 0))
			continue;
		for (int f = 0; f < sm->m_nFaces; f++)
			bmvertcount[sm->/*m_faces[f].*/m_nBitmap]+=3;
	}

	int *bmvertofs = rm.bmvertofs = new int[num_bitmaps]();
	v = 0;
	for (int i = 0; i < num_bitmaps; i++) {
		bmvertofs[i] = v;
		v += bmvertcount[i];
	}
	int vertcount = rm.vertcount = v;

	int *bmvertpos = new int[num_bitmaps]();
	memcpy(bmvertpos, rm.bmvertofs, num_bitmaps * sizeof(int));

	vert *verts = rm.verts = new vert[vertcount];
	for (sm = m.m_subModels; sm; sm = sm->m_next) {
		if (ExcludeSubModel(sm, 0, -1, 0, 0))
			continue;
		int hastex = sm->m_nTexCoord;
		CFloatVector3 ofs = sm->m_vOffset;
		for (int fi = 0; fi < sm->m_nFaces; fi++) {
			ASE::CFace& f = sm->m_faces[fi];
			int bm = sm->m_nBitmap, v = bmvertpos[bm];
			for (int j = 0; j < 3; j++) {
				verts[v + j].pos = sm->m_vertices[f.m_nVerts[j]].m_vertex + ofs;
				if (hastex)
					verts[v + j].tex = sm->m_texCoord[f.m_nTexCoord[j]];
			}
			bmvertpos[bm] += 3;
		}
	}
	delete[] bmvertpos;

	rm.bmtex = new GLuint[num_bitmaps]();
	rm.vbo = 0;

	return rmp;
}

void xmodel_show(void *model, int mpcolor, g3s_lrgb *light) {
	render_model& rm = *(render_model *)model;
	int num_bitmaps = rm.m.m_textures.m_nBitmaps;

	if (GameCfg.ClassicDepth && !(Game_mode & GM_MULTI))
		glEnable(GL_DEPTH_TEST);

	float color_alpha;
	if (tmap_drawer_ptr == draw_tmap_flat) { // cloaked effect
		OGL_DISABLE(TEXTURE_2D);
		color_alpha = 1.0 - (grd_curcanv->cv_fade_level/(GLfloat)GR_FADE_LEVELS) * 0.9;
		glColor4f(0, 0, 0, color_alpha);
	} else {
		OGL_ENABLE(TEXTURE_2D);
		color_alpha = (grd_curcanv->cv_fade_level >= GR_FADE_OFF)?1.0:(1.0 - (float)grd_curcanv->cv_fade_level / ((float)GR_FADE_LEVELS - 1.0));
		glColor4f(f2fl(light->r), f2fl(light->g), f2fl(light->b), color_alpha);
	}

	glBindBuffer(GL_ARRAY_BUFFER, rm.vbo);
	glVertexPointer(3, GL_FLOAT, sizeof(vert), (void *)0);
	glTexCoordPointer(2, GL_FLOAT, sizeof(vert), (void *)offsetof(vert, tex));
	glEnableClientState(GL_VERTEX_ARRAY);
	glEnableClientState(GL_TEXTURE_COORD_ARRAY);
	int team = mpcolor == -1 ? 0 : mpcolor >= 7 ? 1 : mpcolor + 2;
	for (int i = 0; i < num_bitmaps; i++) {
		if (!rm.bmvertcount[i])
			continue;
		if (rm.m.m_textures.m_bitmaps[i].Team() && team && rm.m.m_textures.m_bitmaps[i].Team() != team) {
			for (int j = 0; j < num_bitmaps; j++)
				if (rm.m.m_textures.m_bitmaps[j].Team() == team)
					glBindTexture(GL_TEXTURE_2D, rm.bmtex[j]);
		} else
			glBindTexture(GL_TEXTURE_2D, rm.bmtex[i]);
		glDrawArrays(GL_TRIANGLES, rm.bmvertofs[i], rm.bmvertcount[i]);
	}
	glDisableClientState(GL_TEXTURE_COORD_ARRAY);
	glDisableClientState(GL_VERTEX_ARRAY);
	glBindBuffer(GL_ARRAY_BUFFER, 0);
	if (GameCfg.ClassicDepth && !(Game_mode & GM_MULTI))
		glDisable(GL_DEPTH_TEST);
}

#if 0
#define GLAPIENTRY
#define GL_DEBUG_TYPE_ERROR               0x824C
#define GL_DEBUG_OUTPUT                   0x92E0

void GLAPIENTRY gl_debug_callback(GLenum source, GLenum type, GLuint id, GLenum severity, GLsizei length,
	const GLchar* message, const void* userParam) {
	//if (severity == 0x826b) return;
	fprintf(stderr, "GL CALLBACK: %s type = 0x%x, severity = 0x%x, message = %s\n",
		(type == GL_DEBUG_TYPE_ERROR ? "** GL ERROR **" : ""),
		type, severity, message);
}

void gl_debug() {
	glEnable(GL_DEBUG_OUTPUT);
	glDebugMessageCallback(gl_debug_callback, 0 );
	glDebugMessageControl(GL_DONT_CARE, GL_DONT_CARE, GL_DEBUG_SEVERITY_NOTIFICATION, 0, NULL, GL_FALSE);
}
#endif

void xmodel_show_at(void *model, vms_vector *pos, vms_matrix *orient, int mpcolor, g3s_lrgb *light) {
	if (!((render_model *)model)->glloaded)
		xmodel_load_gl(model);

	vms_vector v,v2,vpos;
	vms_matrix vmat,m;
	vm_vec_sub(&v,&View_position,pos);
	vm_vec_rotate(&v2,&v,orient);
	vm_copy_transpose_matrix(&m,orient);
	vm_matrix_x_matrix(&vmat,&m,&View_matrix);
	vm_vec_rotate(&vpos,&v2,&vmat);

	vpos.z *= -1;

	// create 4x4 lookat matrix
	float fm[16];
	fix *xp = &vmat.rvec.x;
	for (int i = 0; i < 3; i++) {
		for (int j = 0; j < 3; j++)
			fm[i * 4 + j] = f2fl(xp[j * 3 + i]);
		fm[i * 4 + 3] = 0;
	}
	xp = &vpos.x;
	for (int j = 0; j < 3; j++)
		fm[3 * 4 + j] = -f2fl(xp[j]);
	fm[15] = 1;

	// forward vec -> backward vec
	for (int j = 0; j < 3; j++)
		fm[2 + j * 4] *= -1;

	glPushMatrix();
	glLoadMatrixf(fm);
	xmodel_show(model, mpcolor, light);
	glPopMatrix();
}

void xmodel_free_all() {
	for (int i = 0; i < NUM_XMODELS; i++)
		if (xmodels[i]) {
			xmodel_free(xmodels[i]);
			xmodels[i] = NULL;
		}
}

void xmodel_load_all() {
	static int free_registered;
	for (int i = 0; i < NUM_XMODELS; i++)
		if (!xmodels[i])
			xmodels[i] = xmodel_load(xmodelnames[i]);
	if (!free_registered) {
		atexit(xmodel_free_all);
		free_registered = 1;
	}
}

void xmodel_load_gl_all() {
	for (int i = 0; i < NUM_XMODELS; i++)
		if (xmodels[i])
			xmodel_load_gl(xmodels[i]);
}

void xmodel_free_gl_all() {
	for (int i = 0; i < NUM_XMODELS; i++)
		if (xmodels[i])
			xmodel_free_gl(xmodels[i]);
}

#define ELMS(x) (sizeof(x) / sizeof((x)[0]))

static int xmodel_translate(enum xmodel_type type, int modelnum)
{
	if (type == XM_POLYOBJ && modelnum >= 0 && modelnum < ELMS(xmodel_xlate))
		return xmodel_xlate[modelnum];

	if (type == XM_POWERUP)
	{
		switch (modelnum)
		{
			case POW_EXTRA_LIFE: return model_pow_extralife;
			case POW_ENERGY: return model_pow_energy;
			case POW_SHIELD_BOOST: return model_pow_shield;
			case POW_LASER: return model_pow_laser;
			case POW_KEY_BLUE: return model_pow_bluekey;
			case POW_KEY_RED: return model_pow_redkey;
			case POW_KEY_GOLD: return model_pow_goldkey;
			case POW_MISSILE_1: return model_concussion;
			case POW_MISSILE_4: return model_pow_concussion4;
			case POW_QUAD_FIRE: return model_pow_quadlaser;
			case POW_VULCAN_WEAPON: return model_pow_vulcan;
			case POW_SPREADFIRE_WEAPON: return model_pow_spreadfire;
			case POW_PLASMA_WEAPON: return model_pow_plasma;
			case POW_FUSION_WEAPON: return model_pow_fusion;
			case POW_PROXIMITY_WEAPON: return model_pow_pminepack;
			case POW_HOMING_AMMO_1: return model_homer;
			case POW_HOMING_AMMO_4: return model_pow_homer4;
			case POW_SMARTBOMB_WEAPON: return model_smartmsl;
			case POW_MEGA_WEAPON: return model_mega;
			case POW_VULCAN_AMMO: return model_pow_vulcanammo;
			case POW_CLOAK: return model_pow_cloak;
			case POW_INVULNERABILITY: return model_pow_invul;
			case POW_GAUSS_WEAPON: return model_gauss;
			case POW_HELIX_WEAPON: return model_helix;
			case POW_PHOENIX_WEAPON: return model_phoenix;
			case POW_OMEGA_WEAPON: return model_omega;
			case POW_SUPER_LASER: return model_superlaser;
			case POW_FULL_MAP: return model_pow_full_map;
			case POW_CONVERTER: return model_converter;
			case POW_AMMO_RACK: return model_armorack;
			case POW_AFTERBURNER: return model_afterburner;
			case POW_HEADLIGHT: return model_pow_headlight;
			case POW_SMISSILE1_1: return model_smartmsl;
			case POW_SMISSILE1_4: return model_smartmsl;
			case POW_GUIDED_MISSILE_1: return model_guided;
			case POW_GUIDED_MISSILE_4: return model_guided4;
			case POW_SMART_MINE: return model_sminepack;
			case POW_MERCURY_MISSILE_1: return model_mercury;
			case POW_MERCURY_MISSILE_4: return model_mercury4;
			case POW_EARTHSHAKER_MISSILE: return model_eshaker;
			default: return -1;
		}
	}
	return -1;
}

// returns 1 if drawn
int xmodel_show_if_loaded(enum xmodel_type type, int modelnum, vms_vector *pos, vms_matrix *orient, int mpcolor, g3s_lrgb *light) {
	int xmodelnum = xmodel_translate(type, modelnum);
	if (xmodelnum == -1 || !xmodels[xmodelnum])
		return 0;
	xmodel_show_at(xmodels[xmodelnum], pos, orient, mpcolor, light);
	return 1;
}

int xmodel_exists(enum xmodel_type type, int modelnum) {
	int xmodelnum = xmodel_translate(type, modelnum);
	return xmodelnum != -1 && xmodels[xmodelnum];
}
