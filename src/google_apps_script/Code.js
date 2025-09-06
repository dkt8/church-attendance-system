// === QR Attendance Script - V2.3.0 ===

// Global in-memory caches for faster repeated lookups
let _masterMap = null;  // Map: normalizedName → [sheetName, row]

/**
 * doGet(e)
 * - Serves Scanner.html UI if no 'name' param.
 * - Always uses batch async mode for optimal performance
 */
function doGet(e) {
  if (!e?.parameter?.name) {
    return HtmlService
      .createHtmlOutputFromFile("Scanner")
      .setTitle("QR Code Scanner");
  }

  try {
    // Direct synchronous processing - no more async triggers
    return ContentService
      .createTextOutput(logScan(e.parameter.name));
  } catch (err) {
    return ContentService
      .createTextOutput("Error: " + err.message);
  }
}

/**
 * getSpreadsheetUrl()
 * - Returns the URL of the current spreadsheet for the View button.
 */
function getSpreadsheetUrl() {
  return SpreadsheetApp.getActive().getUrl();
}

/**
 * logScan(data)
 * - Main function to record attendance quickly.
 * - New format: "Name ClassName" e.g. "Giuse Trần Hoàng Nguyên Khôi c1"
 */
function logScan(data) {
  // data = " Giuse Trần  Hoàng   Nguyên Khôi c1 ";
  console.log(`logScan start: ${data}`);

  // data = ["Giuse", "Trần", "Hoàng", "Nguyên", "Khôi", "c1"]
  const parts = data.trim().split(/\s+/);

  const className = parts.pop(); // c1
  const nameOnly = parts.join(" "); // "Giuse Trần Hoàng Nguyên Khôi"
  const normalized = normalize(nameOnly); // "giusetranhoangnguyenkhoi"

  // console.log(`Parsed: name="${nameOnly}", class="${className}", normalized="${normalized}"`);

  const masterMap = getMasterMap();
  if (!(normalized in masterMap)) {
    console.log(`Return error: Name not in masterMap: ${normalized}`);
    return `Error: "${nameOnly}" not found in Master map.`;
  }

  // Normalize sheet name to first + last character, lowercase (e.g. "Chiên 1" → "c1")
  const [sheetName, row] = masterMap[normalized];
  const normalizedSheetName = (sheetName.charAt(0) + sheetName.charAt(sheetName.length - 1)).toLowerCase();

  // Validate that the class matches
  if (normalizedSheetName !== className) {
    console.log(`Return error: Class mismatch. Expected ${normalizedSheetName}, got ${className}`);
    return `Error: "${nameOnly}" belongs to ${normalizedSheetName}, not ${className}.`;
  }

  // Validate the sheet
  const sheet = SpreadsheetApp.getActive().getSheetByName(sheetName);
  if (!sheet) {
    console.log(`Return error: Sheet missing: ${sheetName}`);
    return `Error: Sheet "${sheetName}" not found.`;
  }

  const now = new Date();
  const hh = String(now.getHours()).padStart(2, "0");
  const mm = String(now.getMinutes()).padStart(2, "0");
  const ss = String(now.getSeconds()).padStart(2, "0");
  const currentTime = `${hh}:${mm}:${ss}`;

  // Simple: Find today's column directly (no complex caching needed)
  const baseCol = findTodayColumn(sheet);
  if (!baseCol) {
    console.log(`Return error: No date column for today`);
    return `Error: No matching column for today's date.`;
  }

  if (currentTime >= "09:10:00" && currentTime < "10:00:00") {
    console.log(`Return skipped: Time within skip window: ${currentTime}`);
    return `Skipped: No attendance marked between 09:10 and 10:00 for ${nameOnly}`;
  }

  const col = (currentTime >= "10:00:00") ? baseCol + 1 : baseCol;
  const status = (currentTime < "09:00:00") ? "X"
    : (currentTime < "09:10:00") ? "T"
      : (currentTime < "12:00:00") ? "X"
        : "O";

  sheet.getRange(row, col).setValue(status);
  console.log(`Checked in ${nameOnly} → sheet:${sheetName}, row:${row}, col:${col}, status:${status}`);

  const successMsg = `Success: ${nameOnly} (${className}) checked in at ${hh}:${mm}:${ss}.`;
  console.log(`Return success: ${successMsg}`);
  return successMsg;
}

/**
 * findTodayColumn(sheet)
 * - Simple function to find today's TL column
 * - Pattern: dates every 2 columns starting from column 5
 */
function findTodayColumn(sheet) {
  const today = new Date();
  // Set today to start of day for fair comparison
  today.setHours(0, 0, 0, 0);

  console.log(`Today object: ${today}`);

  // Get just the header row with dates
  const headerRow = sheet.getRange(9, 1, 1, sheet.getLastColumn()).getValues()[0];

  // Check every 2 columns starting from column 5 (index 4)
  for (let idx = 4; idx < headerRow.length; idx += 2) {
    const cell = headerRow[idx];
    console.log(`Column ${idx + 1}: ${cell}`);

    if (cell instanceof Date) {
      // Set cell date to start of day for fair comparison
      const cellDate = new Date(cell);
      cellDate.setHours(0, 0, 0, 0);

      console.log(`Comparing dates: today=${today.getTime()} vs cell=${cellDate.getTime()}`);

      // If today is less than or equal to cell date (incoming sunday), this is our column
      if (today.getTime() <= cellDate.getTime()) {
        console.log(`Match found! Returning column ${idx + 1}`);
        return idx + 1;
      }
    }
  }

  return null; // No suitable date column found
}

/**
 * normalize(text)
 * - Removes accents, whitespace, and lowercases the input.
 */
function normalize(text) {
  return text.trim().toLowerCase()
    .normalize('NFD')
    .replace(/đ/g, 'd')
    .replace(/[\u0300-\u036f\s]/g, '');
}

/**
 * buildAndCacheMasterMap()
 * - Reads the "Master" sheet and caches name→[sheet,row] map.
 */
function buildAndCacheMasterMap() {
  const ms = SpreadsheetApp.getActive().getSheetByName('Master');
  const data = ms.getDataRange().getValues();
  const map = {};
  data.slice(1).forEach(r => {
    const [orig, sh, rn] = r;
    if (orig) {
      map[normalize(orig)] = [sh, rn];
    }
  });
  CacheService.getScriptCache().put('masterMap', JSON.stringify(map), 6 * 60 * 60);
  _masterMap = map;
}

/**
 * getMasterMap()
 * - Returns in-memory or cached masterMap, building if needed.
 */
function getMasterMap() {
  if (_masterMap) return _masterMap;
  const cache = CacheService.getScriptCache();
  let raw = cache.get('masterMap');
  if (!raw) {
    buildAndCacheMasterMap();
    raw = cache.get('masterMap');
  }
  if (!raw) throw new Error('Master map could not be loaded.');
  _masterMap = JSON.parse(raw);
  return _masterMap;
}

/**
 * buildMasterSheet()
 * - Collects all student data from class sheets and adds to Master sheet
 * - Format: Normalized Name | Sheet Name | Row Number
 */
function buildMasterSheet() {
  const ss = SpreadsheetApp.getActive();

  // Get or create Master sheet
  let masterSheet = ss.getSheetByName('Master');
  if (!masterSheet) {
    masterSheet = ss.insertSheet('Master');
  } else {
    masterSheet.clear();
  }

  // Add headers
  masterSheet.getRange(1, 1, 1, 3).setValues([
    ['Normalized Name', 'Sheet Name', 'Row Number']
  ]);

  // Collect data from all sheets
  const allData = [];
  const sheets = ss.getSheets();

  sheets.forEach(sheet => {
    const sheetName = sheet.getName();

    const data = sheet.getDataRange().getValues();

    // Process all rows, skip non-student rows in the loop
    for (let i = 0; i < data.length; i++) {
      const row = data[i];
      const studentNumber = row[0];

      // Skip if first column is not a positive integer (not student data)
      if (!studentNumber || typeof studentNumber !== 'number' || !Number.isInteger(studentNumber) || studentNumber <= 0) {
        continue;
      }

      const saintName = (row[1] || "").toString().trim();
      const firstName = (row[2] || "").toString().trim();
      const lastName = (row[3] || "").toString().trim();

      if (saintName || firstName || lastName) {
        const fullName = `${saintName} ${firstName} ${lastName}`.trim();
        const normalizedName = normalize(fullName);

        if (normalizedName) {
          allData.push([normalizedName, sheetName, i + 1]);
        }
      }
    }
  });

  // Write data to Master sheet
  if (allData.length > 0) {
    masterSheet.getRange(2, 1, allData.length, 3).setValues(allData);
    masterSheet.autoResizeColumns(1, 3);
  }

  return `Master sheet built with ${allData.length} students`;
}

/**
 * clearCache()
 * - Clears both in-memory and service caches for debugging.
 */
function clearCache() {
  _masterMap = null;

  const cache = CacheService.getScriptCache();
  cache.remove('masterMap');

  console.log("All caches cleared");
}



