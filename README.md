# Accessing the website and admins, and running the server
Logging into the server:
`ssh ubuntu@filterbuddy.org`

Site URL:
https://filterbuddy.org/

Admin URL:
https://filterbuddy.org/admin/

Admin credentials are pinned on the project's Slack channel.

The website currently only allows pre-authorized emails to sign in.
If you want to log in using your YouTube credentials, contact project leads to
pre-authorize your email.

Test account:
`uwresearcher02@gmail.com`

Password and 2FA auth initialization codes for this account are this pinned on
the project's Slack channel.

# Making Code Contributions
You can work on the code either locally or on the server. Some things are
not available in the local environment

## Local Development
To develop locally, clone the repo, setup a virtual environment for django and
install necessary packages. Then run `python manage.py migrate` and
`python manage.py migrate --run-syncdb`.

Then make a file named `magic.local` at the root of this repository. The
existence of this file will cause the server to use a local database and skip
any YouTube authentication.

To clear the local database, delete `db.sqlite3` and rerun the migration
commands.

## Server Development
Some parts of the site require authentication with Google's API. To interact
with the Google API, you _must develop on the server_.

The server runs via `screen`. To view the console output or restart the server,
you need to do `screen -r`. If it complains about the screenn being `(Attached)`
someone else is logged on and viewing the server output. You can use `screen -x`
instead to enter a shared screen.

If you need to restart the server:
- If there is no screen session (server just rebooted), use `screen -S server`
    to start a fresh one.
- Enter the screen session and run `python3 manage.py runserver` from the repo
    root

You can code directly on the server (not recommended) via vim or if you want to
code in an editor other than vim, you can mount the server on your local machine
and use the editor of your choice using this:
https://www.digitalocean.com/community/tutorials/how-to-use-sshfs-to-mount-remote-file-systems-over-ssh

If you do code live on the server, please make sure to do one of the following
actions to keep the server environment clean:
- If making _temporary_ changes, make sure to `git checkout -- (...FILES)` to
    reset changed files to their original versions after your changes.
- If making _permanent_ changes, please create a new `branch` and make changes
    there

The server may need to be reset to the github `main` branch at any time without
notice. Any changes not recorded in a separate branch (including commits on
`main` on the server that have not been pushed to GH) will be lost.

# Django
If you are not familiar with Django, please check out this Django tutorial to learn the basics:
https://docs.djangoproject.com/en/3.2/intro/tutorial01/

It might help to review the code while going through this tutorial.
