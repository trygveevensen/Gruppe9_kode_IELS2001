<?php
// ALL php kode skrevet av ChatGPT
if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $data = isset($_POST['data']) ? trim($_POST['data']) : '';
    $timestamp = time(); // seconds since Unix epoch
    $line = $data . ',' . $timestamp . "\n";

    // Overwrite the file each time
    file_put_contents(__DIR__ . '/sleeptime.txt', $line);

    echo "Data saved!";
    exit;
}

