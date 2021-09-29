# Accessing the website and admins, and running the server
Logging into the server:
ssh ubuntu@wordfilters.railgun.in 

Site URL:
https://wordfilters.railgun.in/

Admin URL:
https://wordfilters.railgun.in/admin/

Admin credentials are pinned on the project's Slack channel.

The website currently only allows pre-authorized emails to sign in. If you want to log in using your YouTube credentials, contact project leads to pre-authorize your email.

Test account:
uwresearcher01@gmail.com

Password for this is this pinned on the project's Slack channel.

# Coding on the Server
Since this site requires authentication with Google's API, I haven't yet figures out a way to develop this in a local environment. For now, make your code changes directly on the server. 
If you want to code in an editor other than vim, you can mount the server on your local machine and use the editor of your choice using this:
https://www.digitalocean.com/community/tutorials/how-to-use-sshfs-to-mount-remote-file-systems-over-ssh 
