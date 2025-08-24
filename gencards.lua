local cjson = require("cjson")

-- Read a JSON file
local function read_json(filename)
    local file = io.open(filename, "r")
    if not file then
        error("Could not open " .. filename)
    end
    local content = file:read("*a")
    file:close()
    return cjson.decode(content)
end

-- Write a JSON file
local function write_json(filename, data)
    local file = io.open(filename, "w")
    if not file then
        error("Could not open " .. filename .. " for writing")
    end
    file:write(cjson.encode(data))
    file:close()
end

-- Generate 500 random cards (values between 1 and 52) for a given seed
local function generate_cards_for_seed(seed, num_cards)
    math.randomseed(seed)
    local cards = {}
    for i = 1, num_cards do
        table.insert(cards, math.random(1, 52))
    end
    return cards
end

-- Main execution
local function main()
    local seeds = read_json("seeds.json")
    local results = {}

    for _, entry in ipairs(seeds) do
        local seed = entry.scaled
        local generated_cards = generate_cards_for_seed(seed, 500)
        table.insert(results, {
            original = entry.original,
            scaled = seed,
            cards = generated_cards
        })
    end

    write_json("cards_generated.json", results)
    print("Generated 500 cards for each seed and wrote results to cards_generated.json")
end

main()
