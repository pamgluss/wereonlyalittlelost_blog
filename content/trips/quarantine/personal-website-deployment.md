---
title: "Getting Travis to Deploy my Website to Godaddy Part 1"
date: 2020-04-14
tags: ['Quarantine']
draft: false
---

In case it wasn't immediately obvious, my education and background are NOT in tech. Originally I wanted to be an artist! That's hilarious considering how [crappy I am at painting.](/trips/quarantine/dresser-painting) 

Anyways, when I was a senior in college I decided to do a hard turn into software by taking a couple of web development classes for non-majors. I figured I'd showcase my amazing animation skills AND my amazing web development skills by building my portfolio out on my Dad's domain. Leading us to [here](http://www.gluss.com/pamela/). It is in fact possible you were directed here by that website!

This Hugo site has a nifty pipeline with TravisCi that I'm extremely fond of, and it wasn't that hard to set up. I would like to have a similar pipeline for my personal site. The problem that can't be ignored is that it is hosted on GoDaddy. Historically I would open FileZilla, connect to the remote server, and drag n drop files to make changes to my website. What I noticed when I dusted the site off was I had all kinds of random files in there - index.html AND index.php for example. Doing this manually is a huge pain in the butt and is very easy to get out of sync with Github.

So this blog post will be where I compile my investigations, progress, and hopefully eventual success. 

Let's get started - can I automate the steps I've already been taking? That is to say, can I make a script like the one I use for Hugo to ftp to Godaddy? So let's [just google that...](https://blog.eduonix.com/shell-scripting/how-to-automate-ftp-transfers-in-linux-shell-scripting/) and it does look possible, at least to upload a file at a time. 

```
HOST='REDACTED'
USER='REDACTED'
PASSWD='REDACTED'

ftp -inv $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
hash
mput *.html
bye
END_SCRIPT
exit 0
```

Let's see if that works for me in my terminal.

```
220---------- Welcome to Pure-FTPd [privsep] [TLS] ----------
220-You are user number 2 of 500 allowed.
220-Local time is now 12:06. Server port: 21.
220-This is a private system - No anonymous login
220 You will be disconnected after 3 minutes of inactivity.
331 User  OK. Password required
230 OK. Current restricted directory is /
Hash mark printing on (1024 bytes/hash mark).
local: index.html remote: index.html
200 PORT command successful
425 Could not open data connection to port 53059: Connection timed out
221-Goodbye. You uploaded 0 and downloaded 0 kbytes.
221 Logout.
```

Wow I really thought that was going to work, until the last three lines. What's interesting is that it does upload an index.html file, just an empty one with a 0 kb size. So what's the deal. Googling and googling again, I found out it's a [problem with FTP active mode and firewalls](https://stackoverflow.com/questions/30771969/getting-could-not-open-data-connection-to-port-xxxx-when-uploading-file-to-ftp). That kind of leaves me in a pickle because that's out of my wheelhouse and potentially dangerous to get wrong. 

But wait, what's passive mode and how do I use that? [This article](https://www.jscape.com/blog/bid/80512/active-v-s-passive-ftp-simplified) goes into the differences between Active Mode and Passive Mode and then tries to sell you a product. [It turns out](https://stackoverflow.com/questions/18643542/how-to-use-passive-ftp-mode-in-windows-command-prompt) that passive mode is a simple flag when you open ftp, `-p`. I tacked it onto my ftp call in run.sh and voila!

```
220---------- Welcome to Pure-FTPd [privsep] [TLS] ----------
220-You are user number 4 of 500 allowed.
220-Local time is now 13:44. Server port: 21.
220-This is a private system - No anonymous login
220 You will be disconnected after 3 minutes of inactivity.
331 User  OK. Password required
230 OK. Current restricted directory is /
Hash mark printing on (1024 bytes/hash mark).
local: index.html remote: index.html
227 Entering Passive Mode (173,201,92,1,197,201)
150 Accepted data connection
##
226-File successfully transferred
226 0.036 seconds (measured here), 41.60 Kbytes per second
1635 bytes sent in 0.000645 seconds (2.42 Mbytes/s)
221-Goodbye. You uploaded 2 and downloaded 0 kbytes.
221 Logout.
```

Now for the challenge of uploading not only the index.html but also CSS, JavaScript and images. In the [original link](https://blog.eduonix.com/shell-scripting/how-to-automate-ftp-transfers-in-linux-shell-scripting/) I posted at the top, it lists the commands we can use to traverse the local and remote directories. In that way, we can write our bash script to go into the different folders and upload all the files inside of them, like so:

```
ftp -pinv $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
hash

mput *.html
mput *.md

cd css/
lcd css/
mput *.css

cd ../js/
lcd ../js/
mput *.js

cd ../img/
lcd ../img/
mput *.*

bye
END_SCRIPT
```

I tested this by deleting all the files through Filezilla, verifying I got a 404 page on the live site, then running run.sh, and verifying the HTML, CSS and image appear again on the live site. That's neat as hell. 

My QA sensibilities tell me there must be a better way to do this. Say what happens if I make a new directory? Or rename my files? I'll get into that in part 2.


[Continue Reading Part 2](/trips/quarantine/personal-website-deployment-2)