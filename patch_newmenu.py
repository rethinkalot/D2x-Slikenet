#!/usr/bin/env python3
with open('main/newmenu.c', 'r') as f:
    content = f.read()

# Edit 1: nm_draw_background - change 'scores' to dynamic bitmapname
content = content.replace(
    'ogl_loadbmtexture_f(&nm_background, GameCfg.TexFilt, "scores");',
    'ogl_loadbmtexture_f(&nm_background, GameCfg.TexFilt, HIRESMODE ? "scoresb" : "scores");'
)

# Edit 2: nm_draw_background - add post-smash reload check after the OGL block
old = '#if defined(OGL)\n\t\togl_loadbmtexture_f(&nm_background, GameCfg.TexFilt, HIRESMODE ? "scoresb" : "scores");\n#endif\n\t\tBGScaleX=((float)SWIDTH/nm_background.bm_w);'
new = '#if defined(OGL)\n\t\togl_loadbmtexture_f(&nm_background, GameCfg.TexFilt, HIRESMODE ? "scoresb" : "scores");\n#endif\n\n\t\t// Reload if GL texture was invalidated (e.g. custom textures toggle),\n\t\t// using the correct bitmapname so the PNG override is found.\n\t\tif (!nm_background.gltexture || nm_background.gltexture->handle <= 0)\n\t\t\togl_loadbmtexture_f(&nm_background, GameCfg.TexFilt, HIRESMODE ? "scoresb" : "scores");\n\n\t\tBGScaleX=((float)SWIDTH/nm_background.bm_w);'
content = content.replace(old, new)

# Edit 3: nm_draw_background1 - add OGL block with bitmapname before gr_palette_load
old2 = '\t\t(void)pcx_error;\n\t\t}\n\t\tgr_palette_load( gr_palette );'
new2 = '\t\t(void)pcx_error;\n\t\t}\n\n#if defined(OGL)\n\t\t// Load (or reload after GL texture invalidation, e.g. custom textures toggle)\n\t\t// with a bitmapname so the PNG override can be found.\n\t\t// Falls back to the PCX when custom textures is off or no PNG exists.\n\t\t{\n\t\t\tchar bmname[64];\n\t\t\tconst char *dot = strrchr(filename, \'.\');\n\t\t\tint len = dot ? (int)(dot - filename) : (int)strlen(filename);\n\t\t\tif (len > 0 && (size_t)len < sizeof(bmname))\n\t\t\t{\n\t\t\t\tstrncpy(bmname, filename, len);\n\t\t\t\tbmname[len] = \'\\0\';\n\t\t\t\t// strip any directory prefix so only the basename is used\n\t\t\t\tconst char *slash = strrchr(bmname, \'/\');\n\t\t\t\tif (!slash) slash = strrchr(bmname, \'\\\\\');\n\t\t\t\tif (slash)\n\t\t\t\t\tmemmove(bmname, slash + 1, strlen(slash) + 1);\n\n\t\t\t\tif (!nm_background1.gltexture || nm_background1.gltexture->handle <= 0)\n\t\t\t\t\togl_loadbmtexture_f(&nm_background1, GameCfg.TexFilt, bmname);\n\t\t\t}\n\t\t}\n#endif\n\n\t\tgr_palette_load( gr_palette );'
content = content.replace(old2, new2)

with open('main/newmenu.c', 'w') as f:
    f.write(content)

print('Done')
