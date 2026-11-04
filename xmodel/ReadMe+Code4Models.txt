Put the 2 filesfor each build "xmodel.cpp"  and  "xmodelnames.h" inside your:
   D1root\xmodel\"FilesHere"
   D2root\xmodel\"FilesHere"


Update following code blocks: this will give whitelist the 3d models by name
and it will add a toggle in graphics
#1 Enables Models in your config
#2 Loads Models
#3 Adds Menu Toggle in graphics to disable/enable models vs host option
#4 Renders Polys for 3dModels unless host says no
#5 Renders Objects for 3d Models unless host says no
#6-1 Core Rendering codeblocks (reads the ase file information for pos/orient/and ids of old originals)
#6-2 turns on or off the original sprites via toggle and info from #6-1
-----------------------------------------------------

### 1. **Configuration Initialization** (`main/config.c`):
```c
GameCfg.UseCustomModels = 1;  // Default: enabled```


### 2. **Model Loading** (`main/bm.c` line 136-137):
```c
#ifdef OGL
if (GameCfg.UseCustomModels)
    xmodel_load_all();  // Loads all models from xmodelnames[]
#endif
```

### 3. **Menu Toggle** (`main/menu.c` lines 1461-1463):
```c
if (GameCfg.UseCustomModels != m[opt_gr_custommodels].value) {
    GameCfg.UseCustomModels = m[opt_gr_custommodels].value;
    if (GameCfg.UseCustomModels)
        xmodel_load_all();     // Load models
    else
        xmodel_free_all();     // Free models
}
```

### 4. **Polyobject Rendering** (`main/polyobj.c` line 523-526):
```c
#ifdef OGL
if (GameCfg.UseCustomModels && (!(Game_mode & GM_MULTI) || Netgame.AllowCustomModelsTextures))
    if (xmodel_show_if_loaded(XM_POLYOBJ, model_num, pos, orient, ...))
        return;  // Model drawn (or skipped if already drawn)
#endif
```

### 5. **Powerup Rendering** (`main/powerup.c` line 135):
```c
if (xmodel_show_if_loaded(XM_POWERUP, obj->id, &obj->pos, &orient, -1, &lrgb))
    return;
```

### 6. **Core Rendering Functions** (`xmodel/xmodel.cpp`):

**`xmodel_show_if_loaded()`** (line 317-323):
```c
int xmodel_show_if_loaded(enum xmodel_type mt, int modelnum, ...) {
    int xmodelnum = xmodel_xlate(mt, modelnum);
    if (xmodelnum == -1 || !xmodels[xmodelnum])
        return 0;
    xmodel_show_at(xmodels[xmodelnum], pos, orient, ...);
    return 1;
}
```

`xmodel_xlate()`  (line 308-314):
```c
static int xmodel_xlate(enum xmodel_type mt, int modelnum) {
    if (mt == XM_POLYOBJ && modelnum >= 0 && modelnum < SDL_arraysize(xmodel_polyobj_xlate))
        return xmodel_polyobj_xlate[modelnum];
    if (mt == XM_POWERUP && modelnum >= 0 && modelnum < SDL_arraysize(xmodel_powerup_xlate))
        return xmodel_powerup_xlate[modelnum];
    return -1;
}
```



