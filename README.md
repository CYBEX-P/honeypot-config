# honeypot-configuration
Configuration overview for UNR honeypots.

Slides for the honeypot presentation can be found [here](honeypot_pres.pptx): 

## Starting the Honeypot
If the virtual machines have been recently shut off, the following things need to be done to start the honeypot again:
##### SSH server
- sudo service filebeat start
- sudo service ssh start (if ssh access is required)
- sudo su cowrie
- (do the following as the cowrie user, full paths provided to avoid confusion):
- source /home/cowrie/cowrie/cowrie-env/bin/activate
- /home/cowrie/cowrie/bin/cowrie start

##### Web server
- sudo service filebeat start

##### (DigitalOcean honeypot only) Droplet
* sudo iptables-restore iptables.conf

## Central ELK server
The central ELK server is configured to accept logs from all honeypots. It receives logstash data as beats on port 5000. Kibana is currently running on port 5601, although it only accepts traffic from localhost.

The logstash configuration file for the central ELK server is [Here](configs/elk-master-logstash.conf)

## Network Configuration
NAT port forwarding overview:
- 22, 2222 --> SSH-ARF:2222 (Cowrie SSH port)
- 23, 2223 --> SSH-ARF:2223 (Cowrie telnet port)
- 22222 --> SSH-ARF:22222 (OpenSSH server: I keep this service off on the SSH server when I don't need it)
- 143, 993, 110, 995, 25 --> Mailserver-ARF (25 should be the only port needed, but I forwarded all the mail ports)
- 80 --> Webserver-ARF
- 5900 --> Monitor-ARF (Remote desktop)

The SSH component of the honeypot is composed of two servers, both running on a local virt-manager network: the ELK server and the SSH server. The SSH server is the actual honeypot, and runs a fake server on several SSH and Telnet ports. Data from this server are sent to the ELK server, which saves and processes the data.

The mail server is a single server on the same local network. It acts as a normal mail server, configured to send and receive mail. At present no data from this server is processed and forwarded anywhere.

## SSH Configuration
The SSH honeypot uses [Cowrie](https://github.com/cowrie/cowrie) as the honeypot and [filebeat](https://www.elastic.co/products/beats/filebeat) to forward Cowrie logs to the ELK server. Cowrie is installed according to the [Cowrie docs](https://github.com/cowrie/cowrie/blob/master/INSTALL.md). Filebeat is installed with the [provided deb package](https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-installation.html). I had no issues following the installation instructions for either. A few things were changed after the basic install for Cowrie:

- etc/cowrie.cfg.default was copied to etc/cowrie.cfg. The hostname was changed to arfedu-main, download_limit_size was enabled and set to 40MB, telnet was enabled, and additional listen points were set as follows: listen_endpoints = tcp:22:interface=0.0.0.0 tcp:2222:interface=0.0.0.0. The server seems to still not accept traffic on ports 22 and 23, so for now I changed the NAT rules on pfsense to forward these ports to 2222 and 2223, respectively.
- etc/userdb.example was moved to etc/userdb.txt and was modified so that all accounts had "\*" as their valid password (allowing all passwords). The rules excluding passwords containing 'honeypot' or '12345' were removed.

Filebeat was configured to forward the cowrie.json logs to the ELK-ARF server. Cowrie has an inbuilt module for forwarding logs to elasticsearch, but this was not used. The filebeat.yml configuration file (placed in /etc/filebeat) has been uploaded in the configs folder, [Here](configs/filebeat.yml).

## Mail Configuration
The mail server was installed according to [this tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-postfix-on-ubuntu-18-04). /etc/postfix/virtual was modified to map the contact, mail, and admin usernames to cybex-user@arfeducation.org's inbox. I found that I needed to install MySQL beforehand for the s-nail installation to work.

Emails pasted to:
- https://pastebin.com/t3j5KCVq
- https://pastebin.com/tjTHkbc3

## Webserver configuration
Both honeypots have apache2 webservers running on their domains. Apache logs are sent to the ELK stack under a default index pattern. The webserver pattern is apache-[timestamp], and the ssh pattern is logstash-[timestamp] (it would obviously be better to have this pattern as ssh-[timestamp], but I used the default pattern when I created the ssh honeypot and did not have the webserver in mind).

The webserver uses filebeat, with a slightly different configuration file (the path is changed to /var/log/apache2/access.log). Although the filter is named 10-cowrie.conf, it uses if/else statements to handle both the cowrie logs and apache logs.

To get access to this data in Kibana, a new index pattern has to be created under the management section. Once this is done, the apache index pattern can be used for visualizations, etc.

## ELK Configuration
ELK was installed according to [the following tutorial](https://logz.io/learn/complete-guide-elk-stack/#installing-elk) on logz.io. I stopped following the tutorial at the "Installing Beats" section. 10-cowrie.conf (placed in /etc/logstash/conf.d/10-cowrie.conf) was written to parse data provided by the honeypot. The conf file reads in Cowrie's JSON data, splits the input command to the first field (just the command the attacker uses, not its arguments. The full command is stored in the message field), and renames "message" to "msg" due to issues with Kibana. The data is then forwarded to elasticsearch, where it is used by Kibana.

The logstash configuration file for each ELK server is [Here](configs/honeypot-logstash.conf)

## DigitalOcean Honeypot
The DigitalOcean honeypot is configured slightly differently than the other honeypots. Routing is handled by iptables, which forwards ports similarly to the other 2 honeypots. Mail ports are not currently forwarded. The DigitalOcean honeypot only contains 2 VMs, one for SSH and one for Web. There is currently no ELK server storing data for this honeypot, the data is sent to the central ELK only.
