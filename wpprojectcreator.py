#!/usr/bin/env python
#
# Copyright 2010, Boy van Amstel
# All rights reserved.
#

# Project creator
import getopt
import sys
import os
import os.path
import re
import urllib
import zipfile
import shutil

# Git
#sys.path.append("./wpprojectcreator")
#from git import *

# Project creator class
class WPProjectCreator(object):

	def __init__(self, dir = None, new = 'n', remote = None):
		
		# Set current directory
		if(dir == None):
			# Get cwd
			self.dir = os.getcwd()
		else:
			self.dir = dir	
		
		print('Current working dir: %s' % self.dir)
		
		# Properties
		self.new = new
		self.remote = remote
		self.projectName = ''
		
		# Proceed with downloading Wordpress
		self.getWordpress()

		# Extract afterwards
		self.extractWordpress()
		
		# Get git location
		self.getGitLocation()
		
		# Run initial commands if new
		if(self.new == 'y'):
			self.createGitRepo()
		else:
			self.getGitRepo()
		
		print('')
		print('DONE! - Use your webbrowser to install the database using the setup.php file')
		print('')
			
	def throwError(self, type, message, solution = None):
		if(type == 'notice'):
			print('= NOTICE	: %s' % message)
		if(type == 'warning'):
			print('= WARNING	: %s' % message)
		if(type == 'error'):
			print('= ERROR		: %s' % message)
			if(solution != None):
				print('= SOLUTION	: %s' % solution)
			sys.exit(2)

	def getWordpress(self):
		print('')
		print('- Download Wordpress')
		print('')
		
		if(os.path.isfile(os.path.join(self.dir, 'latest.zip'))):
			# Latest exists, check if wordpress folder exists, else extract

			self.throwError('notice','latest.zip archive exists')
			
			return False

		else:
			
			wordpress = urllib.urlopen('http://wordpress.org/latest.zip')
			output = open(os.path.join(self.dir, 'latest.zip'),'wb')
			chunkSize = 1024
			totalRead = ''
			progressChars = ['-','\\','|','/','-','\\','|','/']
			curChar = 0
			while True:
				chunk = wordpress.read(chunkSize)
				if not chunk: 
					wordpress.close()
					break
				totalRead += chunk
				sys.stdout.write('Downloading.. %s' % progressChars[curChar])
				sys.stdout.write('\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b')
				sys.stdout.flush()
				curChar += 1
				if(curChar >= len(progressChars)):
					curChar = 0
				#yield chunk			

			output.write(totalRead)
			output.close()
			
			print('Downloaded latest Wordpress archive')
			
			return True
	
	def extractWordpress(self):
		print('')
		print('- Extract Wordpress')
		print('')
		
		if(os.path.isdir(os.path.join(self.dir, 'wordpress'))):
			# Wordpress folder exists, fail
			self.throwError('error', 'wordpress folder already exists', 'Delete or rename and retry')
			
			return False
			
		else:
			# Extract latest.zip
			wpZip = zipfile.ZipFile(os.path.join(self.dir, 'latest.zip'),'r')
			
			for name in wpZip.namelist():
				curItem = os.path.join(self.dir, name)
			
				if name.endswith('/') and not os.path.exists(curItem):
					print('Creating dir %s' % name)
					os.mkdir(curItem)
				else:
					print('Extracting %s' % name)
					f = open(os.path.join(self.dir, name), 'wb')
					f.write(wpZip.read(name))
					f.close()
			
			# Done extracting, remove zip file
			#os.remove(os.path.join(self.dir, 'latest.zip'))
			
			return True
			
	def getGitLocation(self):
		print('')
		print('- Define Git repository location')
		print('')
		
		if(self.remote == None):
			inputRemoteHost = raw_input('Enter the remote host (e.g. git.hostname.nl):')
			inputRemoteProject = raw_input('Enter the remote project (e.g. example-wpcontent):')
			
			# Define patterns
			patHostname = re.compile('^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$', re.I)
			patProject = re.compile('^[a-z\-]{0,}$', re.I)

			# Stuff to get
			mHostname = patHostname.match(inputRemoteHost)
			mProject = patProject.match(inputRemoteProject)
			
			if(mHostname and mProject):
				inputConfirm = raw_input('We\'ll use this remote: git@%s:%s.git [y/n]' % (inputRemoteHost, inputRemoteProject))
				
				if(inputConfirm != 'y'):
					self.getGitLocation()
			else:
				self.throwError('notice', 'Hostname or project name invalid')
				self.getGitLocation()
			
			self.projectName = inputRemoteProject
			self.remote = 'git@%s:%s.git' % (inputRemoteHost, inputRemoteProject)
			
			return True
		
	def createGitRepo(self):
		print('')
		print('- Create Git repository')
		print('')
		
		if(os.path.isdir(os.path.join(self.dir, 'wordpress/wp-content'))):
			
			print('cd wordpress/wpcontent')
			print('git init')
			print('git add .')
			print('git commit -m "initial import"')
			print('git remote add origin %s' % self.remote)
			print('git push origin master')
			confirm = raw_input('Run commands? [y/n]')
			
			if(confirm == 'y'):
				os.chdir(os.path.join(self.dir, 'wordpress/wp-content'))
				os.system('git init')
				os.system('git add .')
				os.system('git commit -m "initial import"')
				os.system('git remote add origin %s' % self.remote)
				os.system('git push origin master')
				
				return True
			else:
				self.throwError('error', 'Project creation aborted')
				return False
	
		else:
			self.throwError('error','Couldn\'t find wordpress/wp-content directory')
			return False
		
	def getGitRepo(self):
		print('')
		print('- Get Git repository')
		print('')
		
		if(os.path.isdir(os.path.join(self.dir, 'wordpress'))):
		
			os.chdir(os.path.join(self.dir, 'wordpress'))
			
			print('cd wordpress')
			print('rm -rf wp-content')
			print('git clone %s' % self.remote)
			print('mv %s wp-content' % self.projectName)
			confirm = raw_input('Run commands? [y/n]')

			if(confirm == 'y'):
				os.chdir(os.path.join(self.dir, 'wordpress'))
				#os.system('rm -rf wp-content')
				shutil.rmtree(os.path.join(self.dir, 'wordpress/wp-content'))
				os.system('git clone %s' % self.remote)
				#os.system('mv %s wp-content' % self.projectName)
				os.rename(os.path.join(self.dir, 'wordpress/%s' % self.projectName), os.path.join(self.dir, 'wordpress/wp-content'))
				return True
			else:
				self.throwError('error', 'Project creation aborted')
				return False
		
		else:
			self.throwError('error','Couldn\'t find wordpress directory')
			return False
		
	
# Run project creator with command line arguments
def main():
	try:                     
		args = sys.argv
		opts, args = getopt.getopt(args[1:], 'd:n:r:', ['dir=','new=','remote=']) 
	except getopt.GetoptError:           
		print('usage: python wpprojectcreator.py [--dir] [--username] [--password] [--key] [--id]\n')
		print('-d, --dir')
		print('		Directory to create the project in [.]')
		print('-n, --new')
		print('		Indicate this is an new project [n]')
		print('-r, --remote')
		print('		Remote location [git@git.hostname.nl:example.git]')
		print('')
		sys.exit(2)
	
	dir = None
	new = None
	remote = None
	for o, a in opts:
		if(o == '-d' or o == '--dir'):
			dir = a
		if(o == '-n' or o == '--new'):
			new = a
		if(o == '-r' or o == '--remote'):
			remote = a

	projectLister = WPProjectCreator(dir, new, remote)
	
# Run main
if(__name__ == '__main__'):
	main()
