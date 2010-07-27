<?php
/**
 * Wordpress config file creator and database importer
 *
 * @author Boy van Amstel
 * @copyright 2010 All rights reserved
 */

/**
 * Wordpress Project Creator
 * Creates database, wp-config.php and imports database dump
 */
class WPProjectCreator {

	/**
	 * Array for storing errors
	 */
	private $_errors = array();

	/**
	 * Constructor sets settings
	 * @param array $settings
	 */
	public function __construct($settings = array()) {
		
		// Copy settings
		$this->setSettings($settings);
		
	}
	
	/**
	 * Sets settings
	 * @param array $settings
	 */
	public function setSettings($settings) {
		$this->_settings = $settings;
	}
	
	/**
	 * Static method for getting the current URL
	 * @param bool $stripFile
	 * @return string
	 */
	public static function getCurrentPageURL($stripFile = false) {
		$pageURL = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] == 'on' ? 'https://' : 'http://';
		
		$requestURI = $stripFile == true ? substr($_SERVER['REQUEST_URI'], 0, strrpos($_SERVER['REQUEST_URI'], '/')) : $_SERVER['REQUEST_URI'];
		
		$pageURL .= $_SERVER['SERVER_PORT'] != '80' ? $_SERVER["SERVER_NAME"].":".$_SERVER["SERVER_PORT"].$requestURI : $_SERVER['SERVER_NAME'] . $requestURI;
		return $pageURL;
	}

	/**
	 * Static method for getting the current rewrite base
	 * @param bool $stripFile
	 * @return string
	 */
	public static function getCurrentRewriteBase() {
		return substr($_SERVER['REQUEST_URI'], 0, strrpos($_SERVER['REQUEST_URI'], '/')) . '/wordpress/';
	}
	
	/**
	 * Get array with errors
	 * @return array
	 */
	public function getErrors() {
		return $this->_errors;
	}
	
	/**
	 * Create database connection
	 * @return bool
	 */
	public function createDBConnection() {
		if($this->_link = mysql_connect($this->_settings['db_host'], $this->_settings['db_username'], $this->_settings['db_password'])) {
			return true;
		}
		return false;
	}
	
	/**
	 * Create empty database
	 * Removes old tables, or creates new database
	 * @return bool
	 */
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

	/**
	 * Imports tables from SQL dump
	 * @return bool
	 */
	public function importDatabase() {
		
		$file = $this->_settings['db_dump'];
		$link = $this->_link;
		$url = $this->_settings['wp_url'];
		
		// Read database dump
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
					$regex = "/\, \'home\'\, \'(?P<url>[a-zA-Z0-9\:\-\.\/]{0,})\'\, \'[a-z]{2,3}\'\)/";
					preg_match($regex, $line, $matches);
					if(isset($matches['url'])) $originalUrl = $matches['url'];
				}
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
			if(!mysql_query(str_replace($originalUrl, urldecode($url), $query).';', $link)) {
				$this->_errors[] = sprintf('Query \'%s\' failed: %s', $query, mysql_error());
				return false; 
			} 
		} 
		
		// Operation succeeded
		return true; 		

	}

	/**
	 * Creates wp-config.php from wp-config-sample.php
	 * @return bool
	 */
	public function createWPConfig() {
	
		if(!file_exists('wordpress/wp-config-sample.php')) return false;
	
		$settings = $this->_settings;
	
		// Read sample config file
		$lines = @file('wordpress/wp-config-sample.php'); 
		
		if(!$lines) { 
			$this->_errors[] = sprintf('Can not open file \'%s\'', $file); 
			return false; 
		} 

		// Create final config file		
		$handle = fopen('wordpress/wp-config.php', 'w');

		// Get secret keys
		$secretKeys = file('https://api.wordpress.org/secret-key/1.1/salt/');
		
		// Read file, paste variables and save
		foreach($lines as $line) { 
			
			$find = array(
				"/define\(\'DB_NAME\'\, \'[a-zA-Z09\-\_]{1,}\'\)\;/",
				"/define\(\'DB_USER\'\, \'[a-zA-Z09\-\_]{1,}\'\)\;/",
				"/define\(\'DB_PASSWORD\'\, \'[a-zA-Z09\-\_]{1,}\'\)\;/",
				"/define\(\'DB_HOST\'\, \'[a-zA-Z09\-\_]{1,}\'\)\;/",
				"/define\(\'AUTH_KEY\'\,         \'put your unique phrase here\'\)\;/",
				"/define\(\'SECURE_AUTH_KEY\'\,  \'put your unique phrase here\'\)\;/",
				"/define\(\'LOGGED_IN_KEY\'\,    \'put your unique phrase here\'\)\;/",
				"/define\(\'NONCE_KEY\'\,        \'put your unique phrase here\'\)\;/",
				"/define\(\'AUTH_SALT\'\,        \'put your unique phrase here\'\)\;/",
				"/define\(\'SECURE_AUTH_SALT\'\, \'put your unique phrase here\'\)\;/",
				"/define\(\'LOGGED_IN_SALT\'\,   \'put your unique phrase here\'\)\;/",
				"/define\(\'NONCE_SALT\'\,       \'put your unique phrase here\'\)\;/"
				);

			$replace = array(
				sprintf("define('DB_NAME', '%s');", $settings['db_name']),
				sprintf("define('DB_USER', '%s');", $settings['db_username']),
				sprintf("define('DB_PASSWORD', '%s');", $settings['db_password']),
				sprintf("define('DB_HOST', '%s');", $settings['db_host']),
				$secretKeys[0],
				$secretKeys[1],
				$secretKeys[2],
				$secretKeys[3],
				$secretKeys[4],
				$secretKeys[5],
				$secretKeys[6],
				$secretKeys[7]				
				);
				
			// Write to file
			fwrite($handle, preg_replace($find, $replace, $line));
	
		} 
		
		// Close file
		fclose($handle);
		
		return true;
	}

	public function createHTAccess() {
		
		// Open file
		$handle = fopen('wordpress/.htaccess', 'w');
		
		// Set content
		$content = '
# BEGIN WordPress
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteBase [rewritebase]
RewriteRule ^index\.php$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . [rewritebase]index.php [L]
</IfModule>

# END WordPress
';
		
		// Write content
		fwrite($handle, str_replace('[rewritebase]', $this->getCurrentRewriteBase(), $content));
		
		// Close file
		fclose($handle);

		return true;
		
	}

	/**
	 * Read existing wp-config.php
	 * @return array
	 */
	public static function readWPConfig() {
		
		// Open existing config file	
		$handle = fopen('wordpress/wp-config.php', 'r');
		
		// Read contents
		$contents = fread($handle, filesize('wordpress/wp-config.php'));
		
		// Get database name
		preg_match_all("/(define\(\'(DB_NAME|DB_USER|DB_PASSWORD|DB_HOST)\'\, \'(([a-zA-Z09\-\_]{1,}?))\'\)\;)/", $contents, $matches);
		
		return array(
			"db_name" => $matches[3][0],
			"db_username" => $matches[3][1],
			"db_password" => $matches[3][2],
			"db_host" => $matches[3][3]
			);		
	
	}

}

?>