import os
import subprocess
import argparse
import json
import shutil
from threading import Thread
import sys
import ctypes
import asyncio
import builtins
from datetime import datetime, timedelta

original_print = builtins.print

def print(*args, **kwargs):
    current_time = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    original_print(current_time, *args, **kwargs)

ctypes.windll.kernel32.AllocConsole()

class Aider_web():

    def __init__(self,args):
        self.args = args
        self.proc = None
        self.running = False 
        self.output_lines = []
        self.last_activity = datetime.now()
        self.System_prompt="""You are Aider, an expert AI assistant and exceptional senior software developer with vast knowledge across multiple programming languages, frameworks, and best practices.<system_constraints>- No C/C++ compiler, native binaries, or Git- Prefer Node.js scripts over shell scripts- Use Vite for web servers and Node.js for backend- Databases: prefer libsql, sqlite, or non-native solutions- When for react dont forget to write vite config and index.html to the project- Remember to generate a complete package.json file with valid package release version. </system_constraints>"""


    async def generate_working_space(self):
        if self.args.new_project:
            if os.path.exists(self.args.working_dir):
                shutil.rmtree(self.args.working_dir)
        os.makedirs(self.args.working_dir,exist_ok=True)
        source=r".\initial_files\deepseek-v3\\"
        shutil.copytree(source, self.args.working_dir,dirs_exist_ok=True)
        subprocess.run(["git", "init"], cwd=self.args.working_dir, check=True)

    async def start_aider(self,command):
        env = os.environ.copy()
        env["PROMPT_TOOLKIT_FORCE_TERMINAL"] = "1"
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"

        try:
            command=["aider", "--no-show-model-warnings", "--model-settings-file", ".aider.model.settings.yml"]
            print(command)
            self.proc = subprocess.Popen(
                command,
                cwd=self.args.working_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                text=True,
                bufsize=1,
                env=env
            )
        except Exception as e:
            print(e)

        self.running = True
        self.io_thread = Thread(target=self._monitor_output)
        self.io_thread.start()

        await asyncio.sleep(10)
        
    async def timeout_checker(self):
        while True:
            await asyncio.sleep(1)  
            if (datetime.now() - self.last_activity) > timedelta(seconds=30):
                print("Exceed 30s without output, stop")
                break
            

    def _monitor_output(self):
        try:
            while self.running:
                line = self.proc.stdout.readline()
                if not line:
                    if self.proc.returncode is not None:
                        break
                    continue
                
                print(f"[Aider] {line}", end='')
                self.output_lines.append(line.strip())
                self.last_activity = datetime.now()
        except Exception as e:
            print(f"Error: {str(e)}")
        finally:
            self.running = False

        

    async def monitor_time(self):
        timeout_task = asyncio.create_task(self.timeout_checker())

        done, pending = await asyncio.wait(
            [timeout_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        if done:
            self.stop()


    async def initial_input(self):
        if self.running:
            self.proc.stdin.write(self.System_prompt + "\n")
            self.proc.stdin.flush()
        await asyncio.sleep(10)
    


    async def send_command(self, cmd):
        if self.running:
            self.proc.stdin.write(cmd + "\n")
            self.proc.stdin.flush()
        await asyncio.sleep(10)
        

    def stop(self):
        self.running = False
        if self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        if self.io_thread.is_alive():
            self.io_thread.join(timeout=1)


    async def run(self):
        await self.generate_working_space()
        try:
            await self.start_aider(["aider", "--no-show-model-warnings", "--model-settings-file", ".aider.model.settings.yml"])
            await self.initial_input()
            await self.send_command("Please implement a multi-company dashboard for managing and displaying financial data from multiple companies. The dashboard should be able to collect and display financial information from each company, provide consolidated reports, and support cross-company comparisons and reporting. Users should be able to browse financial data from each company, view consolidated reports, and perform financial management and reporting. Apply mint cream as the background; style all components with teal.")
            await self.send_command("Make sure all the files imported are correctly generated, and check the package.json. Generate the remaining files if needed.")
            await self.monitor_time()
        except:
            self.stop()




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-w','--working_dir',type=str)
    parser.add_argument('-n','--new_project',action="store_true")

    args =  parser.parse_args()
    aider = Aider_web(args)
    asyncio.run(aider.run())
    

if __name__=="__main__":
    main()