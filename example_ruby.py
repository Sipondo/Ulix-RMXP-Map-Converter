from rubymarshal.ruby import readruby, writeruby

RUBY_MAPNAME = "Map042.rxdata"
# Open a ruby map
data = readruby(RUBY_MAPNAME)

# Grab numpy array of map
array = data.attributes["@data"].to_array()

# Set all tiles to 420
array[:, :, :] = 420

# Write array to map
data.attributes["@data"].from_array(array)

# Save to a new file
writeruby(data, f"altered_{RUBY_MAPNAME}")
