# Restaura únicamente las fuentes ZIP declaradas y verifica el respaldo completo.
# No abre Unity ni sobrescribe un archivo local diferente.
[CmdletBinding()]
param([switch]$VerifyOnly)

$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$manifestPath = Join-Path $PSScriptRoot 'backup-manifest.json'
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
Add-Type -AssemblyName System.IO.Compression.FileSystem

function Resolve-BackupPath([string]$relative) {
    $resolved = [IO.Path]::GetFullPath((Join-Path $projectRoot $relative))
    $prefix = $projectRoot.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    if (-not $resolved.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Ruta fuera del proyecto: $relative"
    }
    return $resolved
}

function Get-BytesHash([byte[]]$bytes) {
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($algorithm.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant() }
    finally { $algorithm.Dispose() }
}

function Get-FileContentHash([string]$path) {
    $stream = [IO.File]::OpenRead($path)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $stream.Dispose(); $algorithm.Dispose() }
}

foreach ($entry in $manifest.archives) {
    $target = Resolve-BackupPath $entry.target
    $temporaryFolder = Resolve-BackupPath 'Temp/AlarmaBackupRestore'
    [IO.Directory]::CreateDirectory($temporaryFolder) | Out-Null
    $archivePath = Join-Path $temporaryFolder ([Guid]::NewGuid().ToString('N') + '.zip')
    $archive = $null
    try {
        $assembled = [IO.File]::Open($archivePath, [IO.FileMode]::CreateNew)
        try {
            foreach ($part in $entry.parts) {
                $partStream = [IO.File]::OpenRead((Resolve-BackupPath $part))
                try { $partStream.CopyTo($assembled) }
                finally { $partStream.Dispose() }
            }
        } finally { $assembled.Dispose() }
        if ((Get-FileContentHash $archivePath) -cne $entry.zip_sha256) {
            throw "Fragmentos ZIP alterados: $($entry.target)"
        }
        $archive = [IO.Compression.ZipFile]::OpenRead($archivePath)
        if ($archive.Entries.Count -ne 1 -or $archive.Entries[0].FullName -cne $entry.entry) {
            throw "Contenido ZIP inesperado: $($entry.target)"
        }
        $inputStream = $archive.Entries[0].Open()
        $algorithm = [Security.Cryptography.SHA256]::Create()
        try { $sourceHash = ([BitConverter]::ToString($algorithm.ComputeHash($inputStream))).Replace('-', '').ToLowerInvariant() }
        finally { $inputStream.Dispose(); $algorithm.Dispose() }
        if ($archive.Entries[0].Length -ne $entry.bytes -or $sourceHash -cne $entry.sha256) {
            throw "Fuente comprimida alterada: $($entry.target)"
        }
        if (Test-Path -LiteralPath $target) {
            if ((Get-FileContentHash $target) -cne $entry.sha256) {
                throw "La fuente local es distinta; se conserva sin sobrescribir: $($entry.target)"
            }
        } elseif (-not $VerifyOnly) {
            [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($target)) | Out-Null
            $restoring = $target + '.' + [Guid]::NewGuid().ToString('N') + '.tmp'
            try {
                $inputStream = $archive.Entries[0].Open()
                $outputStream = [IO.File]::Open($restoring, [IO.FileMode]::CreateNew)
                try { $inputStream.CopyTo($outputStream) }
                finally { $inputStream.Dispose(); $outputStream.Dispose() }
                if ((Get-FileContentHash $restoring) -cne $entry.sha256) { throw 'Restauración incompleta' }
                [IO.File]::Move($restoring, $target)
            } finally {
                if (Test-Path -LiteralPath $restoring) { Remove-Item -LiteralPath $restoring }
            }
            Write-Host "Restaurado: $($entry.target)"
        }
    } finally {
        if ($null -ne $archive) { $archive.Dispose() }
        if (Test-Path -LiteralPath $archivePath) { Remove-Item -LiteralPath $archivePath }
    }
}

foreach ($entry in $manifest.files) {
    $path = Resolve-BackupPath $entry.path
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Falta: $($entry.path)" }
    $bytes = [IO.File]::ReadAllBytes($path)
    if ($entry.normalize_crlf) {
        $text = [Text.Encoding]::UTF8.GetString($bytes).Replace("`r`n", "`n")
        $bytes = [Text.Encoding]::UTF8.GetBytes($text)
    }
    if ((Get-BytesHash $bytes) -cne $entry.sha256) { throw "Contenido distinto: $($entry.path)" }
}
Write-Host "Respaldo verificado: $($manifest.files.Count) archivos y $($manifest.archives.Count) fuente(s) comprimida(s)."
Write-Host "Unity $($manifest.unity). Escena actual: $($manifest.scene)"
