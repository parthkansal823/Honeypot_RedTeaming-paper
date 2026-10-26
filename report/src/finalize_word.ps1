# Finalises a .docx built by build_report.py, using Microsoft Word itself:
#   1. turns every "Equation Source" paragraph (UnicodeMath text) into a native,
#      editable Word equation with its number on the right,
#   2. updates captions, cross-references, the table of contents and the lists
#      of figures and tables,
#   3. saves the document and (with -Pdf) exports a PDF next to it.
#
#   powershell -ExecutionPolicy Bypass -File report\src\finalize_word.ps1 -Docx report\Project_Report.docx -Pdf

param(
    [Parameter(Mandatory = $true)][string]$Docx,
    [switch]$Pdf
)

$ErrorActionPreference = "Stop"
$path = (Resolve-Path $Docx).Path
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$word.Options.CheckGrammarAsYouType = $false
$word.Options.CheckSpellingAsYouType = $false

try {
    $doc = $word.Documents.Open($path, $false, $false)

    # ---- 1. equations -------------------------------------------------------
    $converted = 0
    for ($guard = 0; $guard -lt 400; $guard++) {
        $rng = $doc.Content
        $find = $rng.Find
        $find.ClearFormatting()
        $find.Text = ""
        $find.Style = $doc.Styles.Item("Equation Source")
        $find.Format = $true
        $find.Forward = $true
        $find.Wrap = 0
        if (-not $find.Execute()) { break }
        $para = $rng.Paragraphs.Item(1)
        $body = $doc.Range($para.Range.Start, $para.Range.End - 1)
        $para.Style = $doc.Styles.Item("Normal")
        $para.Alignment = 1
        $para.SpaceBefore = 6
        $para.SpaceAfter = 6
        try {
            $null = $doc.OMaths.Add($body)
            $body.OMaths.Item(1).BuildUp()
            $converted++
        } catch {
            Write-Host "  equation left as text: $($body.Text)"
        }
    }
    Write-Host "equations converted: $converted"

    # ---- 2. fields, contents and lists -------------------------------------
    $null = $doc.Fields.Update()
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    foreach ($tof in $doc.TablesOfFigures) { $tof.Update() }
    $doc.Repaginate()
    $null = $doc.Fields.Update()
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    foreach ($tof in $doc.TablesOfFigures) { $tof.Update() }

    # The empty paragraph that closes each contents/list field must not spill onto a
    # page of its own when the list fills its last page exactly.
    $lists = @()
    foreach ($toc in $doc.TablesOfContents) { $lists += $toc.Range }
    foreach ($tof in $doc.TablesOfFigures) { $lists += $tof.Range }
    foreach ($rg in $lists) { try {
        $after = $doc.Range($rg.End, $rg.End).Paragraphs.Item(1)
        if ($after.Range.Text.Trim([char]13, [char]21, ' ').Length -gt 0) { $after = $after.Next(1) }
        if ($null -ne $after -and $after.Range.Text.Trim([char]13, [char]21, ' ').Length -eq 0) {
            $after.LineSpacingRule = 4
            $after.LineSpacing = 1
            $after.SpaceBefore = 0
            $after.SpaceAfter = 0
            $after.Range.Font.Size = 1
            # If this 1 pt line still spilled onto a page of its own (the list filled its last
            # page exactly), let the next heading start on that page instead of yet another one.
            $doc.Repaginate()
            $nextPara = $after.Next(1)
            $prevPara = $after.Previous(1)
            if ($null -ne $nextPara -and $null -ne $prevPara -and $nextPara.Format.PageBreakBefore -and
                $after.Range.Information(3) -gt $prevPara.Range.Information(3)) {
                $nextPara.Format.PageBreakBefore = $false
            }
        }
    } catch { Write-Host "  list-end fix skipped: $($_.Exception.Message)" } }
    $doc.Repaginate()
    foreach ($toc in $doc.TablesOfContents) { $toc.UpdatePageNumbers() }
    foreach ($tof in $doc.TablesOfFigures) { $tof.UpdatePageNumbers() }

    # Save to a temporary file first and swap it in afterwards, so a brief lock on the
    # original (preview pane, sync client, antivirus) cannot make the whole run fail.
    $tmp = [System.IO.Path]::ChangeExtension($path, ".finalized.docx")
    $doc.SaveAs2($tmp, 16)
    $pages = $doc.ComputeStatistics(2)
    $words = $doc.ComputeStatistics(0)

    if ($Pdf) {
        $pdfPath = [System.IO.Path]::ChangeExtension($path, ".pdf")
        $doc.ExportAsFixedFormat($pdfPath, 17)
        Write-Host "exported $pdfPath"
    }
    $doc.Close($false)
    for ($i = 0; $i -lt 10; $i++) {
        try { Move-Item -Force $tmp $path -ErrorAction Stop; break }
        catch { Start-Sleep -Seconds 3 }
    }
    if (Test-Path $tmp) { Write-Host "could not replace $path (is it open?); finalized copy kept at $tmp" }
    else { Write-Host "saved $path  pages=$pages  words=$words" }
}
catch {
    Write-Host "FAILED at line $($_.InvocationInfo.ScriptLineNumber): $($_.Exception.Message)"
    throw
}
finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
}
