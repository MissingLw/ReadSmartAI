const { Sequelize } = require('sequelize');

const sequelize = new Sequelize('cs340_heardd', 'root', 'Marip0sa$3lCapitan$', {
  host: '127.0.0.1',
  port: 3308,
  dialect: 'mysql',
  pool: {
    max: 10,
    min: 0,
    acquire: 30000,
    idle: 10000
  },
});

module.exports = sequelize;



/*
// Get an instance of mysql we can use in the app
const mysql = require('mysql');

// Create a 'connection pool' using the provided credentials
var pool = mysql.createPool({
    connectionLimit : 10,
    host            : '127.0.0.1',
    port            : 3308,
    user            : 'root',
    password        : 'Marip0sa$3lCapitan$',
    database        : 'cs340_heardd'
})

pool.getConnection((err, connection) => {
  if (err) {
    if (err.code === 'PROTOCOL_CONNECTION_LOST') {
      console.error('Database connection was closed.')
    }
    if (err.code === 'ER_CON_COUNT_ERROR') {
      console.error('Database has too many connections.')
    }
    if (err.code === 'ECONNREFUSED') {
      console.error('Database connection was refused.')
    }
  }

  if (connection) connection.release()

  return
})

// Promisify for Node.js async/await.
pool.query = util.promisify(pool.query)

module.exports = pool;


*/