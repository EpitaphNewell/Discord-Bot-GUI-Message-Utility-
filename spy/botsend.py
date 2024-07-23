import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import discord
from discord.ext import commands
import asyncio
import os
import traceback
import webbrowser
import re

script_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(script_dir, "logs")
os.makedirs(log_dir, exist_ok=True)

# Function to read token from config.txt and create the file if it doesn't exist
def read_token():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.txt')
    
    if not os.path.exists(config_path):
        with open(config_path, 'w') as file:
            file.write('token=YOUR_TOKEN_HERE')
        print("config.txt file created. Please add your token and restart the application.")
        return None
    
    with open(config_path, 'r') as file:
        for line in file:
            if line.startswith('token'):
                token = line.split('=')[1].strip()
                if token == 'YOUR_TOKEN_HERE':
                    print("Please add your token to config.txt and restart the application.")
                    return None
                return token
    print("Token not found in config.txt. Please add your token and restart the application.")
    return None

# Function to log errors
def log_error(error_message, log_dir):
    error_log_filename = os.path.join(log_dir, "error_log.txt")
    with open(error_log_filename, "a") as error_log_file:
        error_log_file.write(error_message + "\n")

# Read token from config file
TOKEN = read_token()
if TOKEN is None:
    log_error("Token is not provided in config.txt.", log_dir)
    exit()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

all_logs_filename = os.path.join(log_dir, "all_logs.txt")

guild_id = None
channel_id = None
channels = []
user_dict = {}  # Dictionary to store user IDs by their display names

URL_REGEX = r'(https?://[^\s]+)'

def open_url(event):
    idx = console.index(tk.CURRENT)
    line = console.get(f"{idx} linestart", f"{idx} lineend")
    urls = re.findall(URL_REGEX, line)
    if urls:
        webbrowser.open(urls[0])

def log_message(message):
    with open(all_logs_filename, "a") as log_file:
        log_file.write(message + "\n")

def save_logs():
    update_console(f"All logs saved to {all_logs_filename}")

async def send_message(content, file=None):
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            try:
                if file:
                    await channel.send(content, file=file)
                else:
                    await channel.send(content)
            except Exception as e:
                update_console(f"Failed to send message: {e}")
                log_error(str(e))
        else:
            update_console("Channel not found")
    else:
        update_console("Channel not set")

def update_console(message):
    console.insert(tk.END, message + '\n')
    console.yview(tk.END)
    log_message(message)

    start_idx = '1.0'
    while True:
        match = re.search(URL_REGEX, console.get(start_idx, tk.END))
        if not match:
            break
        start_idx = console.search(match.group(), start_idx, stopindex=tk.END)
        end_idx = f"{start_idx}+{len(match.group())}c"
        console.tag_add("url", start_idx, end_idx)
        console.tag_config("url", foreground="blue", underline=1)
        console.tag_bind("url", "<Button-1>", open_url)
        console.tag_bind("url", "<Enter>", lambda e: console.config(cursor="hand2"))
        console.tag_bind("url", "<Leave>", lambda e: console.config(cursor=""))

        start_idx = end_idx

async def update_user_list():
    user_listbox.delete(0, tk.END)
    guild = bot.get_guild(guild_id)
    if guild:
        user_dict.clear()
        for member in guild.members:
            display_name = f"[BOT] {member.name}" if member.bot else f"{member.name} ({member.nick if member.nick else member.name})"
            user_listbox.insert(tk.END, display_name)
            user_dict[display_name] = member.id
        user_listbox.update_idletasks()

def load_message_history(log_dir):
    history_filename = os.path.join(log_dir, f"{channel_id}_history.txt")
    if os.path.exists(history_filename):
        with open(history_filename, "r") as file:
            history = file.readlines()
            for line in history:
                update_console(line.strip())

async def update_channel_messages():
    console.delete(1.0, tk.END)
    load_message_history()
    channel = bot.get_channel(channel_id)
    if channel:
        messages = await channel.history(limit=100).flatten()
        history_filename = os.path.join(log_dir, f"{channel_id}_history.txt")
        with open(history_filename, "w") as history_file:
            for message in messages[::-1]:
                author_name = f"[BOT] {message.author}" if message.author.bot else str(message.author)
                msg_content = f"{author_name}: {message.content}"
                update_console(msg_content)
                history_file.write(msg_content + "\n")

@bot.event
async def on_ready():
    update_console(f'Logged in as {bot.user.name}')
    show_server_and_channel_selection()

@bot.event
async def on_message(message):
    if message.channel.id == channel_id:
        author_name = f"[BOT] {message.author}" if message.author.bot else str(message.author)
        content = f"{author_name}: {message.content}"
        update_console(content)
        log_message(content)
        history_filename = os.path.join(log_dir, f"{channel_id}_history.txt")
        with open(history_filename, "a") as history_file:
            history_file.write(content + "\n")
    await bot.process_commands(message)

def on_send(event=None):
    message = entry.get()
    if message:
        if file_path.get():
            with open(file_path.get(), 'rb') as f:
                file = discord.File(f)
                asyncio.run_coroutine_threadsafe(send_message(message, file), bot.loop)
            file_path.set("")
        else:
            asyncio.run_coroutine_threadsafe(send_message(message), bot.loop)
        entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Warning", "Message cannot be empty")

def select_file():
    file = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
    filename = os.path.basename(file)
    if file:
        file_path.set(file)
        update_console(f"File selected: {filename}")

def run_gui():
    global entry, console, file_path, user_listbox, guild_id, channel_id

    root = tk.Tk()
    root.title("Discord Message Sender")

    frame = tk.Frame(root)
    frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    sidebar = tk.Frame(root, width=200, bg="#f0f0f0")
    sidebar.pack(side=tk.LEFT, fill=tk.Y)

    user_listbox = tk.Listbox(sidebar, width=40, height=20, bg="#f0f0f0")
    user_listbox.pack(padx=10, pady=10)
    user_listbox.bind('<<ListboxSelect>>', on_user_select)

    console_frame = tk.Frame(frame)
    console_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    console = scrolledtext.ScrolledText(console_frame, width=80, height=20, wrap=tk.WORD)
    console.pack(fill=tk.BOTH, expand=True)

    entry = tk.Entry(frame, width=50)
    entry.pack(padx=10, pady=10)
    entry.bind('<Return>', on_send)

    send_button = tk.Button(frame, text="Send", command=on_send)
    send_button.pack(padx=10, pady=10)

    file_path = tk.StringVar()
    file_button = tk.Button(frame, text="Choose File", command=select_file)
    file_button.pack(padx=10, pady=10)

    save_button = tk.Button(frame, text="Save All Logs", command=save_logs)
    save_button.pack(padx=10, pady=10)

    select_button = tk.Button(frame, text="Select Server and Channel", command=show_server_and_channel_selection)
    select_button.pack(padx=10, pady=10)

    root.mainloop()

def on_user_select(event):
    selection = user_listbox.curselection()
    if selection:
        selected_user = user_listbox.get(selection[0])
        user_id = user_dict[selected_user]
        entry.insert(tk.END, f"<@{user_id}>")

def show_server_and_channel_selection():
    global guild_id, channel_id, channels

    selection_window = tk.Toplevel()
    selection_window.title("Select Server and Channel")

    tk.Label(selection_window, text="Select Server:").pack(padx=10, pady=10)
    server_listbox = tk.Listbox(selection_window, width=40, height=10)
    server_listbox.pack(padx=10, pady=10)

    tk.Label(selection_window, text="Select Channel:").pack(padx=10, pady=10)
    channel_listbox = tk.Listbox(selection_window, width=40, height=10)
    channel_listbox.pack(padx=10, pady=10)

    async def update_channel_list():
        global channels
        channel_listbox.delete(0, tk.END)
        guild = bot.get_guild(guild_id)
        if guild:
            channels = guild.text_channels
            for ch in channels:
                channel_name = ch.name
                channel_listbox.insert(tk.END, channel_name)
            channel_listbox.bind('<<ListboxSelect>>', on_channel_select)
            await update_user_list()

    def on_server_select(event):
        global guild_id
        selected_server_index = server_listbox.curselection()
        if selected_server_index:
            guild_id = bot.guilds[selected_server_index[0]].id
            guild_name = bot.guilds[selected_server_index[0]].name
            update_console(f"Server set: {guild_name}")
            asyncio.run_coroutine_threadsafe(update_channel_list(), bot.loop)

    def on_channel_select(event):
        global channel_id
        selected_channel_index = channel_listbox.curselection()
        if selected_channel_index:
            channel_id = channels[selected_channel_index[0]].id
            channel_name = channels[selected_channel_index[0]].name
            update_console(f"Channel set: {channel_name}")
            asyncio.run_coroutine_threadsafe(update_channel_messages(), bot.loop)

    guilds = bot.guilds
    for guild in guilds:
        server_listbox.insert(tk.END, guild.name)
    server_listbox.bind('<<ListboxSelect>>', on_server_select)

    tk.Button(selection_window, text="Select", command=selection_window.destroy).pack(padx=10, pady=10)
    selection_window.mainloop()

async def main():
    try:
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, run_gui)
        await bot.start(TOKEN)
    except Exception as e:
        error_message = f"An error occurred: {e}\n{traceback.format_exc()}"
        print(error_message)
        log_error(error_message)

if __name__ == "__main__":
    asyncio.run(main())