import socket
import threading
import customtkinter as ctk
import random
import data as Q

HOST = '127.0.0.1'  #localhost
PORT = 1234         #random numbers

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ChatClient(ctk.CTk):
    def __init__(self, host, port):
        super().__init__()
        
        self.host = host
        self.port = port
        self.nickname = ""
        self.sock = None
        
        self.user_colors = {}

        self.title("Main Menu")
        self.geometry("425x540")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.create_login_widgets()


    def create_login_widgets(self):

        rnd_quote = random.choice(Q.daily_quote)

        #Frame/Column/Row
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            
        self.login_frame.grid_columnconfigure(0, weight=1) 
        self.login_frame.grid_columnconfigure(1, weight=0)

        self.login_frame.grid_rowconfigure(3, weight=2)
        self.login_frame.grid_rowconfigure(6, weight=3) 

        #Labels 
        label_title = ctk.CTkLabel(self.login_frame, text="Join Chat ", font=ctk.CTkFont(size=25, weight="bold"))
        label_title.grid(row=1, column=0, columnspan=2, pady=(12, 2), padx=10) 
            
        label_quote = ctk.CTkLabel(self.login_frame, text=f"- {rnd_quote} -" ,text_color="#AAAAAA", font=ctk.CTkFont(size=14))
        label_quote.grid(row=2, column=0, columnspan=2, pady=(2, 12), padx=10) 

        label_quote.bind("<Button-1>", self.toggle_theme)
        label_quote.configure(cursor="hand2")

        #Entry
        self.nick_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Choose your name!")
        self.nick_entry.grid(row=4, column=0, pady=(12, 2), padx=(10,5), sticky="ew")

        random_name_button = ctk.CTkButton(self.login_frame, text="🎲", width=40 ,command=self.random_name)
        random_name_button.grid(row=4, column=1, pady=(12, 2), padx=(5, 10))
            
        join_button = ctk.CTkButton(self.login_frame, text="Beitreten", command=self.connect_to_chat)
        join_button.grid(row=5, column=0, columnspan=2, pady=(2, 12), padx=10)
            
        self.nick_entry.bind("<Return>", lambda event: self.connect_to_chat())

    def random_name(self):
        first1 = random.choice(Q.firstname)
        second2 = random.choice(Q.secondname)
    
        new_nickname = f"{first1}{second2}"

        self.nick_entry.delete(0, "end")
        self.nick_entry.insert(0, new_nickname)


    #Theme Change
    def toggle_theme(self, event=None):
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")


    def connect_to_chat(self):
        nickname = self.nick_entry.get()
        if not nickname:
            nickname = "Anonym"
        self.nickname = nickname
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            
            self.login_frame.destroy()
            
            self.create_chat_widgets()
            
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
        except Exception as e:
            print(f"Error while Connecting: {e}")
            if self.sock:
                self.sock.close()
            self.create_login_widgets()

    def create_chat_widgets(self):
        self.title("ChatRoom")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.chat_area = ctk.CTkTextbox(self)
        self.chat_area.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")
        self.chat_area.configure(state="disabled", font=ctk.CTkFont(size=14))

        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=0)

        self.msg_entry = ctk.CTkEntry(input_frame, placeholder_text="Type Message!", height=40, font=ctk.CTkFont(size=14))
        self.msg_entry.grid(row=0, column=0, sticky="ew")
        self.msg_entry.bind("<Return>", self.send_message_event)

        self.send_button = ctk.CTkButton(input_frame, text="Send", command=self.send_message_event, width=80, height=40)
        self.send_button.grid(row=0, column=1, padx=(10, 0))

    #User Color
    def get_user_color(self, nickname):
        if nickname not in self.user_colors:
            color = random.choice(Q.color_palette)
            self.user_colors[nickname] = color
        return self.user_colors[nickname]

    def display_message(self, message):
        self.chat_area.configure(state="normal")

        if ": " not in message:
            self.chat_area.tag_config("system", foreground="gray") 
            self.chat_area.insert("end", f"{message}\n", "system")
        
        else:
            try:
                name, content = message.split(": ", 1)
                color = self.get_user_color(name) 
                tag_name = f"color_{name}"
                
                if tag_name not in self.chat_area.tag_names():
                    try:
                        self.chat_area.tag_config(tag_name, foreground=color, weight="bold") 
                    except Exception as e:
                        print(f"Error creating UserTag: {e}")
                
                self.chat_area.insert("end", f"{name}:", tag_name)
                
                self.chat_area.insert("end", f" {content}\n")
                
            except ValueError:
                self.chat_area.insert("end", f"{message}\n")

        self.chat_area.see("end") 
        self.chat_area.configure(state="disabled")
    def receive_messages(self):
        while True:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if message == 'NICK':
                    self.sock.send(self.nickname.encode('utf-8'))
                elif message:
                    self.after(0, self.display_message, message) 
                else:
                    break
            except Exception as e:
                print(f"Error while Receiving: {e}")
                if self.sock:
                    self.sock.close()
                break

    def send_message_event(self, event=None):
        message = self.msg_entry.get()
        if message:
            full_message = f"{self.nickname}: {message}"
            try:
                self.sock.send(full_message.encode('utf-8'))
                self.msg_entry.delete(0, 'end')
            except Exception as e:
                print(f"Sending Error: {e}")


    def on_closing(self):
        if self.sock:
            self.sock.close()
        self.destroy()

if __name__ == "__main__":
    app = ChatClient(HOST, PORT)
    app.mainloop()