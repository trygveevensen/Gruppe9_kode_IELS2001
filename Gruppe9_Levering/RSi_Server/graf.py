import math
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import calendar

now = datetime.now()
fargeIndex = ["b","g","r","m","c","m","y","k","w"]


filnavn = "/var/www/html/data.txt"
df = pd.read_csv(filnavn, sep=",")

datatypes = df.columns.tolist()
datatypes.remove("tid")
datatypes.remove("sensor")


listeSensorNokkel = list(set(df["sensor"].tolist()))
listeSensorNokkel.sort()
listeSensorDf = []
for i in listeSensorNokkel:
    listeSensorDf.append(df[df['sensor'] == i])

ordbokEnhet = {
    "Temperatur": "C",       # Celsius
    "Luftfuktighet": "%",    # Prosent
    "Lufttrykk": "hPa",      # Hektopascal
    "Hastighet": "m/s",      # Meter per sekund
    "Lengde": "m",           # Meter
    "Masse": "kg",           # Kilogram
    "Tid": "s",              # Sekunder
    "Energi": "J",           # Joule
    "Effekt": "W",           # Watt
    "Volum": "L",            # Liter
    "Strømstyrke": "A"       # Ampere
}


ordbokSkala = {
    "D": "I dag",
    "W": "Denne uka",
    "M": "Denne måneden",
    "Y": "I år",
    "T": "Totalt"
}
def plotForIntervall(type):
    now = datetime.now()
    match type:
        case "D":
            xFormat = "%H:%M"
            offset = timedelta(hours=23.99)
            startdate = (now - timedelta(hours=now.hour)).replace(minute=0, second=0, microsecond=0)
            enddate = startdate + offset
            intervall = mdates.HourLocator()
        case "W":
            xFormat = "%a"
            offset = timedelta(days=6,hours=23.99)
            startdate = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            enddate = startdate + offset
        case "M":
            xFormat = "%d"
            nowYear = now.year
            nowMonth = now.month
            offset = timedelta(days=calendar.monthrange(nowYear, nowMonth)[1]-0.01)
            startdate = (now - timedelta(days=now.day-1)).replace(hour=0,minute=0, second=0, microsecond=0)
            enddate = startdate + offset
            intervall = mdates.DayLocator()
        case "Y":
            xFormat = "%b"
            nowYear = now.year
            offset = timedelta(days = 366-.01 if calendar.isleap(nowYear) else 365-.01)
            startdate = datetime(nowYear,1,1)
            enddate = startdate + offset
        case "T":
            intervall =max(df["tid"].tolist()) - min(df["tid"].tolist())
            exp = math.log10(intervall)//1
            startdateTimestamp = min(df["tid"].tolist())-10**(exp)
            enddateTimestamp = max(df["tid"].tolist())+10**(exp)
            startdate = datetime.fromtimestamp(startdateTimestamp)
            enddate = datetime.fromtimestamp(enddateTimestamp)
        case _:
            print("error")
            return
    fig, axes = plt.subplots((len(datatypes)+1) // 2, 2, figsize=(20, len(datatypes) * 2))  # Adjust figure size dynamically
    axes = axes.flatten()
    for j in range(len(datatypes)):
        datatype = datatypes[j]
        totData = []
        for i in range(len(listeSensorDf)):
            sensortype = listeSensorNokkel[i]
            tid = [datetime.fromtimestamp(j) for j in listeSensorDf[i]["tid"].tolist()]
            data = listeSensorDf[i][datatype].tolist()
            totData.extend(data)
            axes[j].plot(tid,data, label = sensortype,color=fargeIndex[i])

        minste = min(totData)
        if math.isnan(minste):
            minste = 0
        storste = max(totData)
        if math.isnan(storste):
            storste = 1
        dataRange = storste - minste
        margin = dataRange*0.1 #10 prosent margin
        axes[j].set_xlim(startdate, enddate)
        axes[j].set_ylim(minste-margin, storste+margin)
        if type == "T":
            axes[j].xaxis.set_major_locator(mdates.AutoDateLocator())
        else:
            axes[j].xaxis.set_major_formatter(mdates.DateFormatter(xFormat))
        axes[j].set_title(datatype)
        axes[j].set_xlabel("Tid")
        axes[j].set_ylabel(f"{ordbokEnhet[datatype]}")
        axes[j].legend()
        axes[j].grid(True)
        fig.suptitle(f"{ordbokSkala[type]}", fontsize=20)

    fig.tight_layout()
    plt.savefig(f"/var/www/html/Figur_{type}.png")
    plt.close()

plotForIntervall("D")
plotForIntervall("W")
plotForIntervall("M")
plotForIntervall("Y")
plotForIntervall("T")
