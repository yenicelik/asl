echo "Restarting Client1..."
az vm restart --name Client1 --resource-group yedavid

echo "Restarting Client2..."
az vm restart --name Client2 --resource-group yedavid

echo "Restarting Client3..."
az vm restart --name Client3 --resource-group yedavid

echo "Restarting Middleware1..."
az vm restart --name Middleware1 --resource-group yedavid

echo "Restarting Middleware2..."
az vm restart --name Middleware2 --resource-group yedavid

echo "Restarting Server1..."
az vm restart --name Server1 --resource-group yedavid

echo "Restarting Server2..."
az vm restart --name Server2 --resource-group yedavid

echo "Restarting Server3..."
az vm restart --name Server3 --resource-group yedavid
