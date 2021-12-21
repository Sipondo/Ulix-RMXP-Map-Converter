from rubymarshal.ruby import readruby, writeruby

# Open a ruby map
data = readruby("Map032.rxdata")

# print(data.attributes["@data"].data)
# print(len(data.attributes["@data"].data))

# DEPRECATED (use numpy instead): Set tile x=3 to 405.
data.attributes["@data"][3, 0, 0] = 405

# Grab numpy array of map
array = data.attributes["@data"].to_array()

# Set all tiles to 420
array[:, :, :] = 420

# Write array to map
data.attributes["@data"].from_array(array)

# Save to a new file
writeruby(data, "Map032_copy.rxdata")
