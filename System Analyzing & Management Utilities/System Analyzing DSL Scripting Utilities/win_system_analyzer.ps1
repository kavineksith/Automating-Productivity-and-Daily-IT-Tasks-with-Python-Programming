$module_list = @(
    "Win32_OperatingSystem", 
    "Win32_ComputerSystem", 
    "Win32_Processor", 
    "Win32_PhysicalMemory",
    "Win32_LogicalMemoryConfiguration", # Not available for current windows os version
    "Win32_DiskDrive", 
    "Win32_DiskPartition", 
    "Win32_LogicalDisk", 
    "Win32_NetworkAdapterConfiguration", 
    "Win32_Battery", 
    "Win32_Process", 
    "Win32_Service", 
    "Win32_NTLogEvent", 
    "Win32_Fan", 
    "Win32_TemperatureProbe", 
    "Win32_LogonSession",
    "Win32_GroupPolicyObject" # Not available for current windows os version
    )

    [int]$index_number = 1

    foreach ($select_module in $module_list) {
        Write-Host "Index Number $index_number Module: $select_module"
        $index_number+=1 # increment index value unitl reach last value
    }

    Write-Host " "

    [int]$userChoice = Read-Host "Please enter number corresponding to Win32 Module"
    Write-Host "Selected Value: $userChoice"

    switch ($userChoice) {
        1 { $select_method = $module_list[0] }
        2 { $select_method = $module_list[1] }
        3 { $select_method = $module_list[2] }
        4 { $select_method = $module_list[3] }
        5 { $select_method = $module_list[4] }
        6 { $select_method = $module_list[5] }
        7 { $select_method = $module_list[6] }
        8 { $select_method = $module_list[7] }
        9 { $select_method = $module_list[8] }
        10 { $select_method = $module_list[9] }
        11 { $select_method = $module_list[10] }
        12 { $select_method = $module_list[11] }
        13 { $select_method = $module_list[12] }
        14 { $select_method = $module_list[13] }
        15 { $select_method = $module_list[14] }
        16 { $select_method = $module_list[15] }
        17 { $select_method = $module_list[16] }
        Default { Write-Host "Please enter valid number" }
    }

    Write-Host "Selected Method: $select_method"
    Get-CimInstance -ClassName $select_method