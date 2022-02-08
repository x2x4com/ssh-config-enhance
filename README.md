# ssh-config-enhance

## How to use

1. Make sure you have python3 on your path
2. Install the requirements in the requirements.txt(`pip install -r requirementys.txt`)
3. Modify you ssh config and add some special comment **after configuring content**
    - \#group groupname 
    - \#tags tags1 tags2 tags3
4. Run the script, `python3 main.py`
   ```bash
    $ python3 main.py -g test
    SSH Manager (Version 3.3)
    Group: test
    Tags: NULL
    +----+--------------------+-------+-----------------+-----------+
    | ID | Link Target        | Group |            Tags | Host Info |
    +----+--------------------+-------+-----------------+-----------+
    | 0  | root@127.0.0.1:22  | test  | test local root | test1     |
    | 1  | root@127.0.0.2:22  | test  | test local root | test2     |
    | 2  | root@127.0.0.3:22  | test  | test local root | test3     |
    | 3  | root@127.0.0.4:22  | test  | test local root | test4     |
    | 4  | root@127.0.0.5:22  | test  | test local root | test5     |
    | 5  | root@127.0.0.6:22  | test  | test local root | test6     |
    | 6  | root@127.0.0.7:22  | test  | test local root | test7     |
    | 7  | root@127.0.0.8:22  | test  | test local root | test8     |
    | 8  | root@127.0.0.9:22  | test  | test local root | test9     |
    | 9  | root@127.0.0.10:22 | test  | test local root | test10    |
    | 10 | root@127.0.0.11:22 | test  | test local root | test11    |
    | 11 | root@127.0.0.12:22 | test  | test local root | test12    |
    +----+--------------------+-------+-----------------+-----------+
    Input [ID] number:
   ```
5. Input the ID to login

Also, you can use filter like this

list all group name is test

```bash
python3 main.py -g test
```

list all group name is test and tags have root

```bash
python3 main.py -g test -t root
```

Recommended use alias to simplify input

add alias

```
alias sso="python3 somedir/main.py"
```

run it

```bash
sso -g test -t root
```

## SSH Config Example

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

