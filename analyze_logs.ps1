# analyze_logs.ps1
# Native PowerShell script to analyze all 120 Honeypot research logs
# and generate Table 1 and Table 2 for the research paper.

$ErrorActionPreference = "SilentlyContinue"

$ScriptDir = $PSScriptRoot
if (-not $ScriptDir) { $ScriptDir = (Get-Location).Path }
Set-Location $ScriptDir

Write-Host "Base Directory: $ScriptDir"
Write-Host "=================================================================="
Write-Host "EMPIRICAL ANALYSIS OF 120 SYNTHETIC HONEYPOT SESSIONS (POWERSHELL)"
Write-Host "=================================================================="

$conditions = @(
    @{ Model = "DeepSeek-V3.2"; Backend = "Static Cowrie"; Path = (Join-Path $ScriptDir "logs\deepseek") },
    @{ Model = "DeepSeek-V3.2"; Backend = "Dynamic Qwen-32B"; Path = (Join-Path $ScriptDir "logs\deepseek_vs_qwen.qwen3-32b") },
    @{ Model = "Gemma-3-4B"; Backend = "Static Cowrie"; Path = (Join-Path $ScriptDir "logs\gemma") },
    @{ Model = "Gemma-3-4B"; Backend = "Dynamic Qwen-32B"; Path = (Join-Path $ScriptDir "logs\gemma_vs_qwen.qwen3-32b") },
    @{ Model = "GPT-OSS-120B"; Backend = "Static Cowrie"; Path = (Join-Path $ScriptDir "logs\gptoss") },
    @{ Model = "GPT-OSS-120B"; Backend = "Dynamic Qwen-32B"; Path = (Join-Path $ScriptDir "logs\gptoss_vs_qwen.qwen3-32b") }
)

$reconPatterns = @("whoami", "id", "uname", "hostname", "ifconfig", "ip a", "ps ", "netstat", "ls ", "ls`$", "pwd", "uptime", "env", "df", "free", "cat /proc")
$credPatterns = @("passwd", "shadow", "\.ssh", "id_rsa", "authorized_keys", "history", "secret", "credential", "key", "\.my\.cnf")
$privPatterns = @("sudo", "su ", "-perm -4000", "-perm -2000", "visudo", "getcap", "pkexec")
$persistPatterns = @("crontab", "\.bashrc", "\.profile", "useradd", "adduser", "chmod \+s", "systemctl enable", "rc\.local")
$exfilPatterns = @("wget", "curl", "scp", "nc ", "ftp", "tftp", "base64")

$results = @{}
$allNormalized = @()

foreach ($cond in $conditions) {
    $dirPath = $cond.Path
    $files = Get-ChildItem -Path $dirPath -Filter "*.json"
    $count = $files.Count
    
    $turnCounts = @()
    $commands = @()
    $latencies = @()
    $reconCount = 0
    $credCount = 0
    $privCount = 0
    $persistCount = 0
    $exfilCount = 0
    $statuses = @{}

    foreach ($file in $files) {
        $raw = Get-Content -Path $file.FullName -Raw -Encoding UTF8
        try {
            $sess = ConvertFrom-Json $raw
        } catch {
            continue
        }

        $st = $sess.status
        if (-not $statuses.ContainsKey($st)) { $statuses[$st] = 0 }
        $statuses[$st]++

        $turns = $sess.turns
        $tCount = if ($turns) { $turns.Count } else { 0 }
        $turnCounts += $tCount

        $sessCmds = @()
        if ($turns) {
            foreach ($t in $turns) {
                $cmd = $t.command
                if (-not $cmd -and $t.raw_response) {
                    $rawCmd = $t.raw_response.Trim()
                    if ($rawCmd -match "[\/\-\|\$\s]") { $cmd = $rawCmd }
                }
                if ($cmd) {
                    $commands += $cmd
                    $sessCmds += $cmd
                    $cmdLower = $cmd.ToLower()

                    if ($reconPatterns | Where-Object { $cmdLower -match $_ }) { $reconCount++ }
                    if ($credPatterns | Where-Object { $cmdLower -match $_ }) { $credCount++ }
                    if ($privPatterns | Where-Object { $cmdLower -match $_ }) { $privCount++ }
                    if ($persistPatterns | Where-Object { $cmdLower -match $_ }) { $persistCount++ }
                    if ($exfilPatterns | Where-Object { $cmdLower -match $_ }) { $exfilCount++ }
                }
                if ($t.latency_sec) {
                    $latencies += [double]$t.latency_sec
                }
            }
        }

        # Normalize session
        $normObj = [PSCustomObject]@{
            session_id = $sess.session_id
            attacker_model = $cond.Model
            honeypot_backend = $cond.Backend
            status = $sess.status
            total_turns = $tCount
            command_count = $sessCmds.Count
            commands = $sessCmds
            started_at = $sess.started_at
            ended_at = $sess.ended_at
        }
        $allNormalized += $normObj
    }

    $meanTurns = if ($turnCounts.Count -gt 0) { ($turnCounts | Measure-Object -Average).Average } else { 0 }
    $meanLat = if ($latencies.Count -gt 0) { ($latencies | Measure-Object -Average).Average } else { 0 }
    $uniqueCmds = ($commands | Select-Object -Unique).Count

    $condKey = "$($cond.Model) | $($cond.Backend)"
    $results[$condKey] = @{
        Model = $cond.Model
        Backend = $cond.Backend
        Sessions = $count
        MeanTurns = [Math]::Round($meanTurns, 1)
        TotalCmds = $commands.Count
        UniqueCmds = $uniqueCmds
        MeanLatency = [Math]::Round($meanLat, 2)
        ReconCount = $reconCount
        CredCount = $credCount
        PrivCount = $privCount
        PersistCount = $persistCount
        ExfilCount = $exfilCount
        Statuses = $statuses
    }

    Write-Host "`n[$condKey] -> $count Sessions"
    Write-Host "  Turns/Session: Mean = $([Math]::Round($meanTurns, 1))"
    Write-Host "  Total Commands: $($commands.Count) ($uniqueCmds Unique)"
    Write-Host "  Mean Latency: $([Math]::Round($meanLat, 2))s"
    Write-Host "  Recon: $reconCount, CredHunting: $credCount, PrivEsc: $privCount, Persistence: $persistCount, Exfil: $exfilCount"
}

# Generate Markdown Document
$md = @()
$md += "# Empirical Findings: AI Red-Team Honeypot Datasets`n"
$md += "This document presents the complete empirical statistics extracted from the 120 experimental attacker-vs-honeypot sessions across three distinct model families (`DeepSeek-V3.2`, `Google Gemma-3-4B-IT`, `OpenAI GPT-OSS-120B`) and two honeypot architectural conditions (`Static Cowrie Shell` vs. `Dynamic LLM Qwen-32B`).`n"

$md += "## Table 1: Attacker Model Behavioral Comparison (Static Baseline)`n"
$md += "| Attacker Model | Sessions | Mean Turns | Total Commands | Unique Commands | Reconnaissance (%) | Credential Hunting (%) | PrivEsc (%) | Mean Latency |"
$md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"

foreach ($m in @("Gemma-3-4B", "DeepSeek-V3.2", "GPT-OSS-120B")) {
    $r = $results["$m | Static Cowrie"]
    $tot = if ($r.TotalCmds -gt 0) { $r.TotalCmds } else { 1 }
    $rPct = [Math]::Round(($r.ReconCount / $tot) * 100, 1)
    $cPct = [Math]::Round(($r.CredCount / $tot) * 100, 1)
    $pPct = [Math]::Round(($r.PrivCount / $tot) * 100, 1)
    $md += "| **$m** | $($r.Sessions) | $($r.MeanTurns) | $($r.TotalCmds) | $($r.UniqueCmds) | $rPct% | $cPct% | $pPct% | $($r.MeanLatency)s |"
}

$md += "`n## Table 2: Static Cowrie vs. Dynamic (LLM Qwen-32B) Honeypot Interaction`n"
$md += "| Attacker Model | Honeypot Backend | Mean Turns | Total Commands | Recon (%) | Credential (%) | Mean Latency | Latency Overhead |"
$md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"

foreach ($m in @("DeepSeek-V3.2", "Gemma-3-4B", "GPT-OSS-120B")) {
    $rs = $results["$m | Static Cowrie"]
    $rd = $results["$m | Dynamic Qwen-32B"]

    $totS = if ($rs.TotalCmds -gt 0) { $rs.TotalCmds } else { 1 }
    $totD = if ($rd.TotalCmds -gt 0) { $rd.TotalCmds } else { 1 }

    $rPctS = [Math]::Round(($rs.ReconCount / $totS) * 100, 1)
    $cPctS = [Math]::Round(($rs.CredCount / $totS) * 100, 1)
    $rPctD = [Math]::Round(($rd.ReconCount / $totD) * 100, 1)
    $cPctD = [Math]::Round(($rd.CredCount / $totD) * 100, 1)

    $overhead = if ($rs.MeanLatency -gt 0) {
        $pct = [Math]::Round((($rd.MeanLatency - $rs.MeanLatency) / $rs.MeanLatency) * 100, 1)
        "+$pct%"
    } else { "0%" }

    $md += "| **$m** | Static Cowrie | $($rs.MeanTurns) | $($rs.TotalCmds) | $rPctS% | $cPctS% | $($rs.MeanLatency)s | Baseline |"
    $md += "| **$m** | Dynamic (Qwen-32B) | $($rd.MeanTurns) | $($rd.TotalCmds) | $rPctD% | $cPctD% | $($rd.MeanLatency)s | $overhead |"
}

$md += "`n## Key Qualitative Research Findings for the Paper`n"
$md += "1. **Attacker Model Sophistication:**"
$md += "   - **Gemma-3-4B-IT:** Demonstrates strict single-command adherence but remains largely trapped in basic file exploration (`ls`, `pwd`, `/etc/passwd`)."
$md += "   - **DeepSeek-V3.2:** Shows advanced attack strategies, executing complex piped multi-clause commands (`find / -type f ... | head -30`) targeting `.ssh` keys, backups, and databases."
$md += "   - **GPT-OSS-120B:** Tends to generate multi-command shell script blocks rather than single commands, leading to command concatenation artifacts in raw shell sessions."
$md += "`n2. **Honeypot Backend Deception & Overhead:**"
$md += "   - The dynamic LLM backend (Qwen-32B) successfully responds to arbitrary shell exploration with plausible Linux file systems and configs."
$md += "   - However, the LLM backend incurs significant latency overhead compared to static emulation, which can trigger timeout disconnects if idle-drain thresholds are too aggressive."

# Save paper tables
$outTables = Join-Path $ScriptDir "paper_tables.md"
$md | Out-File -FilePath $outTables -Encoding UTF8
Write-Host "`n[+] Saved Paper Tables to $outTables"

# Save normalized dataset
$normDir = Join-Path $ScriptDir "normalized"
if (-not (Test-Path $normDir)) { New-Item -ItemType Directory -Path $normDir | Out-Null }
$outJsonl = Join-Path $normDir "all_synthetic_120.jsonl"
$allNormalized | ForEach-Object { $_ | ConvertTo-Json -Compress } | Out-File -FilePath $outJsonl -Encoding UTF8
Write-Host "[+] Saved Normalized JSONL Dataset to $outJsonl ($($allNormalized.Count) sessions)"
