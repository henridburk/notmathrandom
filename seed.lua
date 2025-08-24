local json = require("cjson") -- Ensure you have lua-cjson installed

-- Configuration
local Config = {
    MinValue = 0.000,
    MaxValue = 4.000,
    Step = 0.001,
    Multiplier = 100000000000,
    OutputFile = "seeds.json"
}

-- Generate the seeds
function generateSeeds()
    local seeds = {}

    for value = Config.MinValue, Config.MaxValue, Config.Step do
        local seedValue = value * Config.Multiplier

        -- Debugging: Print each calculated seed value
        print("Original:", value, "Scaled:", seedValue)

        -- Insert the original and scaled values into the seeds table
        table.insert(seeds, { original = value, scaled = seedValue })
    end

    -- Debugging: Print the seeds table before writing to the file
    print("Seeds Table:", seeds)

    -- Write the seeds to a JSON file
    local file = io.open(Config.OutputFile, "w")
    if file then
        local success, result = pcall(function() return json.encode(seeds) end)
        if success then
            file:write(result)
            file:close()
            print("Seeds successfully written to " .. Config.OutputFile)
        else
            print("Error encoding JSON:", result)
        end
    else
        print("Error: Could not open file for writing.")
    end
end

-- Run the seed generation function
generateSeeds()
