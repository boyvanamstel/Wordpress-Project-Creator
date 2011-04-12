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
try:
  import urllib.request
except:
  import urllib
import zipfile
import shutil

import sgmllib

class LinkParser(sgmllib.SGMLParser):
    "A simple parser class."

    def parse(self, s):
        "Parse the given string 's'."
        self.feed(s)
        self.close()

    def __init__(self, verbose=0):
        "Initialise an object, passing 'verbose' to the superclass."

        sgmllib.SGMLParser.__init__(self, verbose)
        self.hyperlinks = []

    def start_a(self, attributes):
        "Process a hyperlink and its 'attributes'."

        for name, value in attributes:
            if name == "href":
                self.hyperlinks.append(value)
                
    def get_hyperlinks(self):
        "Return the list of hyperlinks."

        return self.hyperlinks

# Project creator class
class WPProjectCreator(object):

  def __init__(self, dir = None, new = None, boilerplate = None, remote = None):
    
    # Set current directory
    if(dir == None):
      # Get cwd
      self.dir = os.getcwd()
    else:
      self.dir = dir  
    
    print('Current working dir: %s' % self.dir)
    
    # Properties
    self.new = new
    self.boilerplate = boilerplate
    self.remote = remote
    self.projectName = ''
    
    # Proceed with downloading Wordpress
    self.getWordpress()

    # Extract afterwards
    self.extractWordpress()
    
    # Get git location
    self.getGitLocation()
    
    # Run initial commands if new
    if(self.new != None):
      self.createGitRepo()
    else:
      self.getGitRepo()
    
    if(self.boilerplate != None):
      self.installBoilerplate()
    
    print('')
    print('DONE! - Use your webbrowser to install the database using the setup.php file')
    print('')
      
  def throwError(self, type, message, solution = None):
    if(type == 'notice'):
      print('= NOTICE : %s' % message)
    if(type == 'warning'):
      print('= WARNING  : %s' % message)
    if(type == 'error'):
      print('= ERROR    : %s' % message)
      if(solution != None):
        print('= SOLUTION : %s' % solution)
      sys.exit(2)

  def retrieving(self, count, blockSize = 0, totalSize = 0):
    curChar = count % 8
    progressChars = ['-','\\','|','/','-','\\','|','/']
    sys.stdout.write('Downloading.. %s' % progressChars[curChar])
    sys.stdout.write('\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b')
    sys.stdout.flush()

  def getWordpress(self):
    print('')
    print('- Download Wordpress')
    print('')
    
    if(os.path.isfile(os.path.join(self.dir, 'latest.zip'))):
      # Latest exists, check if wordpress folder exists, else extract

      self.throwError('notice','latest.zip archive exists')
      
      return False

    else:
      
      try:
        wordpress = urllib.request.urlretrieve('http://wordpress.org/latest.zip', os.path.join(self.dir, 'latest.zip'), self.retrieving)
        return True
        
      except:
        wordpress = urllib.urlopen('http://wordpress.org/latest.zip')
      
        output = open(os.path.join(self.dir, 'latest.zip'),'wb')
        chunkSize = 1024
        totalRead = ''
        counter = 0
        while True:
          chunk = wordpress.read(chunkSize)
          if not chunk: 
            wordpress.close()
            break
          totalRead += chunk
          self.retrieving(counter, chunkSize)
          counter += 1
  
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
      question = 'Enter the remote host (e.g. git.hostname.nl):'
      try:
        inputRemoteHost = raw_input(question)
      except:
        inputRemoteHost = input(question)
      
      question = 'Enter the remote project (e.g. example-wpcontent):'
      try:
        inputRemoteProject = raw_input(question)
      except:
        inputRemoteProject = input(question)
      
      # Append .git if it's missing
      inputRemoteLen = len(inputRemoteProject)
      if(inputRemoteProject.find('.git', inputRemoteLen - len('.git'), inputRemoteLen) == -1):
        inputRemoteProject = '%s.git' % inputRemoteProject
      
      # Define patterns
      patHostname = re.compile('^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$', re.I)
      patProject = re.compile('^[a-z0-9\-\_\.]{0,}$', re.I)

      # Stuff to get
      mHostname = patHostname.match(inputRemoteHost)
      mProject = patProject.match(inputRemoteProject)
      
      if(mHostname and mProject):
        question = 'We\'ll use this remote: git@%s:%s [y/n]' % (inputRemoteHost, inputRemoteProject)
        try:
          inputConfirm = raw_input(question)
        except:
          inputConfirm = input(question)
        
        if(inputConfirm != 'y'):
          self.getGitLocation()
      else:
        self.throwError('notice', 'Hostname or project name invalid')
        self.getGitLocation()
      
      self.projectName = inputRemoteProject
      self.remote = 'git@%s:%s' % (inputRemoteHost, inputRemoteProject)
      
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
      
      question = 'Run commands? [y/n]'
      try:
        confirm = raw_input(question)
      except:
        confirm = input(question)
      
      if(confirm == 'y'):
        os.chdir(os.path.join(self.dir, 'wordpress', 'wp-content'))
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
      print('git clone %s wp-content' % self.remote)
      #print('mv %s wp-content' % self.projectName)
      
      question = 'Run commands? [y/n]'
      try:
        confirm = raw_input(question)
      except:
        confirm = input(question)

      if(confirm == 'y'):
        os.chdir(os.path.join(self.dir, 'wordpress'))
        #os.system('rm -rf wp-content')
        shutil.rmtree(os.path.join(self.dir, 'wordpress', 'wp-content'))
        os.system('git clone %s wp-content' % self.remote)
        #os.system('mv %s wp-content' % self.projectName)
        #os.rename(os.path.join(self.dir, 'wordpress/%s' % self.projectName), os.path.join(self.dir, 'wordpress/wp-content'))
        return True
      else:
        self.throwError('error', 'Project creation aborted')
        return False
    
    else:
      self.throwError('error','Couldn\'t find wordpress directory')
      return False
      
  def installBoilerplate(self):
    
    # Get a file-like object for the Python Web site's home page.
    f = urllib.urlopen("http://wordpress.org/extend/themes/boilerplate")
    # Read from the object, storing the page's contents in 's'.
    s = f.read()
    f.close()

    link_parser = LinkParser()
    link_parser.parse(s)

    # Get the hyperlinks.
    for link in link_parser.get_hyperlinks():
      # Match with boilerplate url
      if(re.match('^http:\/\/wordpress\.org\/extend\/themes\/download\/boilerplate.[0-9\.]+\.zip', link)):
        self.downloadBoilerplate(link)
        self.extractBoilerplate()
        break
        
  def downloadBoilerplate(self, link):
    print('')
    print('- Download Boilerplate')
    print('')
      
    try:
      boilerplate = urllib.request.urlretrieve(link, os.path.join(self.dir, 'boilerplate-latest.zip'), self.retrieving)
      return True
      
    except:
      boilerplate = urllib.urlopen(link)
    
      output = open(os.path.join(self.dir, 'boilerplate-latest.zip'),'wb')
      chunkSize = 1024
      totalRead = ''
      counter = 0
      while True:
        chunk = boilerplate.read(chunkSize)
        if not chunk: 
          boilerplate.close()
          break
        totalRead += chunk
        self.retrieving(counter, chunkSize)
        counter += 1

      output.write(totalRead)
      output.close()
      
    print('Downloaded latest Boilerplate theme')
    
    return True
    
  def extractBoilerplate(self):
    print('')
    print('- Extract Boilerplate')
    print('')

    # Extract latest.zip
    wpZip = zipfile.ZipFile(os.path.join(self.dir, 'boilerplate-latest.zip'),'r')

    for name in wpZip.namelist():
      curItem = os.path.join(self.dir, 'wordpress', 'wp-content', 'themes', name)
      
      if name.endswith('/') and not os.path.exists(curItem):
        print('Creating dir %s' % name)
        os.mkdir(curItem)
      else:
        print('Extracting %s' % name)
        f = open(os.path.join(self.dir, 'wordpress', 'wp-content', 'themes', name), 'wb')
        f.write(wpZip.read(name))
        f.close()

    # Done extracting, remove zip file
    #os.remove(os.path.join(self.dir, 'boilerplate-latest.zip'))

    return True
    
  
# Run project creator with command line arguments
def main():
  try:                     
    args = sys.argv
    opts, args = getopt.getopt(args[1:], 'd:nr:b', ['dir=','new','remote=','boilerplate']) 
  except getopt.GetoptError:           
    print('usage: python wpprojectcreator.py [--dir /path] [--new] [--remote git@git.hostname.nl:example.git]\n')
    print('-d, --dir')
    print('   Directory to create the project in [.]')
    print('-n, --new')
    print('   Indicate this is an new project')
    print('-b, --boilerplate')
    print('   Automatically download HTML5 Boilerplate theme')
    print('-r, --remote')
    print('   Remote location [git@git.hostname.nl:example.git]')
    print('')
    sys.exit(2)
  
  dir = None
  new = None
  boilerplate = None
  remote = None
  for o, a in opts:
    if(o == '-d' or o == '--dir'):
      dir = a
    if(o == '-n' or o == '--new'):
      new = a
    if(o == '-b' or o == '--boilerplate'):
      boilerplate = a
    if(o == '-r' or o == '--remote'):
      remote = a

  projectCreator = WPProjectCreator(dir, new, boilerplate, remote)
  
# Run main
if(__name__ == '__main__'):
  main()
