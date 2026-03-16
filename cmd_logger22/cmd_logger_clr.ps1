# 设置控制台编码为 UTF-8
chcp 65001 > $null

$historyFile = "history_clr.log"

# 显示历史内容
if (Test-Path $historyFile) {
    Write-Host "`n===== Command History =====`n"
    Get-Content $historyFile -Encoding UTF8
    Write-Host "`n===== Enter Commands Below =====`n"
}

# 主循环：读取用户输入 + 执行 + 记录
while ($true) {
    $cmd = Read-Host -Prompt "PS >"
    
    if ($cmd -eq "exit") {
        Write-Host "`nExiting and saving session..." -ForegroundColor Cyan
        break
    }

    try {
        $output = Invoke-Expression $cmd 2>&1
    } catch {
        $output = $_.Exception.Message
    }

    Write-Output $output

    # 写入日志，使用 UTF-8 编码
    Add-Content -Path $historyFile -Value "`nPS > $cmd" -Encoding UTF8
    $output | ForEach-Object { Add-Content -Path $historyFile -Value $_ -Encoding UTF8 }
}
