echo "Stopping Client1..."
az vm deallocate --name Client1 --resource-group MyResourceGroup

echo "Stopping Client2..."
az vm deallocate --name Client2 --resource-group MyResourceGroup

echo "Stopping Client3..."
az vm deallocate --name Client3 --resource-group MyResourceGroup

echo "Stopping Middleware1..."
az vm deallocate --name Middleware1 --resource-group MyResourceGroup

echo "Stopping Middleware2..."
az vm deallocate --name Middleware2 --resource-group MyResourceGroup

echo "Stopping Server1..."
az vm deallocate --name Server1 --resource-group MyResourceGroup

echo "Stopping Server2..."
az vm deallocate --name Server2 --resource-group MyResourceGroup

echo "Stopping Server3..."
az vm deallocate --name Server3 --resource-group MyResourceGroup
