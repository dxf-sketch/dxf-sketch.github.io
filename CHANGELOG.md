# Changelog

Important changes only; smaller ones are listed as general bug fixes.

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
