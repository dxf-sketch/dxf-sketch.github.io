# Changelog

Important changes only; smaller ones are listed as general bug fixes.

## 1.60.6 — 17 Nov 2026

- Messages show at full width instead of in a narrow column, and on phones over the top of the plan rather than over the panel.
- Photos: the app asks the browser to keep this device’s photos when space runs low, the first time you add one.
- Touch: Saved, Source and the version in the status bar are easier to hit; the closed notes pane no longer catches the keyboard.
- General bug fixes

## 1.60.5 — 17 Nov 2026

- Export: the DXF, the project file and the photos now go out as one .zip, so the project file can’t get left behind or end up in another folder. Open a project file reads the .zip back, photos included. Settings › Where exports go › Project file: In a .zip, Separate or Leave out.
- Laptop: on Windows the program runs without a terminal window; everything is in the page. Projects › Close DXF Sketch stops it, and Projects › On the iPad shows the address to type on the iPad. Starting it again while it runs just opens the page. For troubleshooting, start it with --console.
- General bug fixes

## 1.60.4 — 17 Nov 2026

- Photos: Select several at once, in one room or across the whole project, then move them to another room or delete them together (Select all, too). Undo brings them back.
- General bug fixes

## 1.60.3 — 17 Nov 2026

- Photo angles: when turned on, they show for every room on the floor, not only the selected one (the other rooms’ a little lighter).
- Tap a photo angle on the plan for a small preview: the photo, its number, room and wall, with Open (the full photo viewer) and Go to the room when it belongs to another one.
- General bug fixes

## 1.60.2 — 17 Nov 2026

- Photo wizard: it no longer matters how the device is held. Upright, sideways either way or upside down, with rotation lock on or off, each group of photos is checked against the photos themselves (the texture has to move the way the device turned between them), and turned the right way round if the browser reported it wrongly.
- Photos taken sideways with rotation lock on are shown upright on the marking screen and in the strip; taps stay exact.
- No browser is named in the app’s messages any more.
- General bug fixes

## 1.60.1 — 17 Nov 2026

- Photo wizard: the survey in progress is saved on the device as you go (photos, taps, sizes, tie points). A reload, a crash or closing the app loses nothing: open the wizard again and it carries on where you were. The Walls step shows “Photo wizard · resume…” while one is waiting.
- The saved survey is cleared once the room is drawn, or on Start over; removing a photo removes its saved copy.
- General bug fixes

## 1.60.0 — 17 Nov 2026

- Photo wizard (Settings › Experimental) is now photogrammetry, still on the device with no AI and no internet: take photos all round from one spot and then from a second spot across the room, tap each corner of the room on the photos, and the room is worked out from where they appear. Tie points link overlapping photos automatically, and a bundle adjustment finds the camera, the lens and every point at once; scale comes from one laser length (most accurate), the room height or the camera height.
- Analyzers: tap an analyzer’s two front corners on the photos and the app measures it, tells which way it faces, and suggests the models on file that fit its width; pick one and it is placed against its wall in the plan.
- A clear path through it all: numbered steps for the photos (a ring shows how far round you have gone at each spot) and for the marking, a drawing of where to tap, where each point should be on the next photo, a loupe for precise taps, and a red line wherever a tap disagrees with the rest.
- Doors, windows, passages, outlets, network, water, drains and a ceiling corner can be tapped too; every point shows how well it is pinned down.
- General bug fixes

## 1.59.0 — 16 Nov 2026

- Photo wizard (Settings › Experimental) now measures on the device, with no AI, no API key and no internet: stand in the room, aim the camera’s cross at each wall’s floor line (left part, then right part), turning right from wall to wall, then at doors, windows, passages, outlets, network outlets, water and drains. The motion sensors work out the walls, corners and positions; each wall gets a photo. Scale comes from your camera height, or better from the room height with a Ceiling line marked, or from one laser length of wall 1.
- A live sketch of the room appears as soon as three walls are marked; Undo steps back one mark at a time.
- The Anthropic API key and the photo reading by Claude are gone; a key saved earlier is removed from the device.
- General bug fixes

## 1.58.0 — 16 Nov 2026

- Delete what you select with the Delete or Backspace key: doors, windows, passages, pillars, shafts, beams, services, furniture, equipment, walls, and several items selected together. Undo brings them back.
- A selected beam gets its own bar under the plan, with Delete and Done.
- Tap the logo or DXF Sketch to go home: everything is unselected, open panels close, and the whole plan is shown in 2D. Projects are under ⌘O and the project name.
- General bug fixes

## 1.57.0 — 16 Nov 2026

- Photos: see every photo of the project (Whole project, grouped by room), and go to the previous or next room from the Photos pane with the arrows; tap a room's name to go to it.
- The photo angles button shows a photo with an eye when they are shown, and a crossed-out eye when they are hidden.
- General bug fixes

## 1.56.0 — 16 Nov 2026

- Experimental, in Settings: Photo wizard. Photograph each wall in turn (Walls › Photo wizard) and Claude draws a first draft of the room: walls, doors, windows, passages, pillars, shafts, beams, services and benches. Check it on a preview, pick what to draw, then measure over it: every length shows ≈ until you measure it or Check with laser. Optional room height and one laser length make it much more accurate. Needs your Anthropic API key, which stays on the device; pick Opus, Sonnet or Haiku in Settings.
- The photos from the wizard are kept with the room, tagged to their walls, for the site survey.
- Photo angles are hidden on the sketch until you turn them on.
- The Photos button in the top bar uses the photos icon.
- General bug fixes

## 1.55.1 — 16 Nov 2026

- The photo angles button uses a photo icon instead of a camera.
- General bug fixes

## 1.55.0 — 16 Nov 2026

- Show / hide photo angles on the sketch: a camera button in the tools column (it appears once a photo is pinned on the plan). The site survey still shows them.
- General bug fixes

## 1.54.0 — 16 Nov 2026

- Photos: tap one to open it full screen, then swipe or use the arrows to go through every photo of the project. Each shows its room and wall.
- Move a photo to another room from the viewer (Undo puts it back), or remove it there.
- The Photos panel scrolls when a room has many photos.
- General bug fixes

## 1.53.0 — 16 Nov 2026

- Photos sync across your devices: each photo goes once into a private "DXF Sketch photos" gist on your GitHub, and your other devices download the ones they are missing. Removing a photo or deleting a project removes its photos everywhere. In Settings you can keep photo downloads to Wi-Fi only (where the device says it is on mobile data) or allow mobile data too.
- Clearer headings and descriptions: section headings are larger, and the descriptions under them are a size smaller.
- General bug fixes

## 1.52.0 — 16 Nov 2026

- The site survey PDF is sharper: pages are made at print quality (300 dpi), so text, plans and the 3D views stay crisp when zoomed in or printed.
- Bill of quantities is no longer in Export.
- General bug fixes

## 1.51.0 — 16 Nov 2026

- The Site survey (PDF) button is in colour.
- The site survey is short and to the point: a cover with the general plan, then one page per room with its 2D plan, a 3D view, the essentials (area, height, openings, services, equipment), its checklist and sign-off, and a last page with the checklist for every room and the signatures.
- Signatures are drawn with a finger or pen: sign off a room from its checklist, and sign the survey as surveyor and customer in Export.
- General bug fixes

## 1.50.0 — 16 Nov 2026

- Deleting a project deletes it on all your devices: it comes out of your GitHub backup, and your other devices remove it the next time they sync (Earlier versions keeps a copy).
- Delete buttons have red letters and a red border.
- General bug fixes

## 1.49.0 — 16 Nov 2026

- Steps at the bottom as a flat breadcrumb, like the top bar.
- General bug fixes.

## 1.48.0 — 16 Nov 2026

- Flat top bar, no boxes around boxes.
- Version and scale bar without boxes.
- General bug fixes.

## 1.47.0 — 16 Nov 2026

- cobas 6000 in all seven module combinations.
- General bug fixes.

## 1.46.1 — 16 Nov 2026

- DiaSorin LIAISON XL added.
- General bug fixes.

## 1.46.0 — 16 Nov 2026

- + on every step, reaching every section.
- Walls: add a corner, split a wall, room next door.
- General bug fixes.

## 1.45.0 — 16 Nov 2026

- + menu with categories, then sizes or types.
- No bar above the plan; a small label says what you are placing.
- Less padding on buttons.
- General bug fixes.

## 1.44.0 — 16 Nov 2026

- Compact selection bar: Edit, Select more, ⋯, Delete, ✕.
- General bug fixes.

## 1.43.0 — 16 Nov 2026

- Drag a selection: everything moves together.
- Move furniture and equipment between rooms by dragging or Move to room…
- Bench cabinets and drawers flush with the bench front.
- Room dimensions one size, smaller, regular type, scaling with zoom.
- General bug fixes.

## 1.42.0 — 16 Nov 2026

- + sized like the step buttons; compact Add tiles.
- Cat 6 label.
- General bug fixes.

## 1.41.0 — 16 Nov 2026

- + at the bottom left, in line with the step bar.
- Lighter step bar: number or tick and name.
- General bug fixes.

## 1.40.0 — 16 Nov 2026

- Devices now meet in one shared backup and read all earlier ones.
- Sync now, with last-synced time and project count.
- General bug fixes.

## 1.39.0 — 16 Nov 2026

- Same projects on every device with the same GitHub token, synced room by room.
- No device overwrites newer work from another.
- General bug fixes.

## 1.38.0 — 16 Nov 2026

- Earlier versions: device history and every GitHub backup, opened as copies.
- Restoring a backup never replaces the current project.
- Moving keeps both versions when they differ.
- General bug fixes.

## 1.37.0 — 16 Nov 2026

- New address: dxf-sketch.github.io; the old one hands everything across.
- DXF and project file saved together on iPad and iPhone.
- General bug fixes.

## 1.36.0 — 16 Nov 2026

- Calmer, cleaner look across the app.
- Green ticks for the steps you have filled in.
- Ready for the move to dxf-sketch.github.io.
- General bug fixes.

## 1.35.0 — 16 Nov 2026

- Blue + button on every step: a sheet of large tiles to add rooms, walls, pillars, openings, services, furniture and equipment.
- + turns into Done while adding; pulses on empty steps.
- General bug fixes.

## 1.34.0 — 16 Nov 2026

- How-to hints as messages and ⓘ instead of always on screen.
- Guidance moved to tooltips.
- General bug fixes.

## 1.33.0 — 16 Nov 2026

- Site workflow checked end to end in the new order.
- Atellica configurations read left to right from the front.
- Tidier panels and step bar.
- General bug fixes.

## 1.32.0 — 16 Nov 2026

- Pillars before Openings.
- Steps numbered 1 to 8 in circles.
- General bug fixes.

## 1.31.0 — 16 Nov 2026

- New line icons for every piece of equipment and analyzer discipline.
- General bug fixes.

## 1.30.0 — 16 Nov 2026

- Atellica Solution with Rack Handler.
- CN and CS analyzers listed under their own names.
- General bug fixes.

## 1.29.1 — 16 Nov 2026

- IM 1300 / 1600 as one component.
- General bug fixes.

## 1.29.0 — 16 Nov 2026

- One Decapper, position 1, 2 or 3.
- Sample Handler or Rack Handler always before the analyzers.
- Room dimensions grow when zooming in; pillar and shaft measurements match them.
- General bug fixes.

## 1.28.0 — 16 Nov 2026

- Atellica configuration: Solution (CH and IM analyzers) or CI, one per configuration.
- CI with Rack Handler, or for the Sample Handler with Sealer and Decapper (AIA).
- Decapper after the Sample Handler adds no length.
- General bug fixes.

## 1.27.0 — 16 Nov 2026

- Atellica line-up follows the Sealer and Decapper position rules.
- Line-up placed anywhere in the room, nudged to the nearest place where it fits.
- Whole line-up selects all its pieces.
- General bug fixes.

## 1.26.0 — 16 Nov 2026

- Atellica line-up builder: Solution or CI, with left and right turns (L or U).
- Atellica Decapper and Sealer added, under Automation.
- General bug fixes.

## 1.25.0 — 16 Nov 2026

- Added CLINITEK Advantus, Atellica UAS 60, BN II, cobas 6000, cobas e 411, Hb NEXT and MAGLUMI X3, X6, 2000 Plus.
- General bug fixes.

## 1.24.0 — 16 Nov 2026

- CN-3000/6000 (± SA-90), NEPH 630 and CLINITEK Novus added; CS-5100/2500 under Siemens.
- COAG 360 removed.
- Custom size analyzers in their own tab.
- General bug fixes.

## 1.23.0 — 16 Nov 2026

- Analyzers tab by manufacturer (Siemens, Roche, Abbott, Others); equipment kept separate.
- Atellica HEMA 530 and 520 added.
- Recently used removed from the library.
- General bug fixes.

## 1.22.1 — 16 Nov 2026

- Siemens Healthineers models first in every group.
- General bug fixes.

## 1.22.0 — 16 Nov 2026

- Siemens Healthineers analyzers in the library: Atellica, Dimension, ADVIA, IMMULITE, Atellica HEMA, COAG 360 and Atellica 1500.

## 1.21.0 — 16 Nov 2026

- New look on iPad and computers: full-screen plan with floating bars, a step dock at the bottom and a floating side card.
- Messages no longer catch taps meant for the plan.
- General bug fixes.

## 1.20.0 — 16 Nov 2026

- Measure from a photo on the device (no AI): wall length, doors and windows from perspective.
- Check with laser: wall by wall, then each opening; measured values are marked.
- The Claude photo plan is removed.

## 1.19.0 — 16 Nov 2026

- Revisions: issue a revision and see exactly what changed since, in the app and in the Site Survey.

## 1.18.0 — 16 Nov 2026

- Select several items: same height, space evenly, butt together, move by a distance, delete.
- General bug fixes.

## 1.17.0 — 16 Nov 2026

- Bill of quantities in the app (copy to Excel) and in the Site Survey.
- General bug fixes.

## 1.16.0 — 16 Nov 2026

- Photo pins on the plan and in the Site Survey.
- General bug fixes.

## 1.15.0 — 16 Nov 2026

- Analyzer models library (biochemistry, immunology, hematology, coagulation, urinalysis) at published sizes, with typical services.
- General bug fixes.

## 1.14.0 — 16 Nov 2026

- Tap selects, double tap (or Edit) opens the details.
- Undo and redo on the toolbar beside the plan.
- Photos and Notes are separate.
- What's new shows the last five versions.
- Quick taps along a wall keep adding.
- General bug fixes.

## 1.13.1 — 16 Nov 2026

- Selecting fixed: symbols and wall strips no longer take taps meant for furniture.
- Taps with a small wobble select instead of moving.
- General bug fixes.

## 1.13.0 — 16 Nov 2026

- Each section selects only its own things; everything else is locked and faded.
- Wall cabinets easy to select.
- General bug fixes.

## 1.12.3 — 16 Nov 2026

- Site Survey PDF: no issues list, one rooms and services table, one page per room.
- General bug fixes.

## 1.12.2 — 16 Nov 2026

- Selecting fixed: a tap on anything selects it unless you are adding things.
- Shorter Site Survey PDF.
- General bug fixes.

## 1.12.1 — 16 Nov 2026

- Add photos already on the device, not only new ones.
- Photos button in the top bar and in the Room panel.
- General bug fixes.

## 1.12.0 — 16 Nov 2026

- Site Survey PDF rebuilt as a professional survey report: plans to scale with title block, rooms and services schedules, a data sheet per room, issues and actions, and sign-off.
- General bug fixes.

## 1.11.1 — 16 Nov 2026

- The tool stays picked: each tap adds another door, outlet, pillar or piece of furniture.
- Clearer hints and messages.
- General bug fixes.

## 1.11.0 — 16 Nov 2026

- Placing furniture over benches, outlets and beams works; wall cabinets stay on the wall, cabinets under the bench.
- Wall cabinets and under-bench cabinets see-through on the plan.
- Backups and live links paced and retried so GitHub limits no longer stop them.
- Site survey in title case; Room schedule renamed Rooms Overview.
- Experimental: plan from photos (Settings).

## 1.10.3 — 15 Nov 2026

- Greek translation completed and reworded.
- General bug fixes.

## 1.10.2 — 15 Nov 2026

- General bug fixes.

## 1.10.1 — 15 Nov 2026

- New project wizard: floor, first room and a plan to start from.

## 1.10.0 — 15 Nov 2026

- Library to add furniture and equipment: tiles by group, search, recently used.
- New project asks for site, initials and version.

## 1.9.6 — 15 Nov 2026

- Equipment: chemicals cabinet.

## 1.9.5 — 15 Nov 2026

- Delete this project from the project menu.

## 1.9.4 — 15 Nov 2026

- General bug fixes.

## 1.9.3 — 15 Nov 2026

- Several projects open at once; cycle through them from the breadcrumb (⇄) or with Alt+→ / Alt+←.
- Water system removed from Equipment.
- General bug fixes.

## 1.9.2 — 15 Nov 2026

- Share redesigned; send by email or iMessage.

## 1.9.1 — 15 Nov 2026

- Equipment reorganised: bench items, floor equipment as their own items (fridge, freezer, fume hood, biosafety cabinet, water system, R/O, PTS, UPS) and Analyzers.

## 1.9.0 — 15 Nov 2026

- English or Greek interface (Settings › General › Language).
- Footer simplified; the Key is in the right-hand toolbar.
- Clearer overlapping-openings warning.

## 1.8.9 — 15 Nov 2026

- General bug fixes.

## 1.8.8 — 15 Nov 2026

- Consistent type scale throughout.
- Step tabs: tap to open the panel, tap again to fold it away.

## 1.8.7 — 15 Nov 2026

- Footer rethought: room and area, save and backup status, made-with icons, source, version.

## 1.8.6 — 15 Nov 2026

- Tidier footer with made-with tags, source link, version and ©.

## 1.8.5 — 15 Nov 2026

- Splash screen on opening; footer shows what it is made with and links to the source.

## 1.8.4 — 15 Nov 2026

- Save and Save as in the project menu; DXF Sketch at the top left opens Home.

## 1.8.3 — 15 Nov 2026

- General bug fixes.

## 1.8.2 — 15 Nov 2026

- The custom-size Equipment piece is now called Analyzer.

## 1.8.1 — 15 Nov 2026

- Equipment: PTS replaces the sample rack, UPS added (both as DXF blocks); reverse osmosis shown as R/O.
- Hints show as a short message instead of widening the choices bar.

## 1.8.0 — 15 Nov 2026

- Breadcrumb: project › floor › room, with a project menu to switch sites; departments show only when a floor has more than one.

## 1.7.8 — 15 Nov 2026

- General bug fixes.

## 1.7.7 — 15 Nov 2026

- Power boards stay out of the walls, against the outer line of the hatch.

## 1.7.6 — 15 Nov 2026

- Power boards: tap near any wall, inside or outside, or drag to any wall and side.

## 1.7.5 — 15 Nov 2026

- General bug fixes.

## 1.7.4 — 15 Nov 2026

- Wall hatch scale 20 by default.
- Smaller room dimensions and names on screen.

## 1.7.3 — 15 Nov 2026

- Removed Compare visits, Room schedule (CSV) and Plan to scale from Export.
- General bug fixes.

## 1.7.2 — 15 Nov 2026

- Power boards snap to either side of a wall (this room or the other side).

## 1.7.1 — 15 Nov 2026

- Power boards in any size (room, sub, distribution and main boards to start from); each size is its own DXF block.

## 1.7.0 — 15 Nov 2026

- Services: power board with its breakers; drawn to scale, in 3D, on elevations, in the schedule and survey, and in the DXF as the block Power Board.
- Computers save through a Save dialog (site survey PDF included); phones and tablets keep the share sheet.
- Links are copied instead of going through the system share sheet.

## 1.6.3 — 15 Nov 2026

- Phones: one-row header, and the floor, laboratory and room switches fit the screen.
- General bug fixes.

## 1.6.2 — 15 Nov 2026

- 3D: empty floors below yours get the outside walls and windows of your floor.

## 1.6.1 — 15 Nov 2026

- 3D shows the floors below yours, even empty ones, as a named stack.

## 1.6.0 — 15 Nov 2026

- The DXF export saves the project file (.json) next to it, under the same name, to open later and carry on.
- Opening a project file already on the device asks whether to carry on from it or open a copy.
- On computers, the project file in the export folder is kept up to date as you work.

## 1.5.0 — 15 Nov 2026

- Where exports go: ask each time (share sheet), straight into a folder you pick (DXF by default, OneDrive folders too; Chrome and Edge on computers), or Downloads.

## 1.4.3 — 15 Nov 2026

- Saving through the share sheet no longer adds a Text.txt next to the file.
- General bug fixes.

## 1.4.2 — 15 Nov 2026

- Editing together: when two people change the same room, you are asked which version to keep instead of the later change winning.

## 1.4.1 — 15 Nov 2026

- App icons are now SVG.
- General bug fixes.

## 1.4.0 — 15 Nov 2026

- Editing together: people you share a live link with can edit too, each with their own GitHub token; changes are combined room by room and appear for everyone within a minute or so.

## 1.3.5 — 15 Nov 2026

- Settings redesigned in the style of iOS: grouped rows with switches and segmented controls.

## 1.3.4 — 15 Nov 2026
- Wording: “works offline, no internet connection needed (Wi-Fi or mobile data)” instead of “works with no signal”.
- General bug fixes.

## 1.3.3 — 15 Nov 2026
- 3D: door, window and passage frames sit flush within the wall instead of poking through its faces, and passages get a proper frame like a door's, without the leaf.

## 1.3.2 — 15 Nov 2026
- 3D shows doors, windows and passages properly: doors with their frame and the leaf (or both leaves of a double door) standing open the way they swing on the plan; windows with a frame all round, a mullion on wide ones, glass and an inside sill; passages with a lining round the opening.

## 1.3.1 — 15 Nov 2026
- DXF: each beam is now one closed dashed polyline (its outline, ends on the wall faces) instead of two separate lines, so it can be picked, moved and stretched in AutoCAD as one object. The dash pattern runs continuously round its corners.

## 1.3.0 — 15 Nov 2026
- Ceiling beams (in Pillars): pick Beam, tap the wall where it starts and then the wall opposite; with Ortho on it runs square to the first wall. Give it its width and underside height. It is drawn as two dashed lines with “u/s” and its height, hangs from the ceiling in 3D, shows in section on the wall elevations, and the site survey gives each room's lowest clear height and warns when tall furniture stands under a lower beam.
- DXF: beams go on a new layer, Room Beams, colour 125 with a dashed linetype, with the text “BEAM 300 u/s +2.40”.

## 1.2.2 — 14 Nov 2026
- Floors have a number: set which floor you are on (for example the 3rd), and the ground, 1st and 2nd floors are listed below it, empty, until you work on them. The floor you pick is the one you work on; floors are listed top to bottom, can be added above or below, and their names follow their number unless you rename them.
- General bug fixes.

## 1.2.1 — 14 Nov 2026
- Site survey as a PDF: plan, room schedule, each room with its services, needs, checklist, notes and photos, page-numbered on A4. Names in any language print correctly.
- Export fits its panel: the buttons wrap onto two columns, with no sideways scrolling.

## 1.2.0 — 14 Nov 2026
- Floors: a hospital has floors, each with its laboratories (the floor button next to Laboratory). The DXF puts each floor in a row of its own, named, one above the other.
- Wall elevations: any wall seen from inside the room, with doors, windows, pillars, furniture, equipment and services at their heights and a chain of dimensions; print or save it as PDF.
- Heights: services have a height above the floor (shown in 3D, elevations and the survey), windows a sill and height, and rooms an optional false ceiling.
- Equipment needs: PCs, printers, sinks, centrifuges, reverse osmosis and the named equipment know which outlets, network points, water and drains they need. Equipment and Services say what is still missing.
- Templates: save a room's furniture, equipment and services and drop them into another room in one tap.
- Open an existing DXF as a faint underlay to trace over (File menu or the laboratory menu). It is not exported.
- Compare with an earlier visit: room by room, what changed in area, walls, openings, services and furniture.
- Site checklist per room (measured, photographed, services counted, signed off), shown in the room list and the site survey. The site report is now called the site survey.
- General bug fixes.

## 1.1.0 — 14 Nov 2026
- Backups: with a GitHub token, every project is backed up as you work into a private Gist on your account (photos stay on the device). Projects shows when each was last backed up, and Settings can back up everything at once or restore a project from the backup.
- Storage in Settings: how much room your projects and photos take on this device, with a warning before it fills up.
- Plan to scale (Export): the plan at 1:50 on A4 or A3, or 1:100 if it will not fit, with a title block and scale bar, ready to print or save as PDF.
- Every release is now checked automatically first: the app opens on tablet, portrait and phone sizes, every step and 3D draw, and the DXF is checked for errors, layers, colours and the 0,0 origin.
- General bug fixes.

## 1.0.1 — 14 Nov 2026
- Tap a room's name on the plan to open its details; tap it again to close them and go back to what you were doing. A second tap on anything selected (a wall, door, pillar, outlet or piece of furniture) lets it go.
- Devices still on the old 3.x versions now update to this version by themselves.
- General bug fixes.

## 1.0.0 — 14 Nov 2026
First release.

- Laboratories and rooms: several laboratories per hospital, each with its rooms; rooms can sit next door to each other and share walls. Each room has a name (and one in another language), Room#, height, wall thickness and fill.
- Walls: sketch with Apple Pencil or a finger, start from a rectangle or an L, or walk the room wall by wall with the laser meter. Tap any length or angle to change it; rooms always stay closed.
- Openings, pillars and shafts: doors (single or double, with unequal leaves), windows and passages; pillars and shafts that snap to walls, corners and each other. The floor area leaves them out.
- Services: electrical outlets (1P, 1P UPS, 3P UPS), network outlets (RJ45), water, drain and air, on walls, pillars or shafts.
- Furniture and equipment as your own AutoCAD blocks: benches at any size, cabinets, drawers, chairs, PCs, sinks, printers, centrifuges, reverse osmosis and named equipment. Items on a bench line up with each other, and a selected item shows only the gaps to its neighbours.
- DXF for AutoCAD 2018, millimetres 1:1: your layers, hatched walls, dimensions in your STYLE[inch] style, the Area label, doors, windows, services in their own colours and furniture and equipment in colour 125, all starting from 0,0,0, with a north arrow.
- 3D view with low, cut-away or full-height walls.
- North from the compass along the first wall, or by hand; one tap squares the laboratory up and turns it landscape or portrait.
- Sharing: a short live link that always opens the latest version, sent by email to one person or to anyone, with a green dot for who has it open; or a frozen copy inside a link.
- Files and reports: New, Open, Save and Save as; project files; a printable site report, a plan picture and a room schedule (CSV); photos and notes per room.
- Works offline on any device once added to the Home Screen; light and dark themes; metric or feet and inches; undo and redo; updates from About.
