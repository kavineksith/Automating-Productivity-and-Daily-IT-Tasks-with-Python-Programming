# List of WMI modules with their index and availability status
$module_list = @(
    @{ Index = 1; Name = "Win32_OperatingSystem"; Available = $true },
    @{ Index = 2; Name = "Win32_ComputerSystem"; Available = $true },
    @{ Index = 3; Name = "Win32_Processor"; Available = $true },
    @{ Index = 4; Name = "Win32_PhysicalMemory"; Available = $true },
    @{ Index = 5; Name = "Win32_LogicalMemoryConfiguration"; Available = $false },
    @{ Index = 6; Name = "Win32_DiskDrive"; Available = $true },
    @{ Index = 7; Name = "Win32_DiskPartition"; Available = $true },
    @{ Index = 8; Name = "Win32_LogicalDisk"; Available = $true },
    @{ Index = 9; Name = "Win32_NetworkAdapterConfiguration"; Available = $true },
    @{ Index = 10; Name = "Win32_Battery"; Available = $true },
    @{ Index = 11; Name = "Win32_Process"; Available = $true },
    @{ Index = 12; Name = "Win32_Service"; Available = $true },
    @{ Index = 13; Name = "Win32_NTLogEvent"; Available = $true },
    @{ Index = 14; Name = "Win32_Fan"; Available = $true },
    @{ Index = 15; Name = "Win32_TemperatureProbe"; Available = $true },
    @{ Index = 16; Name = "Win32_LogonSession"; Available = $true },
    @{ Index = 17; Name = "Win32_GroupPolicyObject"; Available = $false }
)

# Function to display the module list
function Show-ModuleList {
    Write-Host "Available WMI Modules:"
    foreach ($module in $module_list) {
        if ($module.Available) {
            Write-Host ("{0,2}: {1}" -f $module.Index, $module.Name)
        } else {
            Write-Host ("{0,2}: {1} (Not available for current Windows OS version)" -f $module.Index, $module.Name)
        }
    }
    Write-Host ""
}

# Function to get module by index
function Get-ModuleByIndex {
    param (
        [int]$index
    )
    $module = $module_list | Where-Object { $_.Index -eq $index }
    if ($module) {
        return $module.Name
    } else {
        throw "Module index $index is not valid."
    }
}

# Show module list
Show-ModuleList

# Prompt user for selection
try {
    [int]$userChoice = Read-Host "Please enter the number corresponding to a Win32 Module"

    # Validate selection and get module
    if ($userChoice -ge 1 -and $userChoice -le $module_list.Count) {
        $select_method = Get-ModuleByIndex -index $userChoice
        Write-Host "Selected Method: $select_method"
        try {
            Get-CimInstance -ClassName $select_method
        } catch {
            Write-Host "Error retrieving data for $select_method. Details: $_"
        }
    } else {
        Write-Host "Invalid selection. Please enter a number between 1 and $($module_list.Count)."
    }
} catch {
    Write-Host "An error occurred: $_"
}
