import customtkinter
from datetime import date
import os.path
from Connection import ConnectToEd, ConnectToEdPart2, AskForNotes # type: ignore
import pickle
import base64


path = "IdentifiantsED.conf"

    
def Save(data):
    with open(path, 'w') as file:
        pickle.dump(data, file)

def Config():
    file = open(path, "a")
    file.close()
    if os.path.getsize(path) > 0:
        with open(path, 'rb') as file:
            Logins = pickle.load(file)
            Questions(ConnectToEd(Logins[0], Logins[1]))
        return    


customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.geometry("1000x700")

def ConnectionCallback(Token):
    if(RemindMe.get() == 1):
        with open(path, 'wb') as file:
            pickle.dump([username, pswd], file)
    QuestionFrame.destroy()
    PeriodFrame = customtkinter.CTkFrame(master=frame, width = 400, height=200)
    PeriodFrame.pack(pady=20, padx=30, fill="both", expand=False)
    PeriodLabel = customtkinter.CTkLabel(master=PeriodFrame, text="Choisissez la période")
    PeriodLabel.pack(pady=15)
    RawPeriods = GetPeriod(AskForNotes(Token))
    RawPeriods.append(["Toute l'année", None])
    FormattedPeriods = [x[0] for x in RawPeriods]
    optionmenu = customtkinter.CTkOptionMenu(master=PeriodFrame, values=FormattedPeriods)
    optionmenu.pack(pady=40)
    ConfirmButton = customtkinter.CTkButton(master=PeriodFrame, text="Calculer la moyenne", command=lambda: GetNotesForPeriod(Token, optionmenu.get(), PeriodFrame))
    ConfirmButton.pack(pady=60)

def GetNotesForPeriod(Token, Period, ToDestroy):
    codePeriod = ""
    for element in GetPeriod(AskForNotes(Token)):
        if element[0] == Period:
            codePeriod = element[1]
            break
    AllNotes = AskForNotes(Token)["notes"]
    NotesFromPeriod = {}
    if codePeriod == "": #No period found, let's take all notes
        for note in AllNotes:
            if note["codeMatiere"] in NotesFromPeriod:
                NotesFromPeriod[note["codeMatiere"]].append([float(note["valeur"]), float(note["noteSur"])]) #Maybe add coeff here (bruh the franglais)
            else:
                NotesFromPeriod.update({note["codeMatiere"]:[[float(note["valeur"]), float(note["noteSur"])]]})
    else:
        for note in AllNotes:
            if note["codePeriode"] == codePeriod:
                note["valeur"] = note["valeur"].replace(",", ".")
                if note["codeMatiere"] in NotesFromPeriod:
                    NotesFromPeriod[note["codeMatiere"]].append([float(note["valeur"]), float(note["noteSur"])]) #Maybe add coeff here (bruh the franglais)
                else:
                    NotesFromPeriod.update({note["codeMatiere"]:[[float(note["valeur"]), float(note["noteSur"])]]})
    Moyenne(NotesFromPeriod, ToDestroy)



def Questions(data):
    DecodedQuestion = base64.b64decode(data["question"])
    DecodedPurpositions = []
    for proposition in data["propositions"]:
        DecodedPurpositions.append(base64.b64decode(proposition))
    global username, pswd
    username, pswd = str(UsernameEntry.get()), str(PasswordEntry.get()) 
    frame4.destroy()
    global QuestionFrame
    QuestionFrame = customtkinter.CTkFrame(master=frame, width = 400, height=200)
    QuestionFrame.pack(pady=20, padx=30, fill="both", expand=False)
    QuestionLabel = customtkinter.CTkLabel(master=QuestionFrame, text=DecodedQuestion)
    QuestionLabel.pack(pady=15)
    optionmenu = customtkinter.CTkOptionMenu(master=QuestionFrame, values=DecodedPurpositions)
    optionmenu.pack(pady=40)
    ConfirmButton = customtkinter.CTkButton(master=QuestionFrame, text="Confirmer", command=lambda: ConnectionCallback(ConnectToEdPart2(base64.b64encode(optionmenu.get()))))
    ConfirmButton.pack(pady=60)


def GetPeriod(Notes):
    Periods = []
    for Period in Notes["periodes"]:
        if Period["periode"] != "Relevé " and Period["periode"] != "Année": #The space after Relevé is normal, it'in the ED version
            Periods.append([Period["periode"], Period["codePeriode"]])
    return Periods


def Moyenne(NotesFromPeriod, ToDestroy = None):
    if ToDestroy != None:
        ToDestroy.destroy()
    AllMoyennes = []
    for matiere in NotesFromPeriod:
        NotesSum = 0
        NotesCount = 0
        for note in NotesFromPeriod[matiere]:
            NotesSum += note[0]*(20/note[1])
            NotesCount += 1
        AllMoyennes.append(NotesSum/NotesCount)
    MoyenneG = 0
    MoyennesCount = 0
    for moyenne in AllMoyennes:
        MoyenneG += moyenne
        MoyennesCount += 1
    MoyenneG = MoyenneG / MoyennesCount
    label.configure(text=f"Moyenne pour la période: {round(MoyenneG, 2)}")

        
frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=30, fill="both", expand=True)

frame2 = customtkinter.CTkFrame(master=frame, width=500, height=100)
frame2.pack(pady=20, padx=30, fill="both", expand=False)

HelloText = customtkinter.CTkLabel(master=frame2, width=400, height=50, text="Bonjour, nous sommes le " + date.today().strftime("%a %d %B %Y"))
HelloText.pack(pady=5, padx=7)

frame3 = customtkinter.CTkFrame(master=frame, width = 500, height=60)
frame3.pack(pady=20, padx=30, fill="both", expand=False)


label = customtkinter.CTkLabel(master=frame3, width=400, height=50, text="Ici s'afficheront les donnees")
label.pack(pady=15, padx=20)

frame4=customtkinter.CTkFrame(master=frame, width = 400, height=200)
frame4.pack(pady=20, padx=30, fill="both", expand=False)

UsernameEntry= customtkinter.CTkEntry(master=frame4, placeholder_text="Identifiant")
UsernameEntry.pack(pady=12, padx=10)

PasswordEntry= customtkinter.CTkEntry(master=frame4, placeholder_text="Mot de passe", show="*")
PasswordEntry.pack(pady=12, padx=10)


button = customtkinter.CTkButton(master=frame4, text="Connection ED", command= lambda:  Questions(ConnectToEd(UsernameEntry.get(), PasswordEntry.get())))
button.pack(pady=12, padx=10)

RemindMe = customtkinter.CTkCheckBox(master=frame4, text="Se souvenir de moi")
RemindMe.pack(pady=12, padx=10)

Config()


root.mainloop()
