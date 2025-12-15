# Tear Down Script for OpenAI Deployment Accounts and Model Deployments


# Query for all OpenAI deployment accounts in the subscription or resource group
$AIObjs = Get-AzResource -ResourceType "Microsoft.CognitiveServices/accounts"

# Get the model deployments for each OpenAI account and store them in an array
$AIObjArray = @()
foreach ($AIobj in $AIObjs) {
    $AIObjArray += Get-AzCognitiveServicesAccountDeployment `
        -ResourceGroupName $AIobj.ResourceGroupName `
        -AccountName $AIobj.Name
}

# Loop through each model deployment and delete it
foreach ($Deployment in $AIObjArray) {
    Remove-AzCognitiveServicesAccountDeployment -ResourceId $Deployment.Id -Force
    Write-Output "Deleted model deployment: $($Deployment.Name)"
}

# Loop through each OpenAI account and delete its child resources first
foreach ($account in $AIObjs) {
    # Find child resources under this account
    $childResources = Get-AzResource | Where-Object { $_.ResourceId -like "$($account.ResourceId)/*" }
    
    foreach ($child in $childResources) {
        Remove-AzResource -ResourceId $child.ResourceId -Force
        Write-Output "Deleted child resource: $($child.Name)"
    }

    # Delete the OpenAI account
    Remove-AzResource -ResourceId $account.ResourceId -Force
    Write-Output "Deleted OpenAI deployment account: $($account.Name)"
}