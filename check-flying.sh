#!/bin/bash

# Quick script to check which flying Pokemon have FlapAround animations
flying_pokemon=(
    "006:charizard"
    "012:butterfree" 
    "016:pidgey"
    "017:pidgeotto"
    "018:pidgeot"
    "021:spearow"
    "022:fearow"
    "041:zubat"
    "042:golbat"
    "049:venomoth"
    "083:farfetchd"
    "123:scyther"
    "142:aerodactyl"
    "144:articuno"
    "145:zapdos"
    "146:moltres"
    "149:dragonite"
)

echo "Checking which Pokemon have FlapAround animations..."
echo "Format: Dex# Name - Result"
echo "=========================="

cd /tmp
for entry in "${flying_pokemon[@]}"; do
    IFS=':' read -r dex name <<< "$entry"
    
    # Pad dex number to 4 digits
    padded=$(printf "%04d" $dex)
    
    # Download and check
    curl -s -L "https://spriteserver.pmdcollab.org/assets/${padded}/sprites.zip" -o "${name}.zip"
    
    if [ -f "${name}.zip" ]; then
        flap_count=$(unzip -l "${name}.zip" 2>/dev/null | grep -c "FlapAround" || echo "0")
        if [ "$flap_count" -gt 0 ]; then
            echo "#${dex} ${name} - ✅ HAS FlapAround"
        else
            echo "#${dex} ${name} - ❌ No FlapAround"
        fi
        rm -f "${name}.zip"
    else
        echo "#${dex} ${name} - ❓ Download failed"
    fi
done

echo "=========================="
echo "Done checking flying Pokemon animations"