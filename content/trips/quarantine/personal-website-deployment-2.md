---
title: "Getting Travis to Deploy my Website to Godaddy Part 2"
date: 2020-08-16
tags: ['Quarantine']
draft: true
---

Continued from [Part 1](/trips/quarantine/personal-website-deployment)

So the Bash script works when I run it locally, but my first go on Travis didn't go so well...

```
227 Entering Passive Mode (173,201,92,1,195,140)
421 Timeout
Not connected.
Not connected.
Local directory now /path/to/css
Not connected.
Not connected.
Local directory now /path/to/js
Not connected.
Not connected.
Local directory now /path/to/img
Not connected.
The command "sh run.sh" exited with 0.
```

Let's take a gander at that. Googled ["ftp passive mode travis ci"](https://blog.travis-ci.com/2018-07-23-the-tale-of-ftp-at-travis-ci) and found out Travis specifically prevents FTP passive mode. CRAP! I was so proud of that bash script! Okay so Travis recommends a few avenues:
- HTTPS: Based on what I've seen and read I strongly doubt this is possible with GoDaddy but there's no point in not looking into it.
-  SFTP: Should come bundled in with `inetutils` right?
- FTP but with a tunnel: I know *of* tunneling but I've never set it up before. Worth a google and they even have a link I can follow.

First: HTTPS requires an SSL cert which according to my dad: "I'm wondering how to enable ssl without paying 10x per month. They would have to work at it to make this hard."

Let's go around that and try out SFTP.
