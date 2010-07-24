<?php
/**
 * Wordpress config file creator and database importer
 *
 * @author Boy van Amstel
 * @copyright 2010 All rights reserved
 */

class WPProjectCreator {

	private $_errors = array();

	public function __construct($settings = array()) {
		
		// Copy settings
		$this->setSettings($settings);
		
	}
	
	public function setSettings($settings) {
		$this->_settings = $settings;
	}
	
	public static function getCurrentPageURL($stripFile = false) {
		$pageURL = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] == 'on' ? 'https://' : 'http://';
		
		$requestURI = $stripFile == true ? substr($_SERVER['REQUEST_URI'], 0, strrpos($_SERVER['REQUEST_URI'], '/')) : $_SERVER['REQUEST_URI'];
		
		$pageURL .= $_SERVER['SERVER_PORT'] != '80' ? $_SERVER["SERVER_NAME"].":".$_SERVER["SERVER_PORT"].$requestURI : $_SERVER['SERVER_NAME'] . $requestURI;
		return $pageURL;
	}
	
	public function getErrors() {
		return $this->_errors;
	}
	
	public function createDBConnection() {
		if($this->_link = mysql_connect($this->_settings['db_host'], $this->_settings['db_username'], $this->_settings['db_password'])) {
			return true;
		}
		return false;
	}
	
	public function createEmptyDatabase() {

		$link = $this->_link;
		$dbName = $this->_settings['db_name'];
		
		// Check if database exists, if not create it, else drop tables
		if(!mysql_select_db($dbName, $link)) { 
			// Create database
			$result = mysql_query(sprintf("CREATE DATABASE %s", $dbName), $link); 
			if(!$result) { 
				$this->_errors[] = sprintf('Could not create database %s', $dbName);
				return false; 
			}
			// Select database
			mysql_select_db($dbName);

			return true;
		} else {
			// Select database
			mysql_select_db($dbName);
			
			// Drop tables
			$succeeded = true;
			$results = mysql_query(sprintf('SHOW TABLES FROM %s', $dbName), $link);
			while($row = @mysql_fetch_assoc($results)) { 

				if(!mysql_query(sprintf('DROP TABLE %s', $row[sprintf('Tables_in_%s', $dbName)]))) {
					$this->_errors[] = sprintf('Failed to drop tables in %s: %s', $dbName, mysql_error());
					$succeeded = false;
					break;
				}
				
			}
			return $succeeded;
		}	
	}
	
	public function importDatabase() {
		
		$file = $this->_settings['db_dump'];
		$link = $this->_link;
		$url = $this->_settings['wp_url'];
		
		// Read file
		$lines = @file($file); 
		
		if(!$lines) { 
			$this->_errors[] = sprintf('Can not open file \'%s\'', $file); 
			return false; 
		} 
		
		// Strip comments and create single line
		$query = '';
		$queries = array();
		$originalUrl = '';
		foreach($lines as $line) { 
			$line = trim($line); 
			
			// Strip comments
			if(!ereg('^--', $line)) { 
				// Find original url, or replace if already found
				if($originalUrl == '') {
					$regex = "/INSERT INTO \`wp_options\` VALUES\([0-9]{0,}\, 0\, \'home\'\, \'(?P<url>[a-zA-Z0-9\:\-\.\/]{0,})\'\, \'[a-z]{2,3}\'\)\;/";
					preg_match($regex, $line, $matches);
					if(isset($matches['url'])) $originalUrl = $matches['url'];
				}
				$line = str_replace($originalUrl, $url, $line);

				$query .= "\n".$line; 
				
				if(substr($line, -1) == ';') {
					$queries[] = trim($query);
					$query = '';
				}
			}
	
		} 
		
		// Return error if the file is empty
		if(count($queries) == 0) { 
			$this->_errors[] = sprintf('File \'%s\' seems to be empty', $file); 
			return false; 
		} 
		
		// Run every line as a query
		foreach($queries as $query) { 
			//$query = trim($query);
			if($query == "") { continue; }
			if(!mysql_query($query.';', $link)) {
				$this->_errors[] = sprintf('Query \'%s\' failed: %s', $query, mysql_error());
				return false; 
			} 
		} 
		
		// Operation succeeded
		return true; 		

	}

}

?>