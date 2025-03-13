import time
import json
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from PIL import Image
import connection
import threading



class Sidebar(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app)
        self.configure(width=150, height=700, corner_radius=0, fg_color="#E3FDFF")
        self.place(x=0, y=0)

        self.server_button_list = {}
        self.parent = app

        # Logo
        logo_path = "assets/logo.png"
        try:
            self.logo_image = Image.open(logo_path).resize((40, 55))
            self.logo_photo = ctk.CTkImage(light_image=self.logo_image, size=(40, 55))
            self.logo_label = ctk.CTkLabel(self, image=self.logo_photo, text="", bg_color="#E3FDFF")
            self.logo_label.place(x=55, y=10)
        except Exception as e:
            print(f"Erreur lors du chargement du logo : {e}")

        self.serverlistlabel = ctk.CTkLabel(
            self,
            text="Liste des serveurs:",
            font=("Arial", 12, "bold"),
            fg_color="#E3FDFF",
            bg_color="#E3FDFF",
            text_color="black"
        )
        self.serverlistlabel.place(x=20, y=80)

        self.add_server_button = ButtonImage(self, "assets/add_server.png", "assets/add_server_hover.png",
                                             "assets/add_server.png",
                                             "assets/add_server_hover.png")
        self.add_server_button.configure(command=lambda: self.parent.configserverpage.show_add_server_page())
        self.update_serverlist("new")  # Met à jour la liste de serveur pour la première fois

    # Met à jour la liste des serveurs
    def update_serverlist(self, session_type="old"):
        with open("serverlist.json", "r") as f:  # Charge la liste des serveurs
            try:
                self.parent.jsonserverlist = json.load(f)
                # Initisalise la liste des noms des serveurs
                serverlist = [server for server in self.parent.jsonserverlist]

            except Exception as e:
                # Si la lecture du fichier serverlist.json est impossible, défini la liste comme vide
                self.parent.jsonserverlist = {}
                serverlist = []

        if len(serverlist) > 0:
            if len(self.parent.serverlist) != 0:  # J'en ai aucune idée
                for serv in self.parent.serverlist:
                    self.parent.serverlist[serv].place_forget()

            for i in range(len(serverlist)):
                serv = serverlist[i]
                if serverlist[i] not in self.parent.serverlist:  # Regarde si il y a des nouveau serveur
                    self.parent.serverlist[serv] = Server(self.parent, self, serv)  # Crée un serveur
                self.parent.serverlist[serv].place(x=0, y=110 + (i * 30))  # Place le serveur
            self.add_server_button.place(relx=0.4, y=110 + (len(serverlist) * 30))  # Place le bouton d'ajout de serveur

            if session_type == "new":
                # Affiche la page de connexion du premier serveur
                self.parent.serverlist[serverlist[0]].show_server_page()

                pass

        else:
            self.parent.configserverpage.show_add_server_page("no_serv")
            self.add_server_button.place_forget()


class Loginpage:
    def __init__(self, parent, server):
        self.background = Background(parent)
        self.parent = parent
        self.server = server
        self.background.place_forget()

        # Tasker
        tasker_path = "assets/Tasker.png"
        try:
            self.tasker_image = Image.open(tasker_path).resize((235, 97))
            self.tasker_photo = ctk.CTkImage(light_image=self.tasker_image, size=(235, 97))
            self.tasker_label = ctk.CTkLabel(self.background, image=self.tasker_photo, text="", bg_color="#E3FDFF")
            self.tasker_label.place(x=305, y=30)
        except Exception as e:
            print(f"Erreur lors du chargement de l'image Tasker : {e}")

        # Label d'entrée de texte
        self.title_label = ctk.CTkLabel(
            self.background,
            text=server.name,
            font=("Arial", 15, "bold"),
            fg_color="#E3FDFF",
            bg_color="#E3FDFF",
            text_color="black"
        )
        self.title_label.place(x=20, y=20)

        # Fond de la carte de connexion
        self.background_connexion_card = Background(self.background)
        self.background_connexion_card.configure(width=350, height=400, fg_color="#91C4F9")
        self.background_connexion_card.place(x=247, rely=0.2)

        # Label Connexion
        self.connexion_card_label = ctk.CTkLabel(
            self.background_connexion_card,
            text="Connexion",
            font=("Arial", 30, "bold"),
            fg_color="transparent",
            bg_color="transparent",
            text_color="#03244F"
        )
        self.connexion_card_label.place(x=100, y=30)

        # Formulaire de connexion
        self.ipfield = LabelField(self.background_connexion_card)
        self.ipfield.configure(fg_color="#91C4F9", width=250)
        self.ipfield.label.configure(fg_color="#91C4F9", text="Ip")
        self.ipfield.text_entry.insert("end", server.ip)
        self.ipfield.text_entry.configure(width=250)
        self.ipfield.place(x=50, y=100)

        self.pswdfield = LabelField(self.background_connexion_card)
        self.pswdfield.configure(fg_color="#91C4F9", width=250)
        self.pswdfield.label.configure(fg_color="#91C4F9", text="Password")
        self.pswdfield.text_entry.configure(width=250, show="*")
        self.pswdfield.place(x=50, y=180)

        self.show_pswd_btn = ButtonImage(self.pswdfield.text_entry, "assets/mask.png", "assets/mask_hover.png", "assets/show.png",
                                         "assets/show_hover.png")
        self.show_pswd_btn.configure(hover_color="#ffffff", command=lambda: self.show_pswd())
        self.show_pswd_btn.place(x=207, y=6)

        self.connexion_btn = Button(self.background_connexion_card)
        self.connexion_btn.configure(width=250, bg_color="#91C4F9", fg_color="#03244F",
                                     command=lambda: self.connect_to_server(), text="Connexion")
        self.connexion_btn.place(x=50, y=290)

        self.status = ctk.CTkLabel(
            self.background_connexion_card,
            text="",
            font=("Arial", 12, "bold"),
            fg_color="#91C4F9",
            bg_color="#91C4F9",
            text_color="black"
        )

    def show_login_page(self):
        self.background.place(x=165, y=15)
        self.background.lift()

    def show_pswd(self):
        if self.pswdfield.text_entry.cget("show") == "*":
            self.pswdfield.text_entry.configure(show="")
            self.show_pswd_btn.toggle_image()

        else:
            self.pswdfield.text_entry.configure(show="*")

    def connect_to_server(self):
        self.status.configure(text="En attente de connexion..", text_color="black")
        self.status.place(x=50, y=255)
        # Crée un thread pour ne pas arreter le programme durant la connexion
        connect_thread = threading.Thread(target=self.connect_thread)
        connect_thread.start()

    def connect_thread(self):
        server_name = self.title_label.cget("text")
        ip = self.ipfield.text_entry.get()
        password = self.pswdfield.text_entry.get()
        self.parent.serverlist[server_name].password = password
        try:
            self.parent.serverlist[server_name].update_status("Connecting")

            socket = connection.connect_to_server(ip, 55555, password,
                                                  self.parent.jsonserverlist[server_name]["certificat"])
            if socket:
                self.server.status = "Connected"
                self.server.create_server_page()
                self.server.socket = socket
                dispath_data = threading.Thread(target=self.server.receive_data)
                dispath_data.start()
            else:
                self.status.configure(text="Mot de passe incorrect.", text_color="red")
                self.parent.serverlist[server_name].update_status("Disconnected")
                return

        except Exception as e:
            self.status.configure(text="Impossible de se connecter.", text_color="red")
            print(f"Erreur de connexion {e}")
            self.server.update_status("Disconnected")
            return

        self.server.update_status("Connected")
        self.server.show_server_page()


class ControlMetricTab(ctk.CTkTabview):
    def __init__(self, parent, server):
        super().__init__(parent)
        self.server = server
        self.server_name = server.name

        self.restart_button = ButtonImage(self, "assets/restart.png", "assets/restart_hover.png", "assets/restart.png",
                                          "assets/restart_hover.png")
        self.restart_button.configure(command=lambda: self.restart_server(), bg_color="#ffffff", fg_color="#ffffff",
                                      hover_color="#ffffff")
        self.restart_button.place(x=790, y=7)

        self.disconnect_btn = ButtonImage(self, "assets/exit.png", "assets/exit_hover.png", "assets/exit.png",
                                          "assets/exit_hover.png")
        self.disconnect_btn.configure(command=lambda: self.disconnect_server(), bg_color="#ffffff", fg_color="#ffffff",
                                      hover_color="#ffffff")
        self.disconnect_btn.place(x=760, y=7)

        self.server_name_label = ctk.CTkLabel(
            self,
            text=self.server_name,
            font=("Arial", 15, "bold"),
            fg_color="#ffffff",
            bg_color="#ffffff",
            text_color="black"
        )

        self.server_name_label.place(x=20, y=10)

        self.restart_screen = ctk.CTkFrame(self, width=855, height=680, bg_color="#FFFFFF", fg_color="#FFFFFF")
        label = ctk.CTkLabel(self.restart_screen, text="Redémarrage en cours...", font=("Arial", 20, "bold"),
                             text_color="#000000")
        label.place(relx=0.5, rely=0.5, anchor="center")

        self.app_instance = parent

        # create tabs
        self.add("Controles")
        self.add("Metriques")

        self.configure(
            parent,
            width=875,
            height=690,
            fg_color="#ffffff",
            bg_color="#ffffff",
            segmented_button_fg_color="#ffffff",
            segmented_button_selected_color="#E3FDFF",
            segmented_button_unselected_color="#FCFAFA",
            segmented_button_selected_hover_color="#E3FDFF",
            segmented_button_unselected_hover_color="#E3FDFF",
            text_color="black",
            corner_radius=10)

        # add widgets on tabs
        self.page1 = Controlpage(self.tab("Controles"), self.app_instance, server)
        self.page2 = Metricpage(self.tab("Metriques"), self.app_instance, server)

        self.after(100, self.check_tab)

    def check_tab(self):
        onglet_selectionne = self.get()  # Obtenir l'onglet sélectionné
        if onglet_selectionne == "Metriques":
            self.page2.insert_data()

        # Relancer la vérification après 100ms
        self.after(1500, self.check_tab)

    def restart_server(self):
        print("Redémarrage serveur...")
        connection.send_commands(self.server.socket, "sleep 1 && shutdown -r 0")

    def show_restart_screen(self):
        self.restart_screen.place(x=10, y=0)
        self.restart_screen.lift()
        reconnect_to_server = threading.Thread(target=self.reconnect_to_server)
        reconnect_to_server.start()

    def reconnect_to_server(self):
        time.sleep(20)
        new_client_socket = None
        while not new_client_socket:
            try:
                new_client_socket = connection.connect_to_server(self.server.ip, 55555, self.server.password,
                                                                 self.app_instance.jsonserverlist[self.server_name][
                                                                     "certificat"])
                if new_client_socket:
                    self.restart_screen.place_forget()
                    self.server.socket = new_client_socket
                    try:
                        self.server.serverpage.destroy()
                    except Exception as e:
                        pass
                    self.server.create_server_page()
                    self.server.show_server_page()

                    dispath_data = threading.Thread(target=self.server.receive_data)
                    dispath_data.start()
                break
            except Exception as e:
                print(f"Erreur lors de la reconnexion au serveur : {e}")
            time.sleep(5)


    def disconnect_server(self):
        connection.close_connection(self.server.socket)
        self.server.update_status("Disconnected")
        self.server.serverpage.place_forget()
        self.server.show_server_page()


class Controlpage(ctk.CTkFrame):
    def __init__(self, parent, app_instance, server):
        super().__init__(parent)
        self.app_instance = app_instance
        self.server = server
        self.configure(
            height=700,
            width=874,
            fg_color="#ffffff")
        self.place(x=0, y=0)

        # Label entrée de texte
        self.label = ctk.CTkLabel(
            self,
            text="Entrez la commande à exécuter :",
            font=("Arial", 15, "bold"),
            fg_color="#ffffff",
            bg_color="#ffffff",
            text_color="black"
        )
        self.label.place(x=170, y=90)

        # Entrée de texte
        self.text_command = ctk.CTkTextbox(
            self,
            fg_color="#E3FDFF",
            bg_color="#ffffff",
            text_color="#000000",
            height=40,
            width=576,
            corner_radius=12
        )
        self.text_command.place(x=170, y=120)

        # Logo/bouton lancer la commande
        self.Lancer_button = ctk.CTkButton(
            self,
            text="Exécuter",
            fg_color="#E3FDFF",
            hover_color="#00ADC2",
            text_color="black",
            font=("Arial", 14),
            command=lambda: self.execute_command()

        )
        self.Lancer_button.place(x=610, y=170)

        self.console_output = ctk.CTkTextbox(
            self,
            fg_color="#D9D9D9",
            bg_color="#D9D9D9",
            text_color="#000000",
            height=385,
            width=874,
        )
        self.console_output.place(x=0, y=250)

    def execute_command(self):
        command = self.text_command.get("1.0", "end-1c")
        connection.send_commands(self.server.socket, command)


class Metricpage(ctk.CTkFrame):

    def __init__(self, parent, app_instance, server):
        super().__init__(parent)
        self.app_instance = app_instance
        self.server = server
        self.processus = [None]
        self.configure(
            height=700,
            width=874,
            fg_color="#ffffff")
        self.place(x=0, y=0)

        # Label entrée de texte
        label = ctk.CTkLabel(
            self, text="Entrez le PID du processus a arrêter", font=("Arial", 15, "bold"), fg_color="#ffffff",
            bg_color="#ffffff", text_color="black"
        )
        label.place(x=170, y=70)

        # Entrée de texte
        self.text_command = ctk.CTkTextbox(
            self,
            fg_color="#E3FDFF",
            bg_color="#ffffff",
            text_color="#000000",
            height=40,
            width=576,
            corner_radius=12
        )
        self.text_command.place(x=170, y=100)

        # Logo/bouton lancer la commande
        Lancer_button = ctk.CTkButton(
            self,
            text="Arrêter",
            fg_color="#E3FDFF",
            hover_color="#00ADC2",
            text_color="black",
            font=("Arial", 14),
            command=lambda: self.kill_process()
        )
        Lancer_button.place(x=610, y=150)

        # define columns
        columns = ('PID', 'Processus', 'CPU', 'RAM')

        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        self.tree.configure(height=20)
        for elt in columns:
            self.tree.heading(elt, text=elt)

        scrollbar = ctk.CTkScrollbar(self, command=self.tree.yview)
        scrollbar.configure(height=400)
        scrollbar.place(x=810, y=220)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.place(x=25, y=200)

    def insert_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            connection.send_commands(self.server.socket, "show_metrics")
        except Exception as e:
            return
        for proc in self.processus:
            if proc:
                self.tree.insert('', tk.END, values=(
                    proc["pid"], proc["name"], str(proc["cpu_percent"]) + " %", str(proc["memory_usage_mb"]) + " Mb"))

    def kill_process(self):
        process_pid = self.text_command.get("1.0", "end-1c")
        connection.send_commands(self.server.socket, f"Kill {process_pid}")


class ConfigServerPage:
    def __init__(self, parent):

        self.background = Background(parent)

        self.page_title = ctk.CTkLabel(
            self.background,
            text="XXXXXXX",
            font=("Arial", 15, "bold"),
            fg_color="#E3FDFF",
            bg_color="#E3FDFF",
            text_color="black"
        )

        self.page_title.place(x=20, y=20)

        # Tasker
        tasker_path = "assets/Tasker.png"
        try:
            self.tasker_photo = ctk.CTkImage(light_image=Image.open(tasker_path).resize((235, 97)), size=(235, 97))
            self.tasker_label = ctk.CTkLabel(self.background, image=self.tasker_photo, text="", bg_color="#E3FDFF")
            self.tasker_label.place(x=295, y=50)

        except Exception as e:
            print(f"Erreur lors du chargement de l'image Tasker : {e}")

        # Formulaire

        self.namefield = LabelField(self.background)
        self.namefield.label.configure(text="Nom")
        self.namefield.place(x=122, y=140)

        self.ipfield = LabelField(self.background)
        self.ipfield.label.configure(text="Ip")
        self.ipfield.place(x=122, y=220)

        self.certfield = LabelField(self.background, "TextBox")
        self.certfield.configure(height=300, width=600)
        self.certfield.label.configure(text="Certificat du serveur")
        self.certfield.text_entry.configure(height=250, width=600)
        self.certfield.place(x=122, y=300)

        self.add_server_btn = Button(self.background)
        self.add_server_btn.configure(text="Ajouter", command=lambda: self.add_server())

        # self.cancel_btn = Button(self.background)
        # self.cancel_btn.configure(text="Annuler", command=lambda: self.test())

        self.edit_server_btn = Button(self.background)
        self.edit_server_btn.configure(text="Modifier")

        self.delete_server_btn = Button(self.background)
        self.delete_server_btn.configure(text="Supprimer", command=lambda: self.test(), fg_color="#FF5E5E")

        self.warning_message = ctk.CTkLabel(
            self.background,
            text="message",
            font=("Arial", 12),
            fg_color="#E3FDFF",
            bg_color="#E3FDFF",
            text_color="red"
        )

        self.parent = parent

    def show_add_server_page(self, status="serv"):
        self.background.place(x=165, y=15)

        for srv in self.parent.serverlist:  # Retirer de l'affichage les potentiels Frame génante
            if self.parent.serverlist[srv].serverpage:
                self.parent.serverlist[srv].serverpage.place_forget()
            self.parent.serverlist[srv].loginpage.background.place_forget()

        # Réinitialisr les champs
        self.warning_message.place_forget()
        self.namefield.text_entry.delete(0, "end")
        self.ipfield.text_entry.delete(0, "end")
        self.certfield.text_entry.delete(0.0, "end")
        self.edit_server_btn.place_forget()
        self.delete_server_btn.place_forget()

        self.add_server_btn.place(x=620, y=600)
        if status == "no_serv":
            """self.cancel_btn.place_forget()"""
        else:
            """ self.cancel_btn.place(x=500, y=600)"""

        self.page_title.configure(text="Ajouter un serveur")

    def show_edit_server_page(self, server):
        self.background.place(x=165, y=15)
        for srv in self.parent.serverlist:  # Retirer de l'affichage les potentiels Frame génante
            if self.parent.serverlist[srv].serverpage:
                self.parent.serverlist[srv].serverpage.place_forget()
            self.parent.serverlist[srv].loginpage.background.place_forget()

        # Réinitialisr les champs
        self.warning_message.place_forget()
        self.namefield.text_entry.delete(0, "end")
        self.ipfield.text_entry.delete(0, "end")
        self.certfield.text_entry.delete(0.0, "end")

        self.edit_server_btn.place(x=620, y=600)
        self.edit_server_btn.configure(command=lambda: self.edit_server(server.name))
        # self.cancel_btn.place(x=500, y=600)
        self.delete_server_btn.place(x=500, y=600)
        self.delete_server_btn.configure(command=lambda: self.delete_server(server))
        self.page_title.configure(text=f"Modification serveur: {server.name}")

        # Récupération des placeholders des champs
        with open("serverlist.json", "r") as f:
            self.parent.jsonserverlist = json.load(f)

        self.namefield.text_entry.insert("end", server.name)
        self.ipfield.text_entry.insert("end", self.parent.jsonserverlist[server.name]["ip"])
        self.certfield.text_entry.insert("end", self.parent.jsonserverlist[server.name]["certificat"])

    def test(self):
        print("zizi")

    def add_server(self):
        # VERIFIER L'ABSENCE DE SERVEUR DU MEME NOM AVANT AJOUT !
        nom = self.namefield.text_entry.get().strip()
        ip = self.ipfield.text_entry.get().strip()
        certificat = self.certfield.text_entry.get("0.0", "end").strip()

        if len(nom) > 0 and len(ip) > 0 and len(certificat) > 0:  # Vérifie que tous les champs soit bien remplis
            for serv in self.parent.jsonserverlist:
                if serv == nom:  # Empeche le doublon des noms
                    self.show_warning_message("Il existe déja un serveur portant ce nom", 160, 140)
                    return
            try:
                with open("serverlist.json", "r") as f:
                    self.parent.jsonserverlist = json.load(f)
            except Exception as e:
                pass
            # Ajoute le serveur a la liste des sevreurs
            self.parent.jsonserverlist[nom] = {"ip": ip, "certificat": certificat}

            with open("serverlist.json", "w") as f:  # Sauvegarde dans le fichier
                json.dump(self.parent.jsonserverlist, f, indent=2)

            # Supprime tous les boutons pour les replacer
            for button in self.parent.sidebar.server_button_list:
                self.parent.sidebar.server_button_list[button][0].destroy()
                self.parent.sidebar.server_button_list[button][1].destroy()
            self.parent.sidebar.update_serverlist()
            self.parent.serverlist[nom].show_server_page()
        else:
            self.show_warning_message("Tous les champs doivent etre renseigné")

    def edit_server(self, server_name):
        nom = self.namefield.text_entry.get().strip()
        ip = self.ipfield.text_entry.get().strip()
        certificat = self.certfield.text_entry.get("0.0", "end").strip()
        new_server = (nom, {"ip": ip, "certificat": certificat})

        if len(nom) > 0 and len(ip) > 0 and len(certificat) > 0:
            if nom != server_name:
                for serv in self.parent.jsonserverlist:  # Empeche le doublon des noms
                    if serv == nom:
                        self.show_warning_message("Il existe déja un serveur portant ce nom", 160, 140)
                        return

                # Permet de garder l'emplacement du serveur dans la liste
                items = list(self.parent.jsonserverlist.items())
                index = items.index((server_name, self.parent.jsonserverlist[server_name]))
                items.insert(index, new_server)
                self.parent.jsonserverlist = dict(items)
                del self.parent.jsonserverlist[server_name]
            else:
                self.parent.jsonserverlist[nom] = {"ip": ip, "certificat": certificat}
                self.parent.serverlist[server_name].update()

            with open("serverlist.json", "w") as f:
                json.dump(self.parent.jsonserverlist, f, indent=2)
            self.parent.sidebar.update_serverlist()
            self.parent.serverlist[nom].show_server_page()
        else:
            self.show_warning_message("Tous les champs doivent etre renseigné")

    def delete_server(self, server):
        self.show_add_server_page()
        del self.parent.jsonserverlist[server.name]

        with open("serverlist.json", "w") as f:
            json.dump(self.parent.jsonserverlist, f, indent=2)

        server.delete_server()
        self.parent.sidebar.update_serverlist()

    def cancel(self):
        pass

    def show_warning_message(self, message, x=122, y=600):
        self.warning_message.configure(text=message)
        self.warning_message.place(x=x, y=y)


class Server(ctk.CTkFrame):
    def __init__(self, parent, parentframe, server_name):
        super().__init__(parentframe)
        self.name = server_name
        self.ip = parent.jsonserverlist[server_name]["ip"]
        self.parent = parent
        self.serverpage = None
        self.loginpage = Loginpage(self.parent, self)
        self.loginpage.show_login_page()
        self.socket = None
        self.status = "Disconnected"
        self.password = ""

        self.configure(
            parentframe,
            height=30,
            width=150,
            fg_color="#E3FDFF"
        )

        self.server_login_button = ctk.CTkButton(
            self, text=self.name,
            text_color="black",
            bg_color="transparent",
            font=("Arial", 15),
            width=40,
            fg_color="transparent",
            hover_color="#00ADC2",
            command=lambda: self.show_server_page()
        )
        self.server_login_button.place(x=10, y=0)

        edit_server_btn = ButtonImage(self, "assets/edit.png", "assets/edit_hover.png", "assets/edit.png",
                                      "assets/edit_hover.png")
        edit_server_btn.configure(command=lambda: parent.configserverpage.show_edit_server_page(self))
        edit_server_btn.place(x=100, y=0)

    def show_server_page(self):
        if self.status == "Connecting" or self.status == "Disconnected":
            self.loginpage.show_login_page()
            for srv in self.parent.serverlist:
                if self.parent.serverlist[srv].serverpage:
                    self.parent.serverlist[srv].serverpage.place_forget()

        elif self.status == "Connected":
            for srv in self.parent.serverlist:
                if self.parent.serverlist[srv].serverpage:
                    self.parent.serverlist[srv].serverpage.place_forget()
                self.parent.serverlist[srv].loginpage.background.place_forget()
                self.parent.configserverpage.background.place_forget()

            self.serverpage.place(x=150, y=10)

    def create_server_page(self):
        self.serverpage = ControlMetricTab(self.parent, self)

    def delete_server(self):
        if self.status == "Connected" or self.status == "Connecting":
            connection.close_connection(self.socket)
        self.destroy()
        del self.parent.serverlist[self.name]

    def update(self):
        self.ip = self.parent.jsonserverlist[self.name]["ip"]
        self.loginpage = Loginpage(self.parent, self)

    def update_status(self, new_status):
        self.status = new_status

        if new_status == "Connected":  # Permet de réinitialiser la page de connexion
            self.loginpage.background.place_forget()
            self.loginpage = Loginpage(self.parent, self)

    def receive_data(self):
        while True:
            try:
                servername, destination, data = connection.receive_data(self.socket)
            except Exception as e:
                print("Arret de la récupération des données")
                break
            if destination == "cmd":
                self.serverpage.page1.console_output.insert("end", data + "\n")
                if data == "Restarting...":
                    self.serverpage.show_restart_screen()
                    connection.close_connection(self.socket)
                    break
            elif destination == "metrics":
                self.serverpage.page2.processus = data





class Background(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.configure(
            parent,
            height=670,
            width=844,
            corner_radius=20,
            fg_color="#E3FDFF"
        )

class LabelField(ctk.CTkFrame):
    def __init__(self, parent, entry_type="Entry"):
        super().__init__(parent)

        self.configure(
            parent,
            fg_color="#E3FDFF",
            height=85,
            width=300,
        )

        self.label = ctk.CTkLabel(
            self,
            text="xxxxxxxxx",
            font=("Arial", 15, "bold"),
            fg_color="#E3FDFF",
            bg_color="#E3FDFF",
            text_color="black"
        )
        self.label.place(x=0, y=0)

        if entry_type == "TextBox":
            self.text_entry = ctk.CTkTextbox(
                self,
                fg_color="#ffffff",
                bg_color="#E3FDFF",
                text_color="#000000",
                height=40, width=250,
                corner_radius=12,
                border_color="#ffffff"
            )
            self.text_entry.place(x=0, y=30)
        else:
            self.text_entry = ctk.CTkEntry(
                self,
                fg_color="#ffffff",
                bg_color="#E3FDFF",
                text_color="#000000",
                height=40, width=250,
                corner_radius=12,
                border_color="#ffffff"
            )
            self.text_entry.place(x=0, y=30)


class Button(ctk.CTkButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(
            parent,
            height=40,
            width=100,
            corner_radius=12,
            text="xxxxxxxx",
            font=("Arial", 15, "bold"),
            fg_color="#00ADC2",
            bg_color="#E3FDFF",
            hover_color="#757575",
        )


class ButtonImage(ctk.CTkButton):
    def __init__(self, parent, icon_path, hover_icon_path, toggled_icon_path, toggled_hover_icon_path):
        super().__init__(parent)

        self.parent = parent
        self.is_toggled = False  # État du bouton

        try:
            # Images par défaut
            self.image = ctk.CTkImage(light_image=Image.open(icon_path))
            self.hover_image = ctk.CTkImage(light_image=Image.open(hover_icon_path))

            # Images après le clic (toggle)
            self.toggled_image = ctk.CTkImage(light_image=Image.open(toggled_icon_path))
            self.toggled_hover_image = ctk.CTkImage(light_image=Image.open(toggled_hover_icon_path))
        except Exception as e:
            print(f"Erreur lors du chargement des icônes : {e}")

        self.configure(
            image=self.image,
            text="",
            fg_color="transparent",
            bg_color="transparent",
            hover_color="#E3FDFF",
            width=10,
            cursor="hand2",
            command=self.toggle_image  # Clic pour changer l'image
        )

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        """Change l'image au survol, en fonction de l'état du bouton"""
        if self.is_toggled:
            self.configure(image=self.toggled_hover_image)
        else:
            self.configure(image=self.hover_image)

    def on_leave(self, event):
        """Remet l'image normale quand la souris quitte le bouton"""
        if self.is_toggled:
            self.configure(image=self.toggled_image)
        else:
            self.configure(image=self.image)

    def toggle_image(self):
        """Change l'image quand on clique et conserve l'effet hover"""
        self.is_toggled = not self.is_toggled
        self.configure(image=self.toggled_image if self.is_toggled else self.image)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.servers = {}

        self.history_nav_page = [ctk.CTkFrame(self)]

        self.title("Tasker")
        self.jsonserverlist = {}
        self.serverlist = {}
        self.configserverpage = ConfigServerPage(self)
        self.sidebar = Sidebar(self)

        # Dimensions de la fenêtre
        window_width = 1024
        window_height = 700
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_offset = (screen_width - window_width) // 2
        y_offset = (screen_height - window_height) // 2

        # Appliquer la géométrie
        self.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")
        self.configure(fg_color="#ffffff")  # Couleur de fond principale




if __name__ == "__main__":
    monitoringApp = App()

    monitoringApp.mainloop()
