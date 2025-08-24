local json = require("cjson") -- Ensure you have lua-cjson installed

-- Configuration Variables
local Config = {
    -- Range for fake os.clock values
    ClockRange = {
        min = 0.001,
        max = 0.500,
        step = 0.001
    },

    -- Number of tables and cards
    NumberOfTables = 500,       -- Generate data for 10 tables as an example
    CardsPerSequence = 500,      -- Generate 5 cards per sequence
    OutputFile = "output.json" -- File to save generated data
}

-- Generate all possible os.clock values based on config
local fakeClockValues = {}
for t = Config.ClockRange.min, Config.ClockRange.max, Config.ClockRange.step do
    table.insert(fakeClockValues, tonumber(string.format("%.3f", t)))
end

-- Function to generate seeds and card sequences
function generateData()
    local data = {} -- Initialize an empty table to hold all entries
    local fakeClockIndex = 1

    for i = 0, Config.NumberOfTables - 1 do
        -- Use the fake os.clock value for seeding
        local currentSeed = fakeClockValues[fakeClockIndex]
        math.randomseed(math.floor(currentSeed * 100000000000)) -- Set the seed for randomness

        -- Debugging: Print the current seed
        print("Generating data for table " .. i .. " with seed: " .. currentSeed)

        -- Generate a sequence of random cards
        local cardSequence = {}
        for cardIndex = 1, Config.CardsPerSequence do
            local randomCard = math.random(1, 52)
            table.insert(cardSequence, randomCard)
        end

        -- Add the generated entry to the data table
        table.insert(data, {
            table_id = i,
            seed = currentSeed,
            card_sequence = cardSequence,
            timestamp = os.date("!%Y-%m-%dT%H:%M:%SZ")
        })

        -- Move to the next fake clock value
        fakeClockIndex = fakeClockIndex + 1
        if fakeClockIndex > #fakeClockValues then
            fakeClockIndex = 1 -- Reset to the beginning if we exhaust the list
        end
    end

    -- Debugging: Print the entire data table before writing to the file
    print("Generated data:")
    for _, entry in ipairs(data) do
        print(json.encode(entry))
    end

    -- Write the entire data table to a JSON file
    local file = io.open(Config.OutputFile, "w")
    if file then
        file:write(json.encode(data)) -- Encode the entire data table to JSON
        file:close()
        print("Data successfully written to " .. Config.OutputFile)
    else
        print("Error: Could not open file for writing.")
    end
end

-- Run the data generation function
generateData()
