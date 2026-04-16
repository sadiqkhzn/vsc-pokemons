#!/bin/bash

# Script to replace black sprites with colored ones from PokeAPI/Showdown

echo "🎨 Fixing Pokemon sprites with colored versions..."

# Function to fix a specific pokemon
fix_pokemon() {
    local pokemon_name=$1
    local id=$2
    local gen=$3
    
    echo "🔧 Processing $pokemon_name (#$id)..."
    
    sprite_dir="media/$gen/$pokemon_name"
    
    if [ -d "$sprite_dir" ]; then
        cd "$sprite_dir"
        
        # Download colored sprites from PokeAPI Showdown
        echo "  📥 Downloading colored sprite..."
        curl -s -L "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/$id.gif" -o colored_base.gif
        
        # For shiny version
        curl -s -L "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/shiny/$id.gif" -o colored_shiny.gif 2>/dev/null
        
        if [ -f "colored_base.gif" ] && [ -s "colored_base.gif" ]; then
            echo "  ✅ Replacing sprites with colored versions..."
            
            # Use the colored sprite for all animations
            cp colored_base.gif default_idle_8fps.gif
            cp colored_base.gif default_walk_8fps.gif
            
            # For flying Pokemon, also replace fly animation
            if [ -f "default_fly_8fps.gif" ]; then
                cp colored_base.gif default_fly_8fps.gif
                echo "    🕊️  Updated fly animation"
            fi
            
            # Replace shiny versions if available
            if [ -f "colored_shiny.gif" ] && [ -s "colored_shiny.gif" ]; then
                cp colored_shiny.gif shiny_idle_8fps.gif
                cp colored_shiny.gif shiny_walk_8fps.gif
                if [ -f "shiny_fly_8fps.gif" ]; then
                    cp colored_shiny.gif shiny_fly_8fps.gif
                fi
                echo "    ✨ Updated shiny animations"
            fi
            
            # Clean up temp files
            rm -f colored_base.gif colored_shiny.gif
            
            echo "  ✅ $pokemon_name sprites updated!"
        else
            echo "  ❌ Failed to download sprite for $pokemon_name"
            rm -f colored_base.gif colored_shiny.gif
        fi
        
        cd ../../../
    else
        echo "  ❌ Directory not found: $sprite_dir"
    fi
}

# Fix specific Pokemon
fix_pokemon "charizard" "6" "gen1"
fix_pokemon "pidgey" "16" "gen1"
fix_pokemon "pidgeotto" "17" "gen1"
fix_pokemon "pidgeot" "18" "gen1"
fix_pokemon "venomoth" "49" "gen1"
fix_pokemon "hoothoot" "163" "gen2"

echo ""
echo "🎉 Sprite fixing complete! Pokemon should now have colors"
echo "📦 Run 'npm run compile && vsce package' to rebuild the extension"