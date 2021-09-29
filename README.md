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
This site requires authentication with Google's API. I haven't yet figured out a way to develop this in a local environment. For now, make your code changes directly on the server. 

If you want to code in an editor other than vim, you can mount the server on your local machine and use the editor of your choice using this:
https://www.digitalocean.com/community/tutorials/how-to-use-sshfs-to-mount-remote-file-systems-over-ssh 

Note that the server is running in a `screen'. You may need to restart the server to observe some of your changes. To do this, use 'screen -r' on the server, use ctrl+c to stop the server and use 'python manage.py runserver' to start it.

# Django
If you are not familiar with Django, please check out this Django tutorial to learn the basics:
https://docs.djangoproject.com/en/3.2/intro/tutorial01/ 

It might help to review the code while going through this tutorial.
