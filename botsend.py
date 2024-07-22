import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import discord
from discord.ext import commands
import asyncio
import os

TOKEN = 'YOUR_TOKEN'
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

script_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(script_dir, "logs")
os.makedirs(log_dir, exist_ok=True)

all_logs_filename = os.path.join(log_dir, "all_logs.txt")

guild_id = None
channel_id = None
channels = []

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
                update_console(f"Message sent: {content}")
            except Exception as e:
                update_console(f"Failed to send message: {e}")
        else:
            update_console("Channel not found")
    else:
        update_console("Channel not set")

def update_console(message):
    console.insert(tk.END, message + '\n')
    console.yview(tk.END)
    log_message(message)

async def update_user_list():
    user_listbox.delete(0, tk.END)
    guild = bot.get_guild(guild_id)
    if guild:
        for member in guild.members:
            if not member.bot:
                user_listbox.insert(tk.END, f"{member.name} ({member.nick if member.nick else member.name})")
        user_listbox.update_idletasks()

@bot.event
async def on_ready():
    update_console(f'Logged in as {bot.user.name}')
    show_server_and_channel_selection()

@bot.event
async def on_message(message):
    if message.channel.id == channel_id and not message.author.bot:
        content = f"{message.author}: {message.content}"
        update_console(content)
        log_message(content)
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
        update_console(f"File sent: {filename}")

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

    console = scrolledtext.ScrolledText(frame, width=80, height=20, wrap=tk.WORD)
    console.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

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
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
