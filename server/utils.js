const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./db/app.db');

db.run(`
    CREATE TABLE IF NOT EXISTS data(
    keyID TEXT,
    value TEXT,
    PRIMARY KEY (keyID)
    ) STRICT
`);

function write(key, value) {
    return new Promise((resolve, reject) => {
        const stmt = db.prepare(`
            INSERT INTO data (keyID, value) VALUES (?, ?)
            ON CONFLICT(keyID) DO UPDATE SET value = ?
        `);
        
        stmt.run(key, value, value, function (err) {
            if (err) {
                return reject(err.message);
            }
            return resolve(this.lastID);
        });
        
        stmt.finalize();
    });
}

function view(key) {
    return new Promise((resolve, reject) => {
        db.get(`
            SELECT value FROM data WHERE keyID = ?
        `, [key], function (err, row) {
            if (err) {
                return reject(err.message);
            }
            return resolve(row ? row.value : null);
        });
    });
}

module.exports = {
    write,
    view
} 