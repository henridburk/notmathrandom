import subprocess
import tempfile
import os

def run_lua_clock():
    # Lua code to call os.clock() and print the result
    lua_code = 'print(os.clock())'

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
        print("Lua os.clock() output:", result.stdout.strip())

    except subprocess.CalledProcessError as e:
        print("Error running Lua script:", e)
        print("Standard Error Output:", e.stderr)

    finally:
        # Clean up the temporary Lua script file
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

if __name__ == "__main__":
    run_lua_clock()
