/**
 * fill_sudoku.jsx — InDesign ExtendScript
 *
 * Loads a dated sudoku puzzle pair from JSON and builds the full
 * newspaper layout (DAGENS SUDOKU) on the active page.
 *
 * Usage: Window → Utilities → Scripts → fill_sudoku.jsx
 *
 * Setup: Edit CONFIG below to match your puzzle folder path and styling.
 */

// ============================================================
// CONFIGURATION — edit these to match your setup
// ============================================================
var CONFIG = {
    // Path to the folder containing the date JSON files (e.g. 2026-04-17.json)
    // Windows: "C:\\Sudoku\\puzzles\\"
    // Mac: "/Users/yourname/sudokugen/puzzles/"
    puzzleFolder: "C:\\Users\\SivertBjellandSevatd\\Downloads\\sudokugen-main\\puzzles\\",

    // Font for digits (falls back to Helvetica if not found)
    fontName: "Williams Bold",

    // Grid line color [R, G, B] 0-255
    lineColor: [192, 31, 31],

    // Main puzzle grid dimensions
    gridWidthMM: 55,
    cellFontSize: 11,        // pt
    thinLine: 0.5,           // pt — cell borders
    thickLine: 1.5,          // pt — box borders

    // Solution grid dimensions
    solutionWidthMM: 22,
    solutionFontSize: 4.5,   // pt
    solutionThinLine: 0.25,
    solutionThickLine: 0.8,

    // Layout spacing (mm)
    headerFontSize: 14,      // pt — "DAGENS SUDOKU"
    labelFontSize: 8,        // pt — "MIDDELS", "VANSKELIG"
    gapBetweenGrids: 6,      // mm
    solutionGap: 4,          // mm — between the two solution grids
};

// ============================================================
// MAIN
// ============================================================
(function () {
    if (app.documents.length === 0) {
        alert("Please open a document first.");
        return;
    }

    // Ask for date
    var today = getCurrentDateString();
    var dateStr = prompt("Enter puzzle date (YYYY-MM-DD):", today);
    if (!dateStr) return;

    // Load JSON
    var jsonPath = CONFIG.puzzleFolder + dateStr + ".json";
    var jsonFile = new File(jsonPath);
    if (!jsonFile.exists) {
        alert("File not found:\n" + jsonPath + "\n\nRun kukoku.exe to generate puzzles first.");
        return;
    }

    jsonFile.open("r");
    jsonFile.encoding = "UTF-8";
    var raw = jsonFile.read();
    jsonFile.close();

    var data = parseJSON(raw);
    if (!data || !data.middels || !data.vanskelig) {
        alert("Invalid puzzle file: " + jsonPath);
        return;
    }

    // Set up
    var doc = app.activeDocument;
    var page = doc.pages[doc.pages.length - 1]; // use last page
    doc.viewPreferences.horizontalMeasurementUnits = MeasurementUnits.MILLIMETERS;
    doc.viewPreferences.verticalMeasurementUnits = MeasurementUnits.MILLIMETERS;

    var lineColor = getOrCreateColor(doc, "Sudoku Red", CONFIG.lineColor);
    var font = findFont(CONFIG.fontName);

    // Page geometry
    var pageBounds = page.bounds; // [top, left, bottom, right]
    var pageWidth = pageBounds[3] - pageBounds[1];
    var centerX = pageBounds[1] + pageWidth / 2;
    var gridW = CONFIG.gridWidthMM;
    var gridLeft = centerX - gridW / 2;
    var cursorY = pageBounds[0] + 8; // start 8mm from top

    // --- "DAGENS SUDOKU" header ---
    cursorY = placeHeader(page, "DAGENS SUDOKU", gridLeft, cursorY, gridW,
                          CONFIG.headerFontSize, font, lineColor);
    cursorY += CONFIG.gapBetweenGrids;

    // --- MIDDELS grid ---
    placeLabel(page, "MIDDELS", gridLeft - 10, cursorY, gridW,
               CONFIG.labelFontSize, font);
    cursorY = placeGrid(page, data.middels.grid, gridLeft, cursorY, gridW,
                        CONFIG.cellFontSize, font, lineColor, false);
    cursorY += CONFIG.gapBetweenGrids;

    // --- VANSKELIG grid ---
    placeLabel(page, "VANSKELIG", gridLeft - 10, cursorY, gridW,
               CONFIG.labelFontSize, font);
    cursorY = placeGrid(page, data.vanskelig.grid, gridLeft, cursorY, gridW,
                        CONFIG.cellFontSize, font, lineColor, false);
    cursorY += CONFIG.gapBetweenGrids;

    // --- "LØSNINGER" header ---
    cursorY = placeHeader(page, "LØSNINGER", gridLeft, cursorY, gridW,
                          CONFIG.labelFontSize, font, lineColor);
    cursorY += 2;

    // --- Two small solution grids side by side ---
    var solW = CONFIG.solutionWidthMM;
    var totalSolW = solW * 2 + CONFIG.solutionGap;
    var solLeft = gridLeft + (gridW - totalSolW) / 2;

    placeGrid(page, data.middels.solution, solLeft, cursorY, solW,
              CONFIG.solutionFontSize, font, lineColor, true);
    placeGrid(page, data.vanskelig.solution, solLeft + solW + CONFIG.solutionGap,
              cursorY, solW, CONFIG.solutionFontSize, font, lineColor, true);

    alert("Sudoku for " + dateStr + " placed!\n\n" +
          "MIDDELS: SE " + data.middels.se_rating + ", " + data.middels.clue_count + " clues\n" +
          "VANSKELIG: SE " + data.vanskelig.se_rating + ", " + data.vanskelig.clue_count + " clues");
})();

// ============================================================
// GRID PLACEMENT
// ============================================================
function placeGrid(page, gridData, left, top, widthMM, fontSize, font, color, isSolution) {
    var cellSize = widthMM / 9;
    var thinW = isSolution ? CONFIG.solutionThinLine : CONFIG.thinLine;
    var thickW = isSolution ? CONFIG.solutionThickLine : CONFIG.thickLine;

    // Create text frame for the table
    var frameBounds = [top, left, top + widthMM, left + widthMM];
    var frame = page.textFrames.add({
        geometricBounds: frameBounds
    });
    frame.textFramePreferences.insetSpacing = [0, 0, 0, 0];

    // Insert table
    frame.insertionPoints[0].contents = "";
    var table = frame.insertionPoints[0].tables.add({
        headerRowCount: 0,
        bodyRowCount: 9,
        columnCount: 9
    });

    // Size columns and rows
    for (var c = 0; c < 9; c++) {
        table.columns[c].width = ptFromMM(cellSize);
    }
    for (var r = 0; r < 9; r++) {
        table.rows[r].height = ptFromMM(cellSize);
    }

    // Style cells
    for (var r = 0; r < 9; r++) {
        for (var c = 0; c < 9; c++) {
            var cell = table.rows[r].cells[c];

            // Set digit
            var val = gridData[r][c];
            cell.contents = (val === 0) ? "" : String(val);

            // Center text
            cell.texts[0].justification = Justification.CENTER_ALIGN;
            cell.verticalJustification = VerticalJustification.CENTER_ALIGN;

            // Font
            try {
                cell.texts[0].appliedFont = font;
                cell.texts[0].pointSize = fontSize;
            } catch (e) {
                cell.texts[0].pointSize = fontSize;
            }

            // Borders — thin by default
            setCellBorders(cell, thinW, color);

            // Thick borders on box boundaries
            if (r % 3 === 0) setCellBorderTop(cell, thickW, color);
            if (r === 8) setCellBorderBottom(cell, thickW, color);
            if (c % 3 === 0) setCellBorderLeft(cell, thickW, color);
            if (c === 8) setCellBorderRight(cell, thickW, color);
        }
    }

    return top + widthMM;
}

// ============================================================
// CELL BORDER HELPERS
// ============================================================
function setCellBorders(cell, weight, color) {
    var sides = ["topEdgeStrokeWeight", "bottomEdgeStrokeWeight",
                 "leftEdgeStrokeWeight", "rightEdgeStrokeWeight"];
    var colorSides = ["topEdgeStrokeColor", "bottomEdgeStrokeColor",
                      "leftEdgeStrokeColor", "rightEdgeStrokeColor"];
    for (var i = 0; i < sides.length; i++) {
        cell[sides[i]] = weight;
        cell[colorSides[i]] = color;
    }
}

function setCellBorderTop(cell, weight, color) {
    cell.topEdgeStrokeWeight = weight;
    cell.topEdgeStrokeColor = color;
}
function setCellBorderBottom(cell, weight, color) {
    cell.bottomEdgeStrokeWeight = weight;
    cell.bottomEdgeStrokeColor = color;
}
function setCellBorderLeft(cell, weight, color) {
    cell.leftEdgeStrokeWeight = weight;
    cell.leftEdgeStrokeColor = color;
}
function setCellBorderRight(cell, weight, color) {
    cell.rightEdgeStrokeWeight = weight;
    cell.rightEdgeStrokeColor = color;
}

// ============================================================
// TEXT PLACEMENT
// ============================================================
function placeHeader(page, text, left, top, width, fontSize, font, color) {
    // Spaced-out letters
    var spaced = text.split("").join(" ");
    var height = fontSize * 0.5;  // mm approx
    var frame = page.textFrames.add({
        geometricBounds: [top, left, top + height, left + width]
    });
    frame.contents = spaced;
    frame.texts[0].justification = Justification.CENTER_ALIGN;
    frame.texts[0].pointSize = fontSize;
    try { frame.texts[0].appliedFont = font; } catch (e) {}
    frame.textFramePreferences.insetSpacing = [0, 0, 0, 0];
    frame.textFramePreferences.autoSizingType = AutoSizingTypeEnum.HEIGHT_ONLY;
    return top + height + 1;
}

function placeLabel(page, text, left, top, gridWidth, fontSize, font) {
    // Vertical rotated label on the left side of the grid
    var spaced = text.split("").join(" ");
    var labelHeight = 4;  // mm width of label frame
    var frame = page.textFrames.add({
        geometricBounds: [top, left, top + gridWidth, left + labelHeight]
    });
    frame.contents = spaced;
    frame.texts[0].justification = Justification.CENTER_ALIGN;
    frame.texts[0].pointSize = fontSize;
    try { frame.texts[0].appliedFont = font; } catch (e) {}
    frame.textFramePreferences.insetSpacing = [0, 0, 0, 0];
    // Rotate text 90 degrees by rotating the frame
    frame.rotationAngle = 90;
    // Reposition after rotation
    frame.move([left, top]);
}

// ============================================================
// UTILITIES
// ============================================================
function getCurrentDateString() {
    var d = new Date();
    var yyyy = d.getFullYear();
    var mm = String(d.getMonth() + 1);
    if (mm.length < 2) mm = "0" + mm;
    var dd = String(d.getDate());
    if (dd.length < 2) dd = "0" + dd;
    return yyyy + "-" + mm + "-" + dd;
}

function getOrCreateColor(doc, name, rgb) {
    try {
        return doc.colors.itemByName(name);
    } catch (e) {}
    try {
        var c = doc.colors.add({
            name: name,
            model: ColorModel.PROCESS,
            space: ColorSpace.RGB,
            colorValue: rgb
        });
        return c;
    } catch (e) {
        return doc.swatches.itemByName("Black");
    }
}

function findFont(name) {
    try {
        return app.fonts.itemByName(name);
    } catch (e) {}
    // Try partial match
    for (var i = 0; i < app.fonts.length; i++) {
        if (app.fonts[i].name.indexOf(name) >= 0) {
            return app.fonts[i];
        }
    }
    // Fallback
    try { return app.fonts.itemByName("Helvetica"); } catch (e) {}
    return app.fonts[0];
}

function ptFromMM(mm) {
    return mm * 2.834645669;
}

// Simple JSON parser for ExtendScript (no native JSON.parse)
function parseJSON(str) {
    try {
        return eval("(" + str + ")");
    } catch (e) {
        return null;
    }
}
