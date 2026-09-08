import subprocess
import os
import sys
from pathlib import Path

BLENDER_5_2 = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
BLENDER_3_6 = r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe"

def run_blender_generator(generator_script: str, output_glb: str = None, output_png: str = None, blender_version="5.2"):
    blender_exe = BLENDER_5_2 if blender_version == "5.2" else BLENDER_3_6
    if not os.path.exists(blender_exe):
        raise FileNotFoundError(f"Blender executable not found at: {blender_exe}")
    
    cmd = [
        blender_exe,
        "--background",
        "--python", generator_script
    ]
    
    # 追加引数を渡す
    if output_glb or output_png:
        cmd.append("--")
        if output_glb:
            cmd.extend(["--export-glb", str(output_glb)])
        if output_png:
            cmd.extend(["--render-png", str(output_png)])
            
    print(f"Running Blender command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    
    print("--- Blender Output ---")
    print(result.stdout)
    if result.returncode != 0:
        print("--- Blender Error ---")
        print(result.stderr)
        return False, result.stderr
        
    return True, result.stdout

if __name__ == "__main__":
    if len(sys.argv) > 1:
        script = sys.argv[1]
        glb = sys.argv[2] if len(sys.argv) > 2 else None
        png = sys.argv[3] if len(sys.argv) > 3 else None
        success, out = run_blender_generator(script, glb, png)
        if not success:
            sys.exit(1)
    else:
        print("Usage: python blender_runner.py <generator_script> [output_glb] [output_png]")
