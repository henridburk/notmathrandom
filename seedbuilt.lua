local json = require("cjson")

-- Read the seeds.json file
local function read_json(filename)
    local file = io.open(filename, "r")
    if not file then
        error("Could not open " .. filename)
    end
    local content = file:read("*a")
    file:close()
    return json.decode(content)
end

-- Write the result to seedbuilt.json
local function write_json(filename, data)
    local file = io.open(filename, "w")
    if not file then
        error("Could not open " .. filename .. " for writing")
    end
    file:write(json.encode(data))
    file:close()
end

-- Process each seed and replace os.clock with the corresponding scaled value
local function process_seeds(seeds)
    local results = {}

    for _, entry in ipairs(seeds) do
        math.randomseed(math.tointeger(entry.scaled) or math.floor(entry.scaled))
        table.insert(results, { original = entry.original, scaled = entry.scaled })
    end

    return results
end

-- Main execution
local function main()
    local seeds = read_json("seeds.json")
    local results = process_seeds(seeds)
    write_json("seedbuilt.json", results)
    print("Processed seeds and wrote results to seedbuilt.json")
end

main()
