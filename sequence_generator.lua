-- Import JSON module for saving data
local json = require("cjson")

-- Function to replicate initial math.random calls to match the server state
local function replicateInitialRandomCalls()
    -- Three initial math.random() calls
    math.random()
    math.random()
	math.random()

    -- One call for generating the gameId
    math.random(1000, 10000000)
end

-- Function to generate a sequence of cards for a single seed
local function generateSequenceForSeed(seed, num_cards)
    -- Initialize the random seed (ensure it's an integer)
    math.randomseed(seed)

    -- Replicate the initial math.random calls to match the server state
    replicateInitialRandomCalls()

    -- Generate a sequence of random cards
    local sequence = {}
    for i = 1, num_cards do
        local card = math.random(1, 52)
        table.insert(sequence, card)
    end

    return sequence
end

-- Function to generate card sequences using coroutines
local function generateCardSequences(seeds, num_cards, output_file)
    local card_sequences = {}

    -- Create a coroutine for each seed
    for _, seed in ipairs(seeds) do
        local co = coroutine.create(function()
            local sequence = generateSequenceForSeed(seed, num_cards)
            card_sequences[tostring(seed)] = sequence
        end)

        -- Run the coroutine
        local success, errorMessage = coroutine.resume(co)
        if not success then
            print("Error in coroutine for seed " .. seed .. ": " .. errorMessage)
        end
    end

    -- Save card sequences to a JSON file
    local file = io.open(output_file, "w")
    if file then
        file:write(json.encode(card_sequences))
        file:close()
        print("Card sequences generated and saved to " .. output_file)
    else
        print("Error: Could not open file to save card sequences.")
    end
end

-- Main execution
print("Enter the number of cards to generate per seed (e.g., 1000): ")
local num_cards = io.read("*n")

if num_cards and num_cards > 0 then
    -- Load seeds from seeds.json
    local seed_file = io.open("json/seeds.json", "r")
    if seed_file then
        local data = seed_file:read("*a")
        seed_file:close()
        local seeds = json.decode(data).seeds

        -- Generate card sequences and save to card_sequences.json
        generateCardSequences(seeds, num_cards, "json/card_sequences.json")
    else
        print("Error: Could not open seeds.json.")
    end
else
    print("Invalid input. Please enter a positive number.")
end
