import gradio as gr
from modules import script_callbacks
from modules import ui
from modules import shared
import threading
import time

github_link = "https://github.com/kabachuha/discord-rpc-for-automatic1111-webui"

def check_progress_loop(RPC_store):
    while True:
        checkpoint_info = shared.sd_model.sd_checkpoint_info
        model_name = checkpoint_info.filename
        if shared.state.job_count == 0:
            RPC_store.update(large_image="auto", large_text=model_name, small_text="Idle")
        else:
            RPC_store.update(large_image="generating", large_text=model_name, small_text=shared.state.job)
        time.sleep(1) # update once per second

def start_rpc():
    print('Launching the Discord RPC extension. By https://github.com/kabachuha')
    print(f'Use this link to report any problems or add suggestions {github_link}')
    from launch import is_installed, run_pip
    if not is_installed("discord-rpc"):
        print("Installing the missing 'discord-rpc' package and its dependencies,")
        print("In case it will give a package error after the installation, restart the webui.")
        run_pip("install discord-rpc", "discord-rpc")
    
    checkpoint_info = shared.sd_model.sd_checkpoint_info
    model_name = checkpoint_info.filename

    import DiscordRPC
    import time 

    rpc = DiscordRPC.RPC.Set_ID(app_id=1065987911486550076)

    rpc.set_activity(
          state="Waiting for start",
          details=model_name,
          large_image="unknown"
        )

    print('Starting the RPC thread')
    state_watcher = threading.Thread(target=check_progress_loop, args=(rpc,), daemon=True)
    state_watcher.start()
    rpc.run()
    print("If everything is fine, the RPC should be running by now. Proceed to your Discord settings and add the app (it's name is huge) to the game list.")
    
def on_ui_tabs():
    start_rpc()
    return []

script_callbacks.on_ui_tabs(on_ui_tabs)
