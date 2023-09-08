# Darknet Crawler P4 praktikum

Willkommen zu unserem Darknet Crawler im Rahmen des P4 Praktikums. Ziel dieses Praktikums war es das Darknet Forum <a href="http://germania7zs27fu3gi76wlr5rd64cc2yjexyzvrbm4jufk7pibrpizad.onion">"Germania"</a> näher zu untersuchen, dessen Strukturen zu verstehen, um interessante Daten von diesem Forum zu extrahieren und schlußendlich adäquat für den Benutzer aufzubereiten und zu präsentieren.

Um Fehler während der Installation und Handhabung möglichst zu vermeiden folgen Sie bitte den nachfolgend beschriebenen Schritten.

## Vorrausetzungen

Um das Program in Betrieb nehmen zu können benötigen Sie ein Debian System der Version 12 (Bookworm). 

Bitte achten Sie darauf dass Sie möglichst keine Altlasten auf diesem System mitbrigen, dh. es sollte sich bei dem verwendeten Debian System möglichst um eine Neuinstallation handeln. Achten Sie bitte weiterhin darauf dass für Ihren User die Berechtigungen auf dem Dateisystem, insbesondere aber zur Verwendung des `sudo` Befehls korrekt konfiguriert sind. Achten Sie stets bei der Ausführung von Befehlen drauf, dass Sie die entsprechenden Berechtigungen besitzen.

Weiterhin wird der Benutzer aufgefordert, Captcha's zu lösen, da dies nicht Teil unserer Implementierung ist.
Es wird mindestens eine Interaktion mit dem User benötigt. Somit muss sichergestellt werden, dass der Benutzer die Website besuchen kann. 
Dies impliziert die Installation des Tor browsers.

Die Sicherstellung dieser Vorraussetzungen ist nicht teil dieser Arbeit und fällt in den Verantwortungsbereich des Endnutzers.
## Installation der Umgebung

Um die Installation der Produktivumgebung so reibungslos wie möglich zu gestalten nutzen Sie bitte das mitgelieferte Skript `install.sh`, das Sie in dem Projektordner finden. Bitte achten Sie darauf dass dieses Skript ausführbar ist. Dazu geben Sie bitte in Ihrem Terminal folgendes ein:

```
$ sudo chmod +x ./install.sh
```

Nachdem dies geschehen ist führen Sie bitte mit entsprechenden Administrator-Berechtigungen das Skript aus.

```
$ sudo ./install.sh
```
Sofern das Skript erfolgreich ausgeführt wurde sollten Sie in Ihrem Terminal folgenden Text sehen: `"Docker, Docker Compose, Python 3.11.4, virtual environment, and requirements have been installed and executed."`

Am Ende des Installationsskript wird die IP-Addresse der SQL Datenbank ausgegeben, welche für die Visualisierungen erforderlich ist. Daher empfehlen wir Ihnen, die IP-Adresse an geeigneter Stelle abzuspeichern.

## Ausführen des Crawlers
Sofern Sie zuvor erfolgreich das Installationsskript ausgeführt haben, können Sie nun den Crawler starten, in dem Sie das `./run.sh` Skript ausführen. Dabei sollten Sie beachten, dass Ihr aktuelles Arbeitsverzeichnis in dem Projektordner ist.

Stellen Sie ausßerdem sicher, dass das Skript die passenden Berechtigungen hat, indem Sie den folgenden Befehl in Ihrem Terminal ausführen:
```
$ sudo chmod +x ./run.sh
```
Möchten Sie nun den Crawler zu starten, geben Sie folgendes in Ihrem Terminal ein:
```
$ ./run.sh
```
Folgen Sie nun den Anweisungen des Crawlers in Ihrem Terminal. Zusätzlich erhalten Sie in Ihrem Terminal den Log Output des Crawlers, der Ihnen unter anderem den Fortschritt anzeigt.

### Interaktion mit dem Benutzer
Wie bereits vorher angedeuet, wird mindestens eine Interaktion benötigt. Nach Ausführung des `run.sh` Skripts wird der Benutzer aufgefordert das Forum <a href="http://germania7zs27fu3gi76wlr5rd64cc2yjexyzvrbm4jufk7pibrpizad.onion">"Germania"</a> zu besuchen und ein Captcha zu lösen.

Daraufhin wird eine Eingabe erwartet, in dem der Session Cookie übergeben werden soll. Diese finden Sie, nachdem Sie das Captcha gelöst haben, unter den DevTools im Browser (`Strg + Umschalt + I`) im Netzwerk Bereich unter einer der gesendeten Anfragen.
Wenn Sie eine Anfrage auswählen, haben Sie die Option 'Cookies'. Dort finden Sie einen `PHPSESSID` Cookie. Dessen Wert wird erwartet als Input für den Crawler.

## Crawler Optionen
Die implementierten Crawler sammeln Informationen über die Forum Beiträge, Sub-Foren, Posts und Informationen über die Benutzer des Forums.
Nach der Eingabe dse `PHPSESSID` Cookies, werden Informationen über die Foren Beiträge, Sub-Foren und Posts gesammel. Kurz darauf werden Sie aufgeordert eine Zahl von 1 bis 25 auszuwählen. Die Benutzerliste besteht aus 25 Seiten, somit wählen Sie aus, von welcher Seite der Crawler anfangen soll Informationen zu sammeln. Nach Auswahl der Startseite, werden Sie aufgefordert eine von zwei Benutzer Crawlern auszuwählen. 

Bei den Benutzern des Forums gibt es 2 Optionen Informationen zu sammeln:
### 1. Generelle Benutzer Daten
Ähnlich wie bei den Foren, werden hier Informationen über alle Benutzer ab der ausgewählten Startseite gesammelt, die auf der Benutzerliste präsentiert werden. Dieser Crawler benötigt ab dem ersten Cookie keine Interaktion mehr (Stand: 02.09.23). 

### 2. Detaillierte Benutzer Daten
Zusätzlich zu den Informationen, die auf der Benutzerliste präsentiert werden, untersucht der detaillierte Crawler jede Profilseite der Benutzer des Forums.
**Achtung**: Hierbei werden mehrere Interaktionen von Ihnen erwartet, da das Forum den Session Cookie erneuert, um sich vor Bots zu schützen. Somit werden Sie nach Auswahl von diesem Crawler mehrmals aufgefordert Captcha's zu lösen. Achten Sie hierbei bitte auf die Korrektheit der Angaben und Anforderung des Crawlers.

## Visualiserung der Daten

Nachdem der Crawler die extrahierten Daten erfolgreich in die MySQL Datenbank geladen hat, rufen Sie bitte in Ihrer VM über einen Browser die Adresse `localhost:3000` auf und loggen Sie sich dort mit dem Grafana Account und Passwort aus der `docker-compose.yaml` ein. Der Standard Benutzer ist `admin` und das Standard Passwort lautet `changeme`.

Nachdem Sie sich erfolgreich eingeloggt habt, fügen Sie in in Grafana die MySQL Datenbank als Datenquelle hinzu. Dazu gehen Sie im Menü links bitte auf den Reiter "Connections" > "Add new connection" und geben Sie dort im Suchfeld "MySQL" ein und klicken Sie auf den blauen Knopf mit der Aufschrift "Add new data source" im rechten oberen Bereich. Nun geben Sie bitte im Feld "Host" die IP und den Port des MySQL Containers an. Diese erhalten Sie am Ende des Installationsskriptes aber Sie können die IP auch manuell ermitteln. Dazu müssen Sie in dem Terminal Ihrer VM folgenden Befehl eingeben um die IP des MySQL Containers zu ermitteln:
```
docker ps -q --filter "name=mysql" | xargs -I {} docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' {}
```
Die nun zurückgelieferte IP geben Sie bitte in dem Host Feld ein und fügen den Port hinzu, wie z.B. `<IP>:3306`. Als nächstes Geben Sie bitte in dem Feld "Database" den Namen Ihrer Datenbank, im Feld "User" den Benutzernamen Ihres MySQL Benutzers, und im Feld "Password" das Passwort des Benutzers an. Diese Informationen können Sie im `docker-compose.yaml` entnehmen und ändern. Die Standardwerte sind aber:

```
database = "germania"
user = "user"
password = "User1234"
```
Nachdem Sie diese vier Felder ausgefüllt haben, klicken Sie bitte auf dem Ende der Seite auf den blauen Knopf mit der Aufschrift "Save & test" um MySQL als Datenquelle hinzuzufügen.

Suchen Sie bitte in dem Menü auf der linken Seite den Reiter "Dashboards" und klicken Sie auf den Schriftzug "Dashboards". Dort angekommen klicken Sie auf der rechten Seite auf den blauen Knopf mit der Aufschrift "New" > "Import". Ihnen sollte sich nun eine neue Oberfläche "Import Dashboard" öffnen. Hier laden Sie bitte jeweils die Dashboard Konfigurationen hoch, die Sie in dem Ordner `grafana-dashboards` innerhalb des Projektordners finden. Insgesamt sollten Sie dort ein Dashboard `Forums.json` und `UsersGeneral.json` finden.

Um in dem Forum Dashboard den vollen Visualisierungsumfang nutzen zu können müssen Sie allerdings noch ein Grafana Plugin installieren. Dazu rufen Sie bitte über das Menü auf der linken Seite den Reiter "Administration" > "Plugins" auf. Dort angekommen wählen Sie bitte im oberen Bereich beim Feld "State" den Status "All" aus. Anschließend geben Sie in der Suchleiste zum Suchen von Grafana Plugins bitte "Treemap" ein und klicken auf das Plugin vom Autor Marcus Olsson. Dort klicken Sie bitte im oberen rechten Bereich auf den Knopf "Install" um das Plugin zu installieren. Nun sollten Sie auch die letzte Visualisierung des Forum Dashboards nutzen können.

Nachdem Sie diesen Vorgang erfolgreich abgeschlossen haben können Sie nun über die beiden Dashboards jeweils einige ausgewählte Zusammenstellungen der extrahierten Informationen zu den Foren und den Usern des Darknet Forums Germania finden.

Es ist anzumerken, dass Sie als Benutzer natürlich weitere Dashboards erstellen können und jedes bestehende Dashboards um weitere individuelle Visualisierungen erweitern können. Wir ermutigen Sie als Benutzer dazu von dieser Möglichkeit Gebrauch zu machen. Für einen ersten Einstieg schauen Sie gerne auf der [offizielen Webseite von Grafana](https://grafana.com/docs/grafana/latest/getting-started/build-first-dashboard/) vorbei und arbeiten sie sich von dort aus weiter.
