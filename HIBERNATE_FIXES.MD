--- FIX 1 ---

remus@remus-B850-AORUS-STEALTH-ICE:~/Dokumente/thesis-v1-exp$ systemctl status sleep.target suspend.target hibernate.target hybrid-sleep.target
○ sleep.target - Sleep
     Loaded: loaded (/usr/lib/systemd/system/sleep.target; static)
     Active: inactive (dead)
       Docs: man:systemd.special(7)

○ suspend.target - Suspend
     Loaded: loaded (/usr/lib/systemd/system/suspend.target; static)
     Active: inactive (dead)
       Docs: man:systemd.special(7)

○ hibernate.target - System Hibernation
     Loaded: loaded (/usr/lib/systemd/system/hibernate.target; static)
     Active: inactive (dead)
       Docs: man:systemd.special(7)
○ hybrid-sleep.target
     Loaded: loaded (/usr/lib/systemd/system/hybrid-sleep.target; static)
     Active: inactive (dead)
       Docs: man:systemd.special(7)


remus@remus-B850-AORUS-STEALTH-ICE:~/Dokumente/thesis-v1-exp$ sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
Created symlink '/etc/systemd/system/sleep.target' → '/dev/null'.
Created symlink '/etc/systemd/system/suspend.target' → '/dev/null'.
Created symlink '/etc/systemd/system/hibernate.target' → '/dev/null'.
Created symlink '/etc/systemd/system/hybrid-sleep.target' → '/dev/null'.

remus@remus-B850-AORUS-STEALTH-ICE:~/Dokumente/thesis-v1-exp$ systemctl status sleep.target suspend.target hibernate.target
○ sleep.target
     Loaded: masked (Reason: Unit sleep.target is masked.)
     Active: inactive (dead)

○ suspend.target
     Loaded: masked (Reason: Unit suspend.target is masked.)
     Active: inactive (dead)

○ hibernate.target
     Loaded: masked (Reason: Unit hibernate.target is masked.)
     Active: inactive (dead)

○ hybrid-sleep.target
     Loaded: masked (Reason: Unit hybrid-sleep.target is masked.)
     Active: inactive (dead)


--- FIX 2

remus@remus-B850-AORUS-STEALTH-ICE:~/Dokumente/thesis-v1-exp$ cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference
balance_performance

remus@remus-B850-AORUS-STEALTH-ICE:~/Dokumente/thesis-v1-exp$ cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
powersave

--- Service einrichten der nach jedem reboot die settings ändert ---

```
[Unit]
Description=Pin AMD EPP and governor to performance
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'for f in /sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference; do echo performance > "$f"; done; for f in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do echo performance > "$f"; done'
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

(/etc/systemd/system/cpu-performance.service)

--- daemon neu laden (um datei zu erkennen) ---

sudo systemctl daemon-reload

--- service aktivieren ---

sudo systemctl enable --now cpu-performance.service


--- nach neustart prüfen --- 

remus@remus-B850-AORUS-STEALTH-ICE:~/Dokumente/thesis-v1-exp$ cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference
performance

remus@remus-B850-AORUS-STEALTH-ICE:~/Dokumente/thesis-v1-exp$ cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
performance
