FUNCTION_APP_NAME="${FUNCTION_APP:-shwast-fun-app}"
cp -r backend-functions/ temp/
cp -r backend-shared/ temp/
cd temp/
func azure functionapp publish "$FUNCTION_APP_NAME"
