import os
import subprocess
import argparse
import json
import shutil
from threading import Thread
import sys
import ctypes
import asyncio
from datetime import datetime, timedelta
from collections import deque


ctypes.windll.kernel32.AllocConsole()

class Aider_web():

    def __init__(self,args):
        self.args = args
        self.proc = None
        self.running = False 
        self.output_lines = []
        self.last_activity = datetime.now()
        self.System_prompt="""You are Aider, an expert AI assistant and exceptional senior software developer with vast knowledge across multiple programming languages, frameworks, and best practices.<system_constraints>- You MUST generate the code and files Directly without telling me the implementation plan, just generate the codes and files. - No C/C++ compiler, native binaries, or Git- Prefer Node.js scripts over shell scripts- Use Vite for web servers and Node.js for backend- Databases: prefer libsql, sqlite, or non-native solutions- When for react dont forget to write vite config and index.html to the project- You MUST generate a complete package.json file with valid package release version. </system_constraints>"""


    async def generate_working_space(self):
        if self.args.new_project:
            if os.path.exists(self.args.working_dir):
                shutil.rmtree(self.args.working_dir)
        os.makedirs(self.args.working_dir,exist_ok=True)
        source=r"..\initial_files\deepseek-v3\\"
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
        await asyncio.sleep(30)
        

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
            await self.send_command(self.args.instruction)
            await self.send_command("Make sure all the files imported are correctly generated, and a complete package.json file with valid package release version exists. Generate the remaining files if needed.")
            await self.monitor_time()
        except:
            self.stop()



class TaskScheduler:
    def __init__(self, runner, commands, args, max_concurrent=8):
        self.command_queue = asyncio.Queue()    
        self.running_tasks = set()              
        self.completed_results = []             
        self.semaphore = asyncio.Semaphore(max_concurrent)  
        self.runner=runner
        self.args=args
      
        
        for cmd in commands:
            self.command_queue.put_nowait(cmd)

    async def worker(self):

        while not self.command_queue.empty():
            async with self.semaphore: 
                cmd = await self.command_queue.get()
                print(f"Start Task: {cmd} | Task remain: {self.command_queue.qsize()}")
              
                try:
                    result = await self.run_command(cmd)
                    self.completed_results.append((cmd, result, None))
                except Exception as e:
                    self.completed_results.append((cmd, None, str(e)))
              
                self.command_queue.task_done()

    async def run_command(self, command):
      
        start_time = datetime.now()
        args_dict={}
        args_dict.update(
            {
                "working_dir":f"task_{command[0]}",
                "instruction":command[1],
                "new_project":True
            }
        )
        args=argparse.Namespace(**args_dict)
        aider = self.runner(args)
        await aider.run()
        return {
            "duration": (datetime.now() - start_time).total_seconds()
        }

    async def monitor_progress(self):

        total = self.command_queue.qsize() + len(self.running_tasks)
        while not self.command_queue.empty() or self.running_tasks:
            done = len(self.completed_results)
            print(f"\rProcess: {done}/{total} | Running: {len(self.running_tasks)}", end="")
            await asyncio.sleep(0.5)

    async def run_all(self):

        workers = [asyncio.create_task(self.worker()) for _ in range(8)]
        monitor_task = asyncio.create_task(self.monitor_progress())
        await self.command_queue.join()  
        monitor_task.cancel()
      

        for task in workers:
            if not task.done():
                task.cancel()
      

        return {
            "total": len(self.completed_results),
            "success": sum(1 for r in self.completed_results if r[1]),
            "failed": sum(1 for r in self.completed_results if r[2])
        }

def load_jsonl(path):
    if path.endswith('json'):
        with open(path, 'r', encoding='utf-8') as fr:
            data=json.load(fr)
        
    else:
        data = []
        with open(path, 'r', encoding='utf-8') as fr:
            for line in fr.readlines():
                data.append(json.loads(line))
    return data


async def main():
    parser = argparse.ArgumentParser()
    args =  parser.parse_args()
    data_path=r"..\test.jsonl"
    commands=load_jsonl(data_path)
    commands = [(i,line.get("instruction")) for i,line in enumerate(commands)]
    scheduler = TaskScheduler(Aider_web, commands, args, max_concurrent=3)
    stats = await scheduler.run_all()
  
    print("\nTask in all:")
    print(f"All Tasks: {stats['total']}")
    print(f"Succeed Tasks: {stats['success']}")
    print(f"Fail Tasks: {stats['failed']}")
  

    for cmd, result, error in scheduler.completed_results[:3]:
        print(f"\nCommand: {cmd}")
        if error:
            print(f"Error: {error}")
        else:
            print(f"Time: {result['duration']:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())