<?php
    $config = parse_ini_file("C:\\FireGUARD\settings.ini", true);
?>
<div align="center" style='color: black'>
    <?php echo($config['FireGUARD']['active_offer']) ?> <a href='mailto:<?php echo($config['FireGUARD']['email']) ?>?subject=WeatherSHIELD Issue'><?php echo($config['FireGUARD']['email']) ?></a>
</div>
