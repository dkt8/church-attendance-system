// === QR Attendance Script with Full Caching and YYYYMMDD DateKey ===

// Global in-memory caches for faster repeated lookups
let _masterMap = null;  // Map: normalizedName → [sheetName, row]
let _dateMap   = null;  // Map: YYYYMMDD key → 1-based column index

/**
 * dateKey(date)
 * - Converts a Date to an integer key in YYYYMMDD format.
 */
function dateKey(date) {
  const yyyy = date.getFullYear();
  const mm   = String(date.getMonth() + 1).padStart(2, '0');
  const dd   = String(date.getDate()).padStart(2, '0');
  return Number(`${yyyy}${mm}${dd}`);  // e.g. 20250518
}

/**
 * doGet(e)
 * - Serves Scanner.html UI if no 'name' param.
 * - Otherwise, processes the QR scan via logScan().
 */
function doGet(e) {
  if (!e?.parameter?.name) {
    return HtmlService
      .createHtmlOutputFromFile("Scanner")
      .setTitle("QR Code Scanner");
  }
  try {
    return ContentService
      .createTextOutput(logScan(e.parameter.name));
  } catch (err) {
    return ContentService
      .createTextOutput("Error: " + err.message);
  }
}

/**
 * logScan(data)
 * - Main function to record attendance quickly.
 * - Minimal logs at entry and before each return.
 */
function logScan(data) {
  console.log(`logScan start: ${data}`);  // entry log

  const masterMap = getMasterMap();
  const normalized = normalize(data);
  if (!(normalized in masterMap)) {
    console.log(`Return error: Name not in masterMap: ${normalized}`);
    return "Error: Name not found in Master map.";
  }

  const [sheetName, row] = masterMap[normalized];
  const sheet = SpreadsheetApp.getActive().getSheetByName(sheetName);
  if (!sheet) {
    console.log(`Return error: Sheet missing: ${sheetName}`);
    return `Error: Sheet "${sheetName}" not found.`;
  }

  const now = new Date();
  const todayKey = dateKey(now);
  const hh = String(now.getHours()).padStart(2, "0");
  const mm = String(now.getMinutes()).padStart(2, "0");
  const ss = String(now.getSeconds()).padStart(2, "0");
  const currentTime = `${hh}:${mm}:${ss}`;

  // Cached date→column lookup with CacheService fallback
  const dateMap = getDateColumnMap(sheet);
  const baseCol = dateMap[todayKey];
  if (!baseCol) {
    console.log(`Return error: No date column for key ${todayKey}`);
    return `Error: No matching column for today's date (${todayKey}).`;
  }

  if (currentTime >= "09:10:00" && currentTime < "10:00:00") {
    console.log(`Return skipped: Time within skip window: ${currentTime}`);
    return `Skipped: No attendance marked between 09:10 and 10:00 for ${data}`;
  }

  const col = (currentTime >= "10:00:00") ? baseCol + 1 : baseCol;
  const status = (currentTime < "09:00:00") ? "X"
               : (currentTime < "09:10:00") ? "T"
               : (currentTime < "12:00:00") ? "X"
               : "O";

  sheet.getRange(row, col).setValue(status);
  console.log(`Checked in ${data} → sheet:${sheetName}, row:${row}, col:${col}, status:${status}`);

  const successMsg = `Success: ${data} checked in at ${hh}:${mm}:${ss}.`;
  console.log(`Return success: ${successMsg}`);
  return successMsg;
}

/**
 * getDateColumnMap(sheet)
 * - Retrieves a cached YYYYMMDD→column map from CacheService or in-memory.
 * - If missing, builds from row 9 headers (strings dd/mm/yyyy or Date objects).
 */
function getDateColumnMap(sheet) {
  // In-memory cache
  if (_dateMap) return _dateMap;

  const cache = CacheService.getScriptCache();
  const cacheKey = 'dateMap';
  let raw = cache.get(cacheKey);
  if (raw) {
    _dateMap = JSON.parse(raw);
    return _dateMap;
  }

  // Build the map
  const header = sheet.getRange(9, 1, 1, sheet.getLastColumn()).getValues()[0];
  const map = {};
  const dateRegex = /^\d{2}\/\d{2}\/\d{4}$/;

  header.forEach((cell, idx) => {
    let dObj = null;
    if (cell instanceof Date) {
      dObj = cell;
    } else if (typeof cell === 'string' && dateRegex.test(cell.trim())) {
      const [d, m, y] = cell.trim().split('/');
      dObj = new Date(+y, +m - 1, +d);
    }
    if (dObj) {
      const key = dateKey(dObj);
      map[key] = idx + 1;
    }
  });

  // Cache for 6 hours and store in-memory
  cache.put(cacheKey, JSON.stringify(map), 6 * 60 * 60);
  _dateMap = map;
  return _dateMap;
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
 * clearCache()
 * - Clears both in-memory and service caches for debugging.
 */
function clearCache() {
  _masterMap = null;
  _dateMap = null;
  const c = CacheService.getScriptCache();
  c.remove('masterMap');
  c.remove('dateMap');
}

/**
 * getSpreadsheetUrl()
 * - Returns the URL of the current spreadsheet for the View button.
 */
function getSpreadsheetUrl() {
  return SpreadsheetApp.getActive().getUrl();
}
