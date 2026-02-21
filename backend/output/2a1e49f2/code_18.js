// ecosystem.config.js (PM2配置)
module.exports = {
  apps: [{
    name: 'tetris-battle-server',
    script: 'index.js',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production'
    }
  }]
};