<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Wordpress Project Creator - Setup</title>

<link rel="stylesheet" href="wpprojectcreator/css/reset.css" type="text/css" />
<link rel="stylesheet" href="wpprojectcreator/css/clearfix.css" type="text/css" />
<link rel="stylesheet" href="wpprojectcreator/css/style.css" type="text/css" />
<link rel="stylesheet" href="wpprojectcreator/css/enhanced.css" type="text/css" />

<script src="wpprojectcreator/js/jquery.js" type="text/javascript"></script>
<script src="wpprojectcreator/js/modernizr.js" type="text/javascript"></script>

<script src="wpprojectcreator/js/config.js" type="text/javascript"></script>
<script src="wpprojectcreator/js/scripts.js" type="text/javascript"></script>

</head>

<body id="index" class="home">
<div id="wrapper">

<?php
/**
 * Wordpress config file creator and database importer
 *
 * @author Boy van Amstel
 * @copyright 2010 All rights reserved
 */

require_once('wpprojectcreator/WPProjectCreator.php');


// Check if the base file exists, if not mention it
if(!file_exists('wordpress/wp-config-sample.php')) {
?>	

	<h1>Error - wp-config-sample.php unavailable</h1>
	<p class="error">It seems wp-config-sample.php doesn't exist. Did you run 'wpprojectcreator.py'? <a href="setup.php">retry</a></p>

<?php	
} else {
	?>
	<h1>Wordpress Project Creator - Setup</h1>
	<?php
	
	// Set settings
	$settings = array();
	
	$settings['wp_url'] = isset($_POST['wp_url']) ? $_POST['wp_url'] : WPProjectCreator::getCurrentPageURL(true).'/wordpress';
	$settings['db_name'] = isset($_POST['db_name']) ? $_POST['db_name'] : '';
	$settings['db_dump'] = isset($_POST['db_dump']) ? $_POST['db_dump'] : 'wordpress/wp-content/dump.sql';
	$settings['db_host'] = isset($_POST['db_host']) ? $_POST['db_host'] : 'localhost';
	$settings['db_username'] = isset($_POST['db_username']) ? $_POST['db_username'] : 'root';
	$settings['db_password'] =  isset($_POST['db_password']) ? $_POST['db_password'] : 'root';

	// If not submitting overwrite settings with existing settings
	if(!isset($_POST['setup_submit'])) {
		$existingSettings = file_exists('wordpress/wp-config.php') ? WPProjectCreator::readWPConfig() : array();
		$settings = array_merge($settings, $existingSettings);
	}

	if(isset($_POST['setup_submit'])) {
		
		// Check if data is set
		if(isset($_POST['wp_url']) &&
			isset($_POST['db_name']) &&
			isset($_POST['db_dump']) &&
			isset($_POST['db_host']) &&
			isset($_POST['db_username']) &&
			isset($_POST['db_password'])) {
				
				// Run setup
				$wpProjectCreator = new WPProjectCreator($settings);
				?><ul class="log"><?php
				?><li>Starting setup..</li><?php
				
				// Connect to database
				if($wpProjectCreator->createDBConnection()) {
					?><li>Connected to database</li><?php

					// Create empty database
					if($wpProjectCreator->createEmptyDatabase()) {
						?><li>Created new database, or removed old tables</li><?php

						// Import .sql file
						if($wpProjectCreator->importDatabase()) {
							?><li>Database imported</li><?php

							// Generate wp-config.php file
							if($wpProjectCreator->createWPConfig()) {
								?><li>Config file created</li><?php

								// Generate .htaccess file
								if($wpProjectCreator->createHTAccess()) {
									?><li>.htaccess file created, proceed to <a href="<?php echo $settings['wp_url']; ?>">website</a></li><?php
								}
							}
						}
					}
				}

				// Display errors
				if(count($wpProjectCreator->getErrors()) > 0) {
					foreach($wpProjectCreator->getErrors() as $error) {
						printf('<li class="error">%s</li>', $error);
					}
				}
				?></ul><?php
				
			} else {
				// Display error
				?>				
				<p class="error">Fill out the entire form.</p>
				<?php
			}
		
	}
	
?>

	<form action="setup.php" method="POST">
		<fieldset>
			<legend>Wordpress</legend>
			<dl class="clearfix">
				<dt><label for="wp_url">URL:</label></dt>
					<dd><input type="text" id="wp_url" name="wp_url" value="<?php echo $settings['wp_url']; ?>" /></dd>
		</fieldset>

		<fieldset>
			<legend>Database</legend>
			<dl class="clearfix">
				<dt><label for="db_name">Name:</label></dt>
					<dd><input type="text" id="db_name" name="db_name" value="<?php echo $settings['db_name']; ?>" /></dd>
				<dt><label for="db_host">Host:</label></dt>
					<dd><input type="text" id="db_host" name="db_host" value="<?php echo $settings['db_host']; ?>" /></dd>
				<dt><label for="db_username">Username:</label></dt>
					<dd><input type="text" id="db_username" name="db_username" value="<?php echo $settings['db_username']; ?>" /></dd>
				<dt><label for="db_password">Password:</label></dt>
					<dd><input type="text" id="db_password" value="<?php echo $settings['db_password']; ?>" name="db_password" /></dd>
				<dt><label for="db_dump">Dump:</label></dt>
					<dd><input type="text" id="db_dump" name="db_dump" value="<?php echo $settings['db_dump']; ?>" /></dd>
		</fieldset>
		
		<fieldset class="clearfix">
			<input type="submit" name="setup_submit" value="Setup" />
		</fieldset>
	</form>

<?php
}
?>

</div>
</body>
</html>