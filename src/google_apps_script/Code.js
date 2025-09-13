// === QR Attendance Script - V2.5.0 ===

// Global in-memory cache for master map
let _masterMap = null;  // Map: normalizedName → {spreadsheetId, row}

// Spreadsheet ID mapping for each class
const SPREADSHEET_MAP = {
  // TODO: Replace with actual IDs
  'c1': '1DdJbRdQ2gcf90_Ac1U7K9k2MlyNQZWF7fz1YLp9EzaM',
  'c2': '1bSayPQafLXuOgM_gPdGP6LWQ7n-qwmB94cpujBnMqGE',
  // au nhi
  'a1': '1atwfmZsL2qco5akH4I84mFDnZyjzR8Q4mFVBrxWxbi4',
  'a2': '1ydlXhW44ILghLTCtF_8jOD9e8J58kCJgULvMveQe6gw',
  'a3': '1Y8XRPwqMSHlbEBDHEXLQYCEc5kCoV_dtuQIV-uo_lpw',
  // thieu nhi
  't1': '1FDtxlNLrSY30U7zAku2nYOFpHb-Fv8yWVucnXnNGCDQ',
  't2': '1nJnfVL0umIN-AKEWFKy9UCp_mRei-PON8GSSDpM4wyc',
  't3': '1prFTfu7Bu7Pb5siP0kHIyt6sMXGL2ITcu0OICAlu488',
  // nghia si
  'n1': '1OXVC22Lcg8_oBHXXhoJygVaogWcjXHSb28ZxRWjMgfQ',
  'n2': '1g27jM5FgkWTzBBiIYtmsPoPkjvZ5zfNiPeFyTL97gAM',
  'n3': '1L47gsgzYrbFU5_3QoqAAf6s8U1IHUUiwoPGlTs_d1s8',
  // hiep si
  'h1': '1Ba2z42eA3ptr6y3d6032mWWceZi4O4DzAld_2vIywvE',
  'h2': '1wAhH1FpNCY7oFtqurRKhL1gIKvmmSBwUP1tVfXBvkfw',
  // boi duong bi tich  
  'bdbt': '1DD7kvnhCcpk7i-bBVhfsh5IryrdHeRyb6n9zRDyX4T4'
};

/**
 * getClassList()
 * - Returns list of class codes and their spreadsheet URLs
 * - Format: [{code, url}]
 */
function getClassList() {
  return Object.entries(SPREADSHEET_MAP).map(([code, id]) => ({
    code: code,
    url: `https://docs.google.com/spreadsheets/d/${id}/edit`
  }));
}

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
 * - Uses master map to route to correct spreadsheet
 */
function logScan(data) {
  // data = "Giuse Trần Hoàng Nguyên Khôi c1";
  console.log(`logScan start: ${data}`);

  // parts = ["Giuse", "Trần", "Hoàng", "Nguyên", "Khôi", "c1"]
  const parts = data.trim().split(/\s+/);

  const className = parts.pop(); // c1
  const nameOnly = parts.join(" "); // "Giuse Trần Hoàng Nguyên Khôi"
  const normalized = normalize(nameOnly); // "giusetranhoangnguyenkhoi"

  console.log(`Parsed: name="${nameOnly}", class="${className}", normalized="${normalized}"`);

  // Use master map for multi-spreadsheet lookup
  const masterMap = getMasterMap();
  if (!(normalized in masterMap)) {
    console.log(`Return error: Name not in masterMap: ${normalized}`);
    return `Error: "${nameOnly}" not found in master map.`;
  }

  const { spreadsheetId, row } = masterMap[normalized];

  // Validate that the requested class matches the spreadsheet
  if (!SPREADSHEET_MAP[className] || SPREADSHEET_MAP[className] !== spreadsheetId) {
    console.log(`Return error: Class mismatch. "${nameOnly}" not found in class ${className}`);
    return `Error: "${nameOnly}" not found in class ${className}.`;
  }

  // Open the target spreadsheet and get "Điểm danh" sheet
  const targetSpreadsheet = SpreadsheetApp.openById(spreadsheetId);
  const sheet = targetSpreadsheet.getSheetByName('Điểm danh');

  if (!sheet) {
    console.log(`Return error: "Điểm danh" sheet missing in ${className} spreadsheet`);
    return `Error: "Điểm danh" sheet not found in ${className} spreadsheet.`;
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
  console.log(`Checked in ${nameOnly} → spreadsheet:${spreadsheetId}, row:${row}, col:${col}, status:${status}`);

  const successMsg = `Success: ${nameOnly} (${className}) checked in at ${hh}:${mm}:${ss}.`;
  console.log(`Return success: ${successMsg}`);
  return successMsg;
}

/**
 * findTodayColumn(sheet)
 * - Simple function to find today's TL column
 * - Pattern: dates every 2 columns starting from column 6
 */
function findTodayColumn(sheet) {
  const today = new Date();
  // Set today to start of day for fair comparison
  today.setHours(0, 0, 0, 0);

  console.log(`Today object: ${today}`);

  // Get header row with dates (Row 8: 7/9/2025, 14/9/2025, 21/9/2025, 28/9/2025)
  const headerRow = sheet.getRange(8, 1, 1, sheet.getLastColumn()).getValues()[0];

  // Check every 2 columns starting from column 6 (index 5)
  for (let idx = 5; idx < headerRow.length; idx += 2) {
    const cell = headerRow[idx];
    console.log(`Column ${idx + 1}: ${cell}`);

    if (cell instanceof Date) {
      // Set cell date to start of day for fair comparison
      const cellDate = new Date(cell);
      cellDate.setHours(0, 0, 0, 0);

      console.log(`Comparing dates: today=${today.getTime()} vs cell=${cellDate.getTime()}`);

      // If today is less than or equal to cell date (upcoming sunday), this is our column
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
 * buildMasterMap()
 * - Scans all spreadsheets and builds a global routing table
 * - Format: normalizedName → {spreadsheetId, row}
 */
function buildMasterMap() {
  console.log('Building master map across all spreadsheets...');

  const masterMap = {};
  let totalStudents = 0;

  // Iterate through all class-to-spreadsheet mappings
  for (const [classCode, spreadsheetId] of Object.entries(SPREADSHEET_MAP)) {
    try {
      console.log(`Processing class ${classCode} (${spreadsheetId})...`);

      // Open the target spreadsheet
      const targetSpreadsheet = SpreadsheetApp.openById(spreadsheetId);

      // Look for the "Điểm danh" sheet specifically
      const dataSheet = targetSpreadsheet.getSheetByName('Điểm danh');

      if (!dataSheet) {
        console.log(`Warning: "Điểm danh" sheet not found in ${classCode} spreadsheet`);
        continue;
      }

      console.log(`Found "Điểm danh" sheet in ${classCode}`);

      // Get all data from the sheet
      const data = dataSheet.getDataRange().getValues();

      // Process each row to find students
      for (let i = 0; i < data.length; i++) {
        const row = data[i];
        const studentNumber = row[1];

        // Skip if second column is not a positive integer (not student data)
        if (!studentNumber || typeof studentNumber !== 'number' || !Number.isInteger(studentNumber) || studentNumber <= 0) {
          continue;
        }

        const saintName = (row[2] || "").toString().trim();
        const firstName = (row[3] || "").toString().trim();
        const lastName = (row[4] || "").toString().trim();

        if (saintName || firstName || lastName) {
          const fullName = `${saintName} ${firstName} ${lastName}`.trim();
          const normalizedName = normalize(fullName);

          if (normalizedName) {
            // Store in master map
            masterMap[normalizedName] = {
              spreadsheetId: spreadsheetId,
              row: i + 1
            };
            totalStudents++;
          }
        }
      }

      console.log(`Processed ${classCode}: found students`);

    } catch (error) {
      console.log(`Error processing ${classCode} (${spreadsheetId}): ${error.message}`);
    }
  }

  // Cache the master map
  CacheService.getScriptCache().put('masterMap', JSON.stringify(masterMap), 6 * 60 * 60);
  _masterMap = masterMap;

  console.log(`Master map built: ${totalStudents} total students across ${Object.keys(SPREADSHEET_MAP).length} spreadsheets`);
  return `Master map built with ${totalStudents} students from ${Object.keys(SPREADSHEET_MAP).length} spreadsheets`;
}

/**
 * getMasterMap()
 * - Returns in-memory or cached master map, building if needed.
 */
function getMasterMap() {
  if (_masterMap) return _masterMap;

  const cache = CacheService.getScriptCache();
  let raw = cache.get('masterMap');

  if (!raw) {
    buildMasterMap();
    raw = cache.get('masterMap');
  }

  if (!raw) throw new Error('Master map could not be loaded.');

  _masterMap = JSON.parse(raw);
  return _masterMap;
}

/**
 * clearCache()
 * - Clears both in-memory and service caches for debugging.
 */
function clearCache() {
  _masterMap = null;

  const cache = CacheService.getScriptCache();
  cache.remove('masterMap');

  console.log("Master cache cleared");
}