echo "Starting Client1..."
az vm start --name Client1 --resource-group MyResourceGroup

echo "Starting Client2..."
az vm start --name Client2 --resource-group MyResourceGroup

echo "Starting Client3..."
az vm start --name Client3 --resource-group MyResourceGroup

echo "Starting Middleware1..."
az vm start --name Middleware1 --resource-group MyResourceGroup

echo "Starting Middleware2..."
az vm start --name Middleware2 --resource-group MyResourceGroup

echo "Starting Server1..."
az vm start --name Server1 --resource-group MyResourceGroup

echo "Starting Server2..."
az vm start --name Server2 --resource-group MyResourceGroup

echo "Starting Server3..."
az vm start --name Server3 --resource-group MyResourceGroup
