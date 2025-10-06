module.exports = {
  apps: [{
    name: 'swap-bot',
    script: 'run_bot.py',
    interpreter: 'python3',
    cwd: '/opt/swap-bot',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
};
