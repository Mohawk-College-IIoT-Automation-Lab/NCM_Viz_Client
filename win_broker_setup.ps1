# Replace this with the actual IP of your WSL instance
$WSL_IP = "172.28.45.123"

# Port forwarding from Windows port 1883 to WSL
netsh interface portproxy add v4tov4 `
    listenport=1883 `
    listenaddress=0.0.0.0 `
    connectport=1883 `
    connectaddress=$WSL_IP

# Allow port 1883 through Windows Firewall
New-NetFirewallRule -DisplayName "Mosquitto MQTT" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 1883 `
    -Action Allow

Write-Host "Port forwarding set to $WSL_IP:1883"