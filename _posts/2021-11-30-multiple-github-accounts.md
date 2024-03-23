---
layout: post
title: Dealing with multiple GitHub Accounts
tags: [git, tutorial, github]
---

The first Google result for "multiple GitHub accounts" right now points to a [solution](https://www.freecodecamp.org/news/manage-multiple-github-accounts-the-ssh-way-2dadc30ccaca/) using a SSH config change:

```conf
# Personal account, - the default config
Host github.com
   HostName github.com
   User git
   IdentityFile ~/.ssh/id_rsa
   
# Work account-1
Host github.com-work_user1    
   HostName github.com
   User git
   IdentityFile ~/.ssh/id_rsa_work_user1
```

I'm not a big fan of this solution as it requires one to use an alias instead of the proper hostname for the remote. I ended up doing an alternative solution using Git's [conditionals](https://blog.jiayu.co/2019/02/conditional-git-configuration/).

```conf
vpb@vpb-inspiron-5379:~$ cat .gitconfig
[user]
    name = Vitor Py Braga
    email = 12871+vitorpy@users.noreply.github.com
    signingkey = 6A2AF2C050EB3B3A
[commit]
    gpgsign = true
[alias]
    logs = log --show-signature
[includeIf "gitdir:~/example/"]
    path = ~/.gitconfig-example
```

```conf
vpb@vpb-inspiron-5379:~$ cat .gitconfig-example 
[user]
    name = Alternate Account
    email = alternate.account@example.com
    signingkey = 123457890ABCDE
[core]
    sshCommand = ssh -i ~/.ssh/example-id_rsa -F /dev/null -o 'IdentitiesOnly yes' 
```

Which is a somewhat cleaner solution.
