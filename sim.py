import subprocess
import tempfile
import os

def run_lua_script(lua_code):
    # Create a temporary Lua script file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.lua', delete=False) as tmp_file:
        tmp_file.write(lua_code)
        tmp_file_path = tmp_file.name

    try:
        # Run the Lua script using subprocess
        result = subprocess.run(
            ['lua', tmp_file_path],
            text=True,
            capture_output=True,
            check=True
        )

        # Print the output from the Lua script
        print("Lua script output:")
        print(result.stdout.strip())

    except subprocess.CalledProcessError as e:
        print("Error running Lua script:")
        print(e.stderr)

    finally:
        # Clean up the temporary Lua script file
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

if __name__ == "__main__":
    lua_script_code = '''
    local blackjackTables = {}
    for i = 0, 127, 1 do
        blackjackTables[i] = false
    end

    Citizen = {
        CreateThread = function(func)
            coroutine.wrap(func)()
        end
    }

    for i = 0, 31, 1 do
        Citizen.CreateThread(function()
            local seed = os.clock() * 100000000000
            math.randomseed(seed)
            print("Thread", i, "- os.clock:", os.clock(), "Seed:", seed)
        end)
    end
    '''

    run_lua_script(lua_script_code)
