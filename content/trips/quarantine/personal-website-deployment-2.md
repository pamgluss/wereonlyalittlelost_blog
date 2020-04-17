---
title: "Getting Travis to Deploy my Website to Godaddy Part 2"
date: 2020-04-16
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

We should tackle that first. I think there's a 3 second timeout for ftp, and Travis being a free service might be too slow? 