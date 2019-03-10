echo "Honeypot file collector"
echo "Ignore Permission denied warnings for tmp files"
echo "Collecting files from ssh-wolf. Enter password for cybex-user"
rsync -r -e 'ssh -p 22223' cybex-user@157.230.141.75:/home/cowrie/cowrie/var/lib/cowrie/downloads/ new-files/
echo "Collecting files from ssh-arf. Enter password for cybex-user"
rsync -r -e 'ssh -p 22222' cybex-user@134.197.113.10:/home/cowrie/cowrie/var/lib/cowrie/downloads/ new-files/
echo "Collecting files from ssh-peavine. Enter password for cybex-user"
rsync -r -e 'ssh -p 22222' cybex-user@134.197.113.9:/home/cowrie/cowrie/var/lib/cowrie/downloads/ new-files/
