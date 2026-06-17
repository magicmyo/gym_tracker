// ── Offline detection ─────────────────────────────────────────────────────────

function updateOnlineStatus() {
  document.body.classList.toggle('offline', !navigator.onLine);
  if (navigator.onLine) syncPendingLogs();
}
window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);
updateOnlineStatus();

// ── IndexedDB pending log queue ───────────────────────────────────────────────

var DB_NAME = 'gymtracker';
var STORE = 'pending_logs';

function openDB() {
  return new Promise(function(resolve, reject) {
    var req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = function(e) {
      e.target.result.createObjectStore(STORE, { autoIncrement: true });
    };
    req.onsuccess = function(e) { resolve(e.target.result); };
    req.onerror = reject;
  });
}

function getPendingLogs() {
  return openDB().then(function(db) {
    return new Promise(function(resolve, reject) {
      var tx = db.transaction(STORE, 'readonly');
      var req = tx.objectStore(STORE).getAll();
      req.onsuccess = function(e) { resolve(e.target.result); };
      req.onerror = reject;
    });
  });
}

function clearPendingLogs() {
  return openDB().then(function(db) {
    var tx = db.transaction(STORE, 'readwrite');
    tx.objectStore(STORE).clear();
  });
}

function syncPendingLogs() {
  getPendingLogs().then(function(logs) {
    if (!logs.length) return;
    fetch('/api/sync/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({ logs: logs }),
    })
    .then(function(res) {
      if (res.ok) {
        clearPendingLogs();
        console.log('[GymTracker] Synced ' + logs.length + ' offline log(s).');
      }
    })
    .catch(function() {
      console.log('[GymTracker] Sync failed, will retry later.');
    });
  });
}

function getCookie(name) {
  var v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return v ? v.pop() : '';
}

// ── Service Worker registration ───────────────────────────────────────────────

if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/static/js/sw.js')
      .then(function() { console.log('[GymTracker] SW registered'); })
      .catch(function(e) { console.warn('[GymTracker] SW failed', e); });
  });
}
