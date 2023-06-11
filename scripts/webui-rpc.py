import gradio as gr
from modules import script_callbacks
from modules import ui
from modules import shared
import threading
import time, os
from time import mktime

github_link = "https://github.com/kabachuha/discord-rpc-for-automatic1111-webui"

def start_rpc():

    print('Launching the Discord RPC extension. By https://github.com/kabachuha, version 0.1b')
    print(f'Use this link to report any problems or add suggestions {github_link}')
    from launch import is_installed, run_pip
    if not is_installed("pypresence"):
        print("Installing the missing 'pypresence' package and its dependencies,")
        print("In case it will give a package error after the installation, restart the webui.")
        run_pip("install pypresence", "pypresence")

    checkpoint_info = shared.sd_model.sd_checkpoint_info
    model_name = os.path.basename(checkpoint_info.filename)

    from pypresence import Presence

    rpc = Presence(1065987911486550076)
    rpc.connect()
    rpc.update(state="Waiting for the start", details=model_name, large_image="unknown", start=mktime(time.localtime()))

    state_watcher = threading.Thread(target=check_progress_loop, args=(rpc,), daemon=True)
    state_watcher.start()

def on_ui_tabs():
    start_rpc()
    return []

script_callbacks.on_ui_tabs(on_ui_tabs)

def check_progress_loop(rpc):
    idle_last = None
    last_timestamp = mktime(time.localtime())
    last_job_count = 0
    last_job_no = 0
    while True:
        checkpoint_info = shared.sd_model.sd_checkpoint_info
        model_name = os.path.basename(checkpoint_info.filename)
        if shared.state.job_count == 0:
            if idle_last == False or idle_last == None:
                last_timestamp = mktime(time.localtime())
                idle_last = True
                last_job_count = 0
                try:
                    rpc.update(large_image="auto", details=model_name, state="Idle", start=last_timestamp)
                except Exception as ex:
                    print(f'Failed to set Discord RPC. model_name="{model_name}", last_timestamp={last_timestamp}. Err: {ex}')
        else:
            if idle_last:
                last_timestamp = mktime(time.localtime())
            if idle_last or last_job_count != shared.state.job_count or last_job_no != shared.state.job_no:
                last_job_no = shared.state.job_no
                try:
                    plural = "pic" if shared.state.job_count == 1 else "pics"
                    rpc.update(large_image="generating", details=model_name, state=f'Generating {shared.state.job_no+1} of {shared.state.job_count} {plural}', start=last_timestamp)
                except Exception as ex:
                    print(f'Failed to set Discord RPC. model_name="{model_name}", last_timestamp={last_timestamp}. Err: {ex}')
                idle_last = False
                last_job_count = shared.state.job_count
        time.sleep(15) # update once per 15 seconds (Discord limitation)
