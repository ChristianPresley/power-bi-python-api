# Install and import Microsoft Graph module for PowerShell
# Install-Module Microsoft.Graph
# Import-Module Microsoft.Graph

# The App Registration (Service Principal) for which consent is being granted
$clientAppId = "4b64746b-957d-42d7-8fb5-0defe36711f3"

# Power BI Service App ID
$resourceAppId = "00000009-0000-0000-c000-000000000000"

# All Power BI Read/Write Permissions
$permissions = @(
    "App.Read.All",
    "Capacity.Read.All",
    "Capacity.ReadWrite.All",
    "Content.Create",
    "Dashboard.Read.All",
    "Dashboard.ReadWrite.All",
    "Dataflow.Read.All",
    "Dataflow.ReadWrite.All",
    "Dataset.Read.All",
    "Dataset.ReadWrite.All",
    "Gateway.Read.All",
    "Gateway.ReadWrite.All",
    "Pipeline.Deploy",
    "Pipeline.Read.All",
    "Pipeline.ReadWrite.All",
    "Report.Read.All",
    "Report.ReadWrite.All",
    "StorageAccount.Read.All",
    "StorageAccount.ReadWrite.All",
    "Tenant.Read.All",
    "Tenant.ReadWrite.All",
    "UserState.ReadWrite.All",
    "Workspace.Read.All",
    "Workspace.ReadWrite.All"
)

# Service Account UPN
$userUpnOrId = "powerbi@m365x51939963.onmicrosoft.com"

# Connect to Microsoft Graph (Admin Permissions Required)
Connect-MgGraph -Scopes ("User.ReadBasic.All Application.ReadWrite.All " `
                        + "DelegatedPermissionGrant.ReadWrite.All " `
                        + "AppRoleAssignment.ReadWrite.All")

# Retrieve App Registration (Service Principal) from Microsoft Graph
$clientSp = Get-MgServicePrincipal -Filter "appId eq '$($clientAppId)'"


# Create a delegated permission that grants the client app access to the
# API, on behalf of the user. (This example assumes that an existing delegated 
# permission grant does not already exist, in which case it would be necessary 
# to update the existing grant, rather than create a new one.)
$user = Get-MgUser -UserId $userUpnOrId
$resourceSp = Get-MgServicePrincipal -Filter "appId eq '$($resourceAppId)'"
$scopeToGrant = $permissions -join " "
$grant = New-MgOauth2PermissionGrant -ResourceId $resourceSp.Id `
                                     -Scope $scopeToGrant `
                                     -ClientId $clientSp.Id `
                                     -ConsentType "Principal" `
                                     -PrincipalId $user.Id

# Assign the app to the user. This ensures that the user can sign in if assignment
# is required, and ensures that the app shows up under the user's My Apps.
if ($clientSp.AppRoles | ? { $_.AllowedMemberTypes -contains "User" }) {
    Write-Warning ("A default app role assignment cannot be created because the " `
        + "client application exposes user-assignable app roles. You must " `
        + "assign the user a specific app role for the app to be listed " `
        + "in the user's My Apps access panel.")
} else {
# The app role ID 00000000-0000-0000-0000-000000000000 is the default app role
# indicating that the app is assigned to the user, but not for any specific 
# app role.
    $assignment = New-MgServicePrincipalAppRoleAssignedTo `
        -ServicePrincipalId $clientSp.Id `
        -ResourceId $clientSp.Id `
        -PrincipalId $user.Id `
        -AppRoleId "00000000-0000-0000-0000-000000000000"
}