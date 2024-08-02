# Summary
Example integration of StealthGuardian in Fortra's Cobalt Strike

If you want to use StealthGuardian with Cobalt Strike, please import `integration/cobaltstrike/stealthguardian.cna` to your Cobalt Strike client. A new menu will show at the top which can be used to configure the connection to the `Middleware`.

# Usage
| Command                 | Description                                                |
| ----------------------- | ---------------------------------------------------------- |
| stealthguardian (or sg) | `Usage: stealthguardian <beacon> <command>`                |
| initiateLogCheck        | Initiate a logcheck, ensure a beacon is mapped to an agent |
| printBeacon             | Get Information about the current Beacon                   |
| listBeacons             | List all Beacons in your client                            |

# Files in this Directory

| Filename                | Purpose                                                                                         |
| ----------------------- | ----------------------------------------------------------------------------------------------- |
| Readme.md               | Readme of this directory                                                                        |
| cobaltstrike.Dockerfile | Dockerfile used for installing the environment                                                  |
| headless-strike.cna     | Agressor Script: Implemented Cobalt Strike function for automatic execution via StealthGuardian |
| logger.cna              | Agressor Script: Functions to send log information to Beacons via StealthGuardian               |
| main.sh                 | Bash script that is executed within the Docker environment                                      |
| stealthguardian.cna     | Agressor Script: Needs to be loaded in Cobalt Strike by the user                                |
| watcher.py              | Python Script that checks for outstanding tasks and/or logs that need to be processed           |

# Supported Commands
The following `Cobalt Strike` commands are supported via the `headless-strike.cna` script in StealthGuardian:

| CNA Command               | Cobalt Strike Agressor Function                                                                                                                                                             |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| beacons                   | N/A                                                                                                                                                                                         |
| use                       | N/A                                                                                                                                                                                         |
| remove                    | [beacon_remove](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#beacon_remove)                       |
| getuid                    | [bgetuid](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bgetuid)                                   |
| help                      | [beacon_command_detail](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#beacon_command_detail)       |
| getsystem                 | [bgetsystem](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bgetsystem)                             |
| execute                   | [bexecute](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bexecute)                                 |
| execute_assembly          | [bexecute_assembly](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bexecute_assembly)               |
| jump                      | [bjump](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bjump)                                       |
| clear                     | [bclear](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bclear)                                     |
| download                  | [bdownload](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bdownload)                               |
| downloads                 |                                                                                                                                                                                             |
| sync_download             |                                                                                                                                                                                             |
| inject                    | [binject](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#binject)                                   |
| spawn                     | [bspawn](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bspawn)                                     |
| shspawn                   | [bshspawn](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bshspawn)                                 |
| shinject                  | [bshinject](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bshinject)                               |
| keylogger                 | [bkeylogger](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bkeylogger)                             |
| keystrokes                |                                                                                                                                                                                             |
| drives                    | [bdrives](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bdrives)                                   |
| upload                    | [bupload](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bupload)                                   |
| pwd                       | [bpwd](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bpwd)                                         |
| rm                        | [brm](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#brm)                                           |
| shell                     | [bshell](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bshell)                                     |
| run                       | [brun](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#brun)                                         |
| runu                      | [brunu](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#brunu)                                       |
| powershell                | [powershell](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#powershell)                             |
| powershell_import         | [bpowershell_import](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bpowershell_import)             |
| powershell_import_clear   | [bpowershell_import_clear](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bpowershell_import_clear) |
| powerpick                 | [bpowerpick](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bpowerpick)                             |
| powerpick_inject          | [bpsinject](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bpsinject)                               |
| screenshot                | [bscreenshot](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bscreenshot)                           |
| screenwatch               | [bscreenwatch](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bscreenwatch)                         |
| steal_token               | [bsteal_token](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bsteal_token)                         |
| kill                      | [bkill](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bkill)                                       |
| sleep                     | [bsleep](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bsleep)                                     |
| socks                     | [bsocks](https://uhstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bsocks)                                    |
| socks_stop                | [bsocks_stop](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bsocks_stop)                           |
| spawnto                   | [bspawnto](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bspawnto)                                 |
| info                      | [binfo](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#binfo)                                       |
| note                      | [bnote](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bnote)                                       |
| ppid                      | [bppid](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bppid)                                       |
| rev2self                  | [brev2self](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#brev2self)                               |
| remove                    | [beacon_remove](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#beacon_remove)                       |
| dcsync                    | [bdcsync](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bdcsync)                                   |
| hashdump                  | [bhashdump](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bhashdump)                               |
| mimikatz                  | [bmimikatz](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bmimikatz)                               |
| mkdir                     | [bmkdir](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bmkdir)                                     |
| cd                        | [bcd](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bcd)                                           |
| mv                        | [bmv](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bmv)                                           |
| net                       | [bnet](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bnet)                                         |
| ipconfig                  | [bipconfig](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bipconfig)                               |
| link                      | [blink](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#blink)                                       |
| unlink                    | [bunlink](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bunlink)                                   |
| make_token                | [bloginuser](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bloginuser)                             |
| dir                       | [bls](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bls)                                           |
| jobs                      | [bjobs](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bjobs)                                       |
| jobkill                   | [bjobkill](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bjobkill)                                 |
| blockdlls                 | [bblockdlls](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bblockdlls)                             |
| logonpasswords            | [blogonpasswords](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#blogonpasswords)                   |
| ps                        | [bps](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bps)                                           |
| _exit                     | [bexit](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bexit)                                       |
| cp                        | [bcp](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bcp)                                           |
| pth                       | [bpassthehash](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bpassthehash)                         |
| reg                       | [breg_queryv](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#breg_queryv)                           |
| ssh                       | [bssh](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bssh)                                         |
| ssh_key                   | [bssh_key](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bssh_key)                                 |
| timestomp                 | [btimestomp](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#btimestomp)                             |
| clipboard                 | [bclipboard](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bclipboard)                             |
| desktop                   | [bdesktop](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bdesktop)                                 |
| getprivs                  | [bgetprivs](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bgetprivs)                               |
| kerberos_ticket_purge     | [bkerberos_ticket_purge](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bkerberos_ticket_purge)     |
| rportfwd                  | [brportfwd](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#brportfwd)                               |
| rportfwd_local            | [brportfwd_local](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#brportfwd_local)                   |
| runas                     | [brunas](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#brunas)                                     |
| setenv                    | [bsetenv](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bsetenv)                                   |
| spawnas                   | [bspawnas](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bspawnas)                                 |
| spawnu                    | [bspawnu](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bspawnu)                                   |
| syscall_method            | [bsyscall_method](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bsyscall_method)                   |
| mode                      | [bmode](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bmode)                                       |
| covertvpn                 | [bcovertvpn](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bcovertvpn)                             |
| connect                   | [bconnect](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bconnect)                                 |
| cancel                    | [bcancel](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bcancel)                                   |
| bbrowserpivot             | [bbbrowserpivot](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bbrowserpivot)                      |
| checkin                   | [bcheckin](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bcheckin)                                 |
| printscreen               | [bbprintscreen](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bprintscreen)                        |
| dllload                   | [bdllload](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bdllload)                                 |
| dllinject                 | [bdllinject](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bdllinject)                             |
| kerberos_ccache_use       | [bkerberos_ccache_use](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bkerberos_ccache_use)         |
| kerberos_ticket_use       | [bkerberos_ticket_use](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bkerberos_ticket_use)         |
| spunnel                   | [bspunnel](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bspunnel)                                 |
| spunnel_local             | [bspunnel_local](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bspunnel_local)                     |
| remote_exec               | [bremote_exec](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bremote_exec)                         |
| elevate                   | [belevate](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#belevate)                                 |
| token_store_steal         | [btoken_store_steal](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#btoken_store_steal)             |
| token_store_steal_and_use | [btoken_store_steal_and_use](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#btoken_store_steal-use) |
| token_store_use           | [btoken_store_use](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#btoken_store_use)                 |
| token_store_show          | [btoken_store_show](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#btoken_store_show)               |
| token_store_remove        | [btoken_store_remove](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#btoken_store_remove)           |
| token_store_remove_all    | [btoken_store_remove_all](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#btoken_store_remove_all)   |
| data_store_list           | [bdata_store_list](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bdata_store_list)                 |
| data_store_load           | [bdata_store_load](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bdata_data_store_load)            |
| argue_add                 | [bargue_add](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bargue_add)                             |
| argue_remove              | [bargue_remove](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bargue_remove)                       |
| argue_list                | [bargue_list](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#bargue_list)                           |
| inline-execute            | [binline-execute](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm?#binline_execute)                   |

# References
Inspired by:

* [cobaltstrike-headless](https://github.com/CodeXTF2/cobaltstrike-headless)
