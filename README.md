# ssh-config-enhance

add alias

```
alias sso="main.py"
```

add comment for ssh config

```
Host *
    ServerAliveInterval 30

Host test1
    HostName ip
    Port 22
    User adidas
    #DynamicForward 12083
    LocalForward 3389 someip:3389
#group group1
#tags test dev

Host jumpserver-test-user1
    HostName ip2
    Port 22
    User user1
#group group2
#tags bastion dev

Host dev-jump-server
    HostName ip2
    User opsadmin
    ForwardAgent yes
    DynamicForward 11083
#group group2
#tags bastion dev ops
```

