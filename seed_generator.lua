-- Import JSON module for saving data
local json = require("cjson")

-- Function to generate seeds
local function generateSeeds(max_seconds, output_file)
    local seeds = {}
    local step = 0.001  -- Step size of 1 millisecond

    -- Generate seeds for the range 0.001 to max_seconds (inclusive)
    for i = 1, max_seconds * 1000 do
        -- Multiply by 100000000 to avoid floating-point errors
        local seed = i * 100000000
        table.insert(seeds, seed)
    end

    -- Save seeds to a JSON file
    local file = io.open(output_file, "w")
    if file then
        file:write(json.encode({ seeds = seeds }))
        file:close()
        print("Seeds generated and saved to " .. output_file)
    else
        print("Error: Could not open file to save seeds.")
    end
end

-- Main execution
print("Enter the maximum time in seconds (e.g., 10 for 0.001 to 10.000): ")
local input = io.read("*n")

if input and input > 0 then
    generateSeeds(input, "json/seeds.json")
else
    print("Invalid input. Please enter a positive number.")
end
