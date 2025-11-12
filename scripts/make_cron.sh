#write out current crontab
crontab -l > mycron
#echo new cron into cron file, run at 6am every day
echo "0 6 * * * cd ~/zamboni && /home/ec2-user/zamboni/venv/bin/python -m zamboni > ~/zamboni/data/cron_log.txt 2>&1" >> mycron
#install new cron file
crontab mycron
rm mycron
