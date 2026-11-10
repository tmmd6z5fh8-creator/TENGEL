# kisekae/r3d/glb: GLB (Meshy) software renderer

This directory is a copy of the stand-alone renderer from W/glb (/home/claude/work/glb). It is used by `kisekae/flat/shiden_glb.py`, which draws the 紫電 (sd) film's face and hoof from まさちゃん's Meshy models.

It is numpy plus a small C rasterizer. It does not need three.js, Blender or a GPU.

## Files

| file | what |
|---|---|
| `glb.py` | glTF 2.0 / GLB loader. `load(path) -> Model`; `Model.flatten(t=None) -> [Prim]` returns world-space prims (skinned at time t); `Model.summary()`; `Model.bbox()` |
| `raster.c` | C visibility-buffer rasterizer (`rasterize`, `rasterize_depth`) |
| `raster.py` | `Camera.look_at`, `Light`, `render(prims, cam, lights, ss, model_matrix, …) -> dict` of linear HDR buffers (`rgb alpha depth normal emissive pos albedo ao shadow mat`), plus `tonemap`, `bloom`, `save` |
| `shot.py` | Shot helpers from W/glb (`analyze`, `face_cam`, `hoof_cam`, `orbit_cam`, `find_eyes_from_frame`, `eye_glow`, `frame`). Not used by the sd film; kept for the next shots |

## Build

`libraster.so` is **not committed**. `raster.py` builds it on first import, and rebuilds it whenever `raster.c` is newer than the library:

    gcc -O3 -shared -fPIC -o libraster.so raster.c -lm

Do not commit `libraster.so` or `__pycache__`.

## Inputs (external, never committed)

The Meshy GLBs are inputs from まさちゃん and are not part of the repository. Point to them with environment variables:

| env | default | what |
|---|---|---|
| `SD_HORSE_GLB` | `/home/claude/work/horse_in/new/Violet_Nightmare_Meshy_AI_2026-11-01_58c781.glb` | 7.75 M triangle textured bust: black horse, violet mane and eyes, white star |
| `SD_HOOF_GLB` | `/home/claude/work/horse_in/new/Violet_Hoof_Flame_Meshy_AI_2026-11-01_862a69.glb` | 0.2 M triangle purple-black foreleg with hoof |
| `METAL_HORSE_GLB` | `/home/claude/work/band3d/orig/silver_thunder.glb` | 0.69 M triangle silver statue of a galloping horse ("Silver Thunder"). Used by `kisekae/flat/metal_glb.py` for the Silver and Gold band wallpapers (第4.149版) |
| `TENGEL_STATUE_GLB` | `/home/claude/work/band3d/orig/tenger.glb` | 0.83 M triangle gold horse on a green pedestal lettered TENGER / テンゲル ("Tenger"). Used by `kisekae/flat/metal_glb.py` for the Master band wallpaper (第4.149版) |

Loading the bust takes about 35 s and about 1.8 GB of RAM. One render at 780×1688 with ss=2 takes about 25 s and about 2.6 GB at peak, so run one 3D process at a time.

## How the band wallpapers use it (第4.149版)

`kisekae/flat/metal_glb.py` turns the two statues into 780×320 pictures (alpha `a` and colour `srgb`) for `kisekae/flat/metal_run.py`:

- The statue is rendered at 4× (3120×1280) as a G-buffer (`alpha`, `normal`, `pos`, `albedo`, `ao`), shaded in numpy, and then box-downsampled. Shading before downsampling keeps the silhouette free of bright speckles.
- The camera is solved in a short loop so that the silhouette lands in a given span, with its lowest row on the floor line.
- Metalness and roughness are not in the G-buffer. `_gbuf` reads them by rendering once more with `base_tex` swapped for `mr_tex` (and restores it afterwards).
- Silver and Gold: a "polished metal" luminance (a small studio environment reflected about the normal, times the texture luminance and AO) is mapped through a silver or a gold colour ramp. Both use the same model, so the two pictures differ only in colour.
- Master: the model keeps its own colours. Gold parts are metal (tinted reflection), green parts are glossy paint (diffuse plus a weak reflection).

Loading a statue takes about 1.5 s and about 0.7 GB of RAM. One 4× render takes about 3 s.

## How the sd film uses it

`kisekae/flat/shiden_film.py` reads `SD_HORSE`:
- `new` (default): the face and the hoof come from the GLBs.
- `SD_HORSE=old`: the previous r3d SDF horse and `shiden_hoof.py` hoof, which rebuilds the film shipped before 第4.119版 (delete frames 54–113 and 175–205 in `ios/fx_assets/_films/sd` first).

In both modes, timing, camera keys, lights, the eye glow and flare, vapor, cracks, lightning, sparks and lettering are the same code.

- **Face (`shiden_glb.face_glb`)**
  - For every frame it solves a camera so that this model's eye and muzzle land exactly on the old head's eye and muzzle screen positions (`face_marks`). That keeps the same position, scale and head-raise.
  - The head-raise is done by rotating the bust about the eye.
  - It renders a G-buffer (`alpha`, `albedo`, `normal`, `pos`), then relights it with the old purple low-key rig. The strong back rims give the forehead and nose line.
  - The model's own mane replaces the 2D HairBuf mane.
- **Hoof (`shiden_glb.hoof_layer_glb`)**
  - The leg is put in the old hoof's standing frame: sole on the ground, toe forward, same sole size.
  - It is then turned into the cut-in canvas (leg from the left, sole to the right, toe up) and tilted by `SD_HOOF_TILT` (default −15°) so the shin lies like the old one.
  - It uses the old camera (az 34→16, el 7→3, fov 12.6) and gets the old rims plus the burning-shoe ring on the sole.
