<?php
// Define the directory where files will be stored
$uploadDirectory = 'uploads/';

// Create the upload directory if it doesn't exist
if (!is_dir($uploadDirectory)) {
    mkdir($uploadDirectory, 0755, true);
}

// Check if the file was uploaded without errors
if (isset($_FILES['file']) && $_FILES['file']['error'] == UPLOAD_ERR_OK) {
    $fileTmpPath = $_FILES['file']['tmp_name'];
    $fileName = $_FILES['file']['name'];
    $fileSize = $_FILES['file']['size'];
    $fileType = $_FILES['file']['type'];
    $fileNameCmps = explode(".", $fileName);
    $fileExtension = strtolower(end($fileNameCmps));

    // Define allowed file extensions
    $allowedExts = ['jpg', 'jpeg', 'png', 'gif'];

    if (in_array($fileExtension, $allowedExts)) {
        // Get tenant name and encode it
        $tenantName = isset($_POST['tenant']) ? $_POST['tenant'] : 'default';
        $encodedTenantName = urlencode($tenantName);


        // Create a unique name for the file
        $newFileName = md5(time() . $fileName) . '.' . $fileExtension;
        $dest_path = $uploadDirectory . $encodedTenantName . '/food/' . $newFileName;

        // Create tenant directory if it doesn't exist
        if (!is_dir(dirname($dest_path))) {
            mkdir(dirname($dest_path), 0755, true);
        }

        // Move the file to the server
        if (move_uploaded_file($fileTmpPath, $dest_path)) {
            // Construct the URL for the uploaded file
            $fileUrl = 'http://techno3gamma.in/bucket/dineops/' . $dest_path;

            // Return the URL as a JSON response
            echo json_encode(['image_url' => $fileUrl], JSON_UNESCAPED_SLASHES);
        } else {
            // Return an error message
            http_response_code(500);
            echo json_encode(['error' => 'Failed to move the uploaded file.']);
        }
    } else {
        // Return an error message for invalid file extension
        http_response_code(400);
        echo json_encode(['error' => 'Invalid file type. Only jpg, jpeg, png, and gif are allowed.']);
    }
} else {
    // Return an error message if no file was uploaded or there was an error
    http_response_code(400);
    echo json_encode(['error' => 'No file uploaded or upload error.']);
}
?>