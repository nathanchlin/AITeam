crontab -e
# 添加以下行（每天凌晨2点执行）
0 2 * * * /home/$USER/backup_gomoku.sh