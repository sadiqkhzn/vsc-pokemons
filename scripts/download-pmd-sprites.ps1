# Download PMD SpriteCollab sprites for all flying Pokemon and convert to GIFs
# This script downloads sprite sheets and converts Walk, Idle, and FlapAround
# animations into GIF format compatible with vscode-pokemon

Add-Type -AssemblyName System.Drawing

# Flying Pokemon: key -> dex number
$flyingPokemon = @{
    'butterfree' = 12; 'pidgey' = 16; 'pidgeotto' = 17; 'pidgeot' = 18
    'spearow' = 21; 'fearow' = 22; 'zubat' = 41; 'golbat' = 42
    'venomoth' = 49; 'farfetchd' = 83; 'doduo' = 84; 'dodrio' = 85
    'scyther' = 123; 'aerodactyl' = 142; 'articuno' = 144; 'zapdos' = 145
    'moltres' = 146; 'dragonite' = 149; 'mew' = 151; 'crobat' = 169
    'hoothoot' = 163; 'noctowl' = 164; 'ledyba' = 165; 'ledian' = 166
    'togetic' = 176; 'xatu' = 178; 'murkrow' = 198; 'gligar' = 207
    'delibird' = 225; 'mantine' = 226; 'skarmory' = 227; 'lugia' = 249
    'hooh' = 250; 'celebi' = 251; 'beautifly' = 267; 'dustox' = 269
    'masquerain' = 284; 'ninjask' = 291; 'shedinja' = 292; 'swablu' = 333
    'altaria' = 334; 'vibrava' = 329; 'flygon' = 330; 'tropius' = 357
    'salamence' = 373; 'latias' = 380; 'latios' = 381; 'rayquaza' = 384
    'taillow' = 276; 'swellow' = 277; 'wingull' = 278; 'pelipper' = 279
    'starly' = 396; 'staravia' = 397; 'staraptor' = 398; 'mothim' = 414
    'combee_male' = 415; 'combee_female' = 415; 'vespiquen' = 416
    'drifloon' = 425; 'drifblim' = 426; 'honchkrow' = 430; 'chatot' = 441
    'togekiss' = 468; 'yanmega' = 469; 'gliscor' = 472; 'shaymin_sky' = 492
    'cresselia' = 488; 'charizard' = 6
}

# Generation mapping for folder output
$genRanges = @(
    @{ Gen = 'gen1'; Min = 1; Max = 151 }
    @{ Gen = 'gen2'; Min = 152; Max = 251 }
    @{ Gen = 'gen3'; Min = 252; Max = 386 }
    @{ Gen = 'gen4'; Min = 387; Max = 493 }
)

function Get-Gen($dexNum) {
    foreach ($g in $genRanges) {
        if ($dexNum -ge $g.Min -and $dexNum -le $g.Max) { return $g.Gen }
    }
    return 'gen1'
}

# Direction row index: 0=Down 1=DownRight 2=Right 3=UpRight 4=Up 5=UpLeft 6=Left 7=DownLeft
$RIGHT_ROW = 2

$mediaDir = Join-Path $PSScriptRoot '..\media'
$tempDir = Join-Path $env:TEMP 'pmd_sprites'
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

$total = $flyingPokemon.Count
$current = 0

foreach ($entry in $flyingPokemon.GetEnumerator()) {
    $pokemonKey = $entry.Key
    $dexNum = $entry.Value
    $dexPadded = $dexNum.ToString().PadLeft(4, '0')
    $gen = Get-Gen $dexNum
    $current++

    Write-Host "[$current/$total] Processing $pokemonKey (#$dexNum)..." -ForegroundColor Cyan

    $zipUrl = "https://spriteserver.pmdcollab.org/assets/$dexPadded/sprites.zip"
    $zipPath = Join-Path $tempDir "$pokemonKey.zip"
    $extractDir = Join-Path $tempDir $pokemonKey

    # Download
    try {
        if (!(Test-Path $zipPath)) {
            Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing -TimeoutSec 30
        }
    } catch {
        Write-Host "  SKIP: Failed to download $zipUrl" -ForegroundColor Red
        continue
    }

    # Extract
    if (Test-Path $extractDir) { Remove-Item $extractDir -Recurse -Force }
    try {
        Expand-Archive $zipPath -DestinationPath $extractDir -Force
    } catch {
        Write-Host "  SKIP: Failed to extract $zipPath" -ForegroundColor Red
        continue
    }

    # Parse AnimData.xml
    $animDataPath = Join-Path $extractDir 'AnimData.xml'
    if (!(Test-Path $animDataPath)) {
        Write-Host "  SKIP: No AnimData.xml" -ForegroundColor Red
        continue
    }
    [xml]$animData = Get-Content $animDataPath

    # Output directory
    $outDir = Join-Path $mediaDir "$gen\$pokemonKey"
    if (!(Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir -Force | Out-Null }

    # Process animations: Walk, Idle, FlapAround
    $animations = @(
        @{ Name = 'Walk'; OutName = 'walk' }
        @{ Name = 'Idle'; OutName = 'idle' }
        @{ Name = 'FlapAround'; OutName = 'fly' }
    )

    foreach ($anim in $animations) {
        $animNode = $animData.AnimData.Anims.Anim | Where-Object { $_.Name -eq $anim.Name }
        if (!$animNode) {
            Write-Host "  No $($anim.Name) animation" -ForegroundColor Yellow
            continue
        }

        $frameW = [int]$animNode.FrameWidth
        $frameH = [int]$animNode.FrameHeight
        $frameCount = $animNode.Durations.Duration.Count
        $durations = @($animNode.Durations.Duration | ForEach-Object { [int]$_ })

        $sheetPath = Join-Path $extractDir "$($anim.Name)-Anim.png"
        if (!(Test-Path $sheetPath)) {
            Write-Host "  No $($anim.Name)-Anim.png file" -ForegroundColor Yellow
            continue
        }

        try {
            $sheet = [System.Drawing.Image]::FromFile($sheetPath)

            # Extract right-facing row frames
            $frames = @()
            for ($f = 0; $f -lt $frameCount; $f++) {
                $srcX = $f * $frameW
                $srcY = $RIGHT_ROW * $frameH
                $frame = New-Object System.Drawing.Bitmap($frameW, $frameH)
                $graphics = [System.Drawing.Graphics]::FromImage($frame)
                $graphics.DrawImage($sheet,
                    (New-Object System.Drawing.Rectangle(0, 0, $frameW, $frameH)),
                    (New-Object System.Drawing.Rectangle($srcX, $srcY, $frameW, $frameH)),
                    [System.Drawing.GraphicsUnit]::Pixel)
                $graphics.Dispose()
                $frames += $frame
            }
            $sheet.Dispose()

            # Create animated GIF using .NET
            # We'll save individual frames and use a simple GIF encoder
            $outGif = Join-Path $outDir "default_$($anim.OutName)_8fps.gif"

            # Simple approach: save first frame as GIF, it won't be animated
            # For proper animated GIF we need to write raw GIF bytes
            $ms = New-Object System.IO.MemoryStream

            # GIF Header
            $writer = New-Object System.IO.BinaryWriter($ms)
            $writer.Write([byte[]]@(0x47, 0x49, 0x46, 0x38, 0x39, 0x61)) # GIF89a

            # Logical Screen Descriptor
            $writer.Write([UInt16]$frameW)
            $writer.Write([UInt16]$frameH)
            $writer.Write([byte]0x00) # No GCT
            $writer.Write([byte]0x00) # BG color
            $writer.Write([byte]0x00) # Pixel aspect

            # Netscape extension for looping
            $writer.Write([byte]0x21) # Extension
            $writer.Write([byte]0xFF) # Application
            $writer.Write([byte]0x0B) # Block size
            $writer.Write([System.Text.Encoding]::ASCII.GetBytes("NETSCAPE2.0"))
            $writer.Write([byte]0x03) # Sub-block size
            $writer.Write([byte]0x01) # Loop
            $writer.Write([UInt16]0)   # Loop count (0 = infinite)
            $writer.Write([byte]0x00) # Terminator

            foreach ($i in 0..($frames.Count - 1)) {
                $frame = $frames[$i]
                # Convert frame to indexed GIF bytes
                $frameMs = New-Object System.IO.MemoryStream
                $frame.Save($frameMs, [System.Drawing.Imaging.ImageFormat]::Gif)
                $gifBytes = $frameMs.ToArray()
                $frameMs.Dispose()

                # Calculate delay (PMD durations are in 1/n units, ~125ms per unit at 8fps)
                $delay = [Math]::Max(1, [Math]::Round($durations[$i] * 12.5 / 10))

                # Graphic Control Extension
                $writer.Write([byte]0x21) # Extension
                $writer.Write([byte]0xF9) # GCE
                $writer.Write([byte]0x04) # Block size
                $writer.Write([byte]0x09) # Dispose: restore to BG + transparent
                $writer.Write([UInt16]$delay)
                $writer.Write([byte]0x00) # Transparent color index
                $writer.Write([byte]0x00) # Terminator

                # Find Image Descriptor in the single-frame GIF (starts after header)
                # GIF header = 6 bytes, LSD = 7 bytes, then possibly GCT
                $headerEnd = 13 # 6 + 7
                # Check for GCT
                $packed = $gifBytes[10]
                $hasGCT = ($packed -band 0x80) -ne 0
                if ($hasGCT) {
                    $gctSize = 3 * [Math]::Pow(2, ($packed -band 0x07) + 1)
                    $headerEnd += $gctSize
                }

                # Skip any extensions in the single-frame GIF
                $pos = $headerEnd
                while ($pos -lt $gifBytes.Count -and $gifBytes[$pos] -eq 0x21) {
                    $pos++ # Skip extension introducer
                    $pos++ # Skip label
                    while ($pos -lt $gifBytes.Count -and $gifBytes[$pos] -ne 0) {
                        $blockSize = $gifBytes[$pos]
                        $pos += $blockSize + 1
                    }
                    $pos++ # Skip terminator
                }

                # Now we should be at the Image Descriptor (0x2C)
                if ($pos -lt $gifBytes.Count -and $gifBytes[$pos] -eq 0x2C) {
                    # Write from Image Descriptor to just before the trailer (0x3B)
                    $endPos = $gifBytes.Count - 1
                    while ($endPos -gt $pos -and $gifBytes[$endPos] -ne 0x3B) { $endPos-- }
                    if ($gifBytes[$endPos] -eq 0x3B) {
                        $writer.Write($gifBytes, $pos, $endPos - $pos)
                    }
                }
            }

            # GIF Trailer
            $writer.Write([byte]0x3B)
            $writer.Flush()

            [System.IO.File]::WriteAllBytes($outGif, $ms.ToArray())
            $ms.Dispose()
            $writer.Dispose()

            foreach ($f in $frames) { $f.Dispose() }

            Write-Host "  Created $($anim.OutName) ($frameCount frames, ${frameW}x${frameH})" -ForegroundColor Green
        } catch {
            Write-Host "  ERROR creating $($anim.Name) GIF: $_" -ForegroundColor Red
        }
    }
}

Write-Host "`nDone! Processed $total flying Pokemon." -ForegroundColor Green
