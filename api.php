<?php

header("Content-Type: application/json");

$data = json_decode(file_get_contents("php://input"), true);

$email = $data["email"] ?? "";

if(!filter_var($email, FILTER_VALIDATE_EMAIL)){
echo json_encode(["message"=>"❌ Email not valid"]);
exit;
}

$file = "emails.json";

$emails = [];

if(file_exists($file)){
$emails = json_decode(file_get_contents($file), true);
}

if(!in_array($email,$emails)){
$emails[] = $email;
file_put_contents($file,json_encode($emails,JSON_PRETTY_PRINT));
echo json_encode(["message"=>"✅ Successfully Subscribed"]);
}else{
echo json_encode(["message"=>"⚠ Email already exists"]);
}

?>