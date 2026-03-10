# Relazione DevOps

In questa relazione vengono descritti gli strumenti **DevOps** utilizzati durante lo sviluppo del progetto e il loro ruolo nell'automatizzazione delle diverse fasi del ciclo di vita dell'applicazione, dalla gestione del codice fino al deployment dell'infrastruttura.

## Introduzione

Il progetto consiste nella realizzazione di un ambiente di simulazione per un ICS (Industrial Control System). 
L'infrastruttura è stata progettata per essere eseguita sia in modalità completamente virtualizzata, basata su container **Docker**, sia in un ambiente fisico, distribuito su diversi dispositivi **Raspberry Pi**.
Lo scopo del progetto è quello di mostrare e mitigare le vulnerabilità di una classica rete industriale, per questo motivo l'ambiente può essere eseguito sia in una configurazione sicura sia in una configurazione insicura, in modo da evidenziare le differenze tra i due scenari.

Per semplificare lo sviluppo, la distribuzione e la gestione dell'infrastruttura, sono stati adottati diversi strumenti **DevOps**, che verranno approfonditi in questo documento:
- **Git**
- **Docker**
- **Docker Compose**
- **GitHub Actions**
- **Ansible**

## Git

**Git** è uno strumento fondamentale per la gestione del codice. 
Oltre alla possibilità di lavorare da dispositivi diversi tramite l'utilizzo di un repository remoto, permette di tracciare tutte le modifiche ai file del progetto nel tempo, rendendo semplice ripristinare versioni precedenti in caso di errori.

Durante lo sviluppo è nata la necessità di mantenere più versioni del codice. 
Il sistema di branching di **Git** ha reso possibile lo sviluppo in parallelo delle diverse varianti del progetto, permettendo inoltre di passare rapidamente tra le varie versioni, rendendo immediato il confronto tra le configurazioni.

Nel repository sono presenti i seguenti branch:
- `unsafe-env` — ambiente insicuro, completamente virtuale.
- `virtual-safe-env` — ambiente sicuro, completamente virtuale.
- `main` — ambiente fisico, con possibilità di avviarlo in configurazione sicura o insicura. 

Il file `.gitignore` è stato configurato per escludere `.env` e certificati `.pem`, evitando così la pubblicazione di informazioni sensibili. 
Sono inoltre esclusi file generati durante l'esecuzione che non è necessario salvare, come `__pycache__` o ambienti virtuali **Python**.

## Docker

**Docker** è stato utilizzato per creare una versione completamente virtualizzata dei componenti della rete. In alcuni casi è stato inoltre possibile eseguire direttamente i container sui **Raspberry Pi**, semplificando la fase di deployment sui dispositivi fisici. 

Per i servizi web come **ScadaBr**, **Logingateway** e **Userhandler** è stato possibile riutilizzare gli stessi Dockerfile della rete virtuale, costruendo le stesse **Docker images** da eseguire direttamente sui **Raspberry Pi** senza alcuna modifica.

Per i componenti **HIL** e **PLC**, **Docker** è stato usato unicamente nella versione virtualizzata, per simulare il comportamento di dispositivi fisici come bracci meccanici e nastri trasportatori. 
Non è stato possibile riutilizzare i **Dockerfile** nell'implementazione fisica, poiché l'utilizzo di container avrebbe reso più complessa la comunicazione con le interfacce hardware dei **Raspberry Pi**.

## Docker Compose

**Docker Compose** è stato utilizzato per definire e orchestrare l'infrastruttura della rete virtualizzata e per facilitare l'esecuzione dei container, anche su alcuni nodi della rete fisica.

### Rete virtuale

Oltre a quello definito nella root del progetto, sono presenti diversi `docker-compose.yaml` distribuiti nelle sottocartelle dei componenti della rete.
I percorsi di questi file vengono specificati nel `.env`, permettendo l'esecuzione congiunta di tutti i servizi necessari alla simulazione dell'infrastruttura.
Questo approccio consente di mantenere ordinata la configurazione dei vari elementi della rete, rendendo l'architettura più modulare e semplificando la gestione delle diverse configurazioni dell'ambiente.

### Rete fisica

Anche in questo caso è stato possibile riutilizzare alcuni `docker-compose.yaml` per eseguire i container direttamente sui **Raspberry Pi**, modificando alcuni parametri di configurazione per adattarli all'ambiente.
Questo è stato particolarmente utile per il router e il controller dell'overlay network **OpenZiti**, permettendo di continuare ad usare le **Docker images** ufficiali cambiando esclusivamente le variabili legate alla rete, non più gestita da **Docker**.
Non è stato possibile utilizzare lo stesso approccio per i tunnelers **OpenZiti**, in quanto non esiste il concetto di sidecar usato per i container, rendendo quindi necessaria l'installazione del servizio `ziti-edge-tunnel` direttamente sui dispositivi della rete ICS.

> **Nota:** la suddivisione dei file `docker-compose.yaml` nelle sottocartelle dei vari componenti si è rivelata particolarmente utile in fase di deployment sui dispositivi fisici, permettendo di riutilizzare selettivamente i servizi necessari su ciascun **Raspberry Pi**.

## GitHub Actions

Per automatizzare alcune operazioni durante lo sviluppo del progetto, è stato utilizzato il sistema di **Continuous Integration** offerto da **GitHub Actions**.
La pipeline è configurata in modo da eseguire una serie di controlli legati alla pulizia e alla correttezza del codice, testando infine il corretto funzionamento dell'intera rete in esecuzione.

### Linting

La prima serie di job è dedicata al linting dei file del repository, in modo da individuare rapidamente errori sintattici e garantire codice ordinato e leggibile.

In particolare vengono eseguiti:

- `actionlint` – per assicurare la correttezza della pipeline stessa.
- `flake8` – per il linting di tutti gli script **Python** e dei web server scritti in **Flask**.
- `hadolint` – per il controllo dei **Dockerfile**.
- `dclint` – per la verifica dei file **Docker Compose**.
- `shellcheck` – per l'analisi degli script shell.
- `htmlhint` – per i template **HTML**.

### Testing

Se tutti i controlli statici sul codice passano i test di linting, l'ultimo job si occupa di avviare l'intera rete virtuale tramite **Docker Compose**, per verificare che ogni servizio si avvii e funzioni correttamente.

In particolare vengono verificati:

- lo stato delle istanze dei **PLC** sfruttando gli healthcheck dei container;
- l'avvio corretto degli **HIL**, controllando i log generati dal container nel momento in cui lo script inizia a comunicare correttamente con il **PLC**;
- il corretto instradamento tramite **Nginx** e il funzionamento del **Logingateway** tramite `curl`;
- l'avvio del servizio **ScadaBr** verificando lo stato dell'interfaccia web tramite `curl`;
- la raggiungibilità del servizio **Userhandler** sempre tramite il comando `curl`.

Questo approccio permette di evitare il testing manuale di ogni servizio dopo modifiche significative ai componenti della rete.
Quest'ultimo passaggio non è però applicabile alla versione fisica del progetto, in quanto risulterebbe molto complesso replicare fedelmente la struttura della rete reale.

## Ansible

Per automatizzare il deployment dell'infrastruttura fisica è stato utilizzato **Ansible**.
I componenti della rete sono distribuiti su diversi **Raspberry Pi**, la cui configurazione manuale risulterebbe lenta e soggetta ad errori.

### Inventory

Il file `inventory.ini` definisce i nodi che compongono la rete e i relativi indirizzi IP.
Ogni **Raspberry Pi** deve essere inserito nell'inventory in modo da poter essere raggiunto da **Ansible** tramite **SSH**, permettendo ai playbook di eseguire comandi direttamente sui dispositivi.

> **Nota:** prima di poter utilizzare **Ansible**, ogni dispositivo deve essere configurato manualmente per consentire l'accesso tramite **SSH** con autenticazione a chiave pubblica.  
> La chiave pubblica del nodo di controllo deve quindi essere copiata sui nodi della rete, ad esempio tramite il comando `ssh-copy-id`.

Gli host sono organizzati in diversi gruppi, cercando di raggruppare gli elementi con installazioni e configurazioni simili tra loro.
In questo modo è inoltre possibile eseguire servizi selettivamente su specifici gruppi di dispositivi utilizzando i `tag` di **Ansible**.

### Playbooks

I playbook di **Ansible** permettono di automatizzare diverse operazioni necessarie alla configurazione e all'esecuzione dell'infrastruttura.

In particolare sono stati sviluppati i seguenti playbook:

- `restart_ntp.yaml` – riavvia il servizio **NTP** su tutti i **Raspberry Pi**, garantendo la sincronizzazione degli orologi di sistema tra i diversi nodi, requisito fondamentale per il corretto funzionamento delle comunicazioni **TLS** all'interno e all'esterno della rete;

- `install_dependencies.yaml` – installa automaticamente tutte le dipendenze necessarie per eseguire i servizi su ogni dispositivo; permette inoltre di distribuire rapidamente i file modificati durante lo sviluppo;

- `runICS.yaml` – avvia o arresta l'infrastruttura ICS nelle diverse modalità utilizzando i tag di **Ansible**:
    - `start` – avvia la configurazione insicura;
    - `start_secure` – avvia la configurazione sicura;
    - `stop` – arresta tutti i servizi della rete.

Grazie a questo approccio è possibile gestire l'intera infrastruttura tramite pochi comandi, semplificando manutenzione e deployment continuo, concetto fondamentale di **DevOps**.

## Miglioramenti possibili

Il progetto dimostra come strumenti **DevOps** possano semplificare sviluppo, testing e deployment di un'infrastruttura complessa. Tuttavia sono possibili ulteriori miglioramenti che potrebbero rendere l'ambiente ancora più robusto e automatizzato.

### Pre-commit hooks

L'introduzione di **pre-commit hooks** permetterebbe di eseguire test e controlli sul codice prima di pubblicare nuove modifiche sul repository remoto.
Questo consentirebbe di individuare più rapidamente eventuali errori, riducendo il numero di pipeline CI fallite e migliorando l'efficienza del processo di sviluppo.

Potrebbero infatti essere eseguiti automaticamente i controlli di linting già presenti nella pipeline di **GitHub Actions**.

### Monitoraggio dell'infrastruttura

L'introduzione di strumenti di monitoraggio permetterebbe di raccogliere metriche sul funzionamento dei servizi e dei dispositivi della rete ICS.

Attualmente il corretto comportamento dell'infrastruttura viene verificato principalmente nell'ambiente virtuale tramite una rapida analisi dei log del sistema.
L'utilizzo di questi servizi permetterebbe invece di osservare continuamente lo stato della rete, includendo anche la versione fisica del progetto, e individuare più rapidamente eventuali anomalie o malfunzionamenti.

Strumenti come **Prometheus** o **Grafana** permetterebbero di visualizzare metriche relative all'utilizzo delle risorse dei **Raspberry Pi**, allo stato dei servizi e al traffico di rete.