import alarmart as a

a.new_scene("StyleGuide")
names = []
for index, color in enumerate(list(a.PALETTE)[:18]):
    name = "Palette_" + color
    a.begin(name, "Materials")
    a.box("ColorChip", (0, 0, 0.1), (0.75, 0.6, 0.2), color, bevel=0.04)
    a.text("Label", color.upper(), (0, -0.32, 0.08), 0.07, "Navy")
    names.append(name)
a.arrange(names, 6, (1.0, 1.0))
a.studio_floor((2.5, 1), 7)
a.camera((2.5, 0.8, 0), (4, -7, 9), 7.8)
a.save_library()
print("WARM_PALETTE_CREATED", len(names), "flat colors; no downloaded textures")
