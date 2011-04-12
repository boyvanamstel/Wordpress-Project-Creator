# Overview

This tool contains a Python and PHP script to streamline working on Wordpress projects from your development machine.

Instead of editing files on your FTP server, wpprojectcreator allows you to easily work locally using an application like Mamp. By using Git to store your wp-content folder and a script to import database dumps, wprojectcreator makes it very easy to work together on the same Wordpress project.

> Notice: works well on OSX and Linux, works partially on Windows.

# What does it do exactly?

* Download Wordpress
* Create a new Git repo out of your wp-content folder
* or clone an existing wp-content folder into the Wordpress folder
* Easily imports database dumps by alterering absolute urls
* Create wp-config.php file
* Create .htaccess file

Adding new developers to your project is as easy as allowing them access to the Git repo and running wpprojectcreator.

## Getting started with a new project

1. Setup a new Git repo at GitHub or wherever.

2. Clone the Wordpress Project Creator into a new folder.
 
        $ git clone git@github.com:boyvanamstel/Wordpress-Project-Creator.git [your-new-wp-site]
 
3. Open a terminal and navigate to the folder that was just created.

4. Run wpprojectcreator.py using Python and append -n for a new repo.
 
		$ python wpprojectcreator.py -n
 
5. Watch while wpprojectcreator downloads the latest version of Wordpress and extracts the files.

6. Answer the questions.
 	
		Enter the remote host (e.g. git.hostname.nl): [your host]
		Enter the remote project (e.g. example-wpcontent): [yourproject]
 
7. Confirm and watch while wpprojectcreator sets up your new git repo and pushes the wp-content folder.

8. Open your new Wordpress site using Mamp in your browser and follow the wizard to setup your site.

9. Using phpmyadmin create a database dump of the site you just created, rename it to dump.sql en place it inside the wp-content folder.
 
		[your-new-wp-site]/wp-content/dump.sql
 
10. All set.

11. To sync the project after a new dump.sql has been added, follow the guide to continue an existing project, starting at step 7.

## Continue an existing project

1. Clone the Wordpress Project Creator into a new folder.
 
		$ git clone git@github.com:boyvanamstel/Wordpress-Project-Creator.git [your-existing-wp-site]
 
3. Open a terminal and navigate to the folder that was just created.

4. Run wpprojectcreator.py using Python.
 
		$ python wpprojectcreator.py
 
5. Watch while wpprojectcreator downloads the latest version of Wordpress and extracts the files.

6. Answer the questions.
 
		Enter the remote host (e.g. git.hostname.nl): [your host]
		Enter the remote project (e.g. example-wpcontent): [yourproject]
 
7. Confirm and watch while wpprojectcreator clones the existing repo into your project.

8. Open your favorite browser and visit the setup.php file located in [your-existing-wp-site].
 
		http://localhost:8888/[your-existing-wp-site]/setup.php
 
9. Fill out the form and press 'setup'. Wpprojectcreator will create wp-config.php, .htacces and import the existing dump.sql.

10. Press the link to 'website' and you're done.

## Include the [HTML5 Boilerplate theme](http://wordpress.org/extend/themes/boilerplate)

To automatically download and extract the latest version of the HTML5 Boilerplate theme into your themes folder append -b to the command.

    $ python wpprojectcreator.py -b

# Notice

If you plan on using Git to deploy your website. Make sure to create a .htacces in [your-wp-site]/wp-content that hides your .git folder and dump.sql file.
 
    <Files dump.sql>
        order deny,allow
        deny from all
    </Files>
	
    <DirectoryMatch .*\.git/.*>
        Order allow,deny
        Deny From All
    </DirectoryMatch>

