##################PORTUGUÊS##################

INSTALAÇÃO:
Correr o ficheiro "setup.py". Este irá instalar todos os pacotes necessários à execução correta do programa

Windows:
	py setup.py install

Linux:
	python3 setup.py install

----------------------------------	
	
EXECUÇÃO:
Correr o ficheiro "monitor.py"

Windows:
	py monitor.py

Linux:
	python3 monitor.py

----------------------------------
	
FICHEIRO JSON:
	CPU Usage:
		Neste campo define-se os valores mínimos e máximos para os quais uma notificação será enviada a um administrador, caso a percentagem de uso de CPU pelos processos do autopsy atinja ou ultrapasse os mesmos.
		Os parâmetros "min" e "max" correspodem a valores de percentagem. 
			Ex.: "min": "20" -> minimo = 20%
	
	Memory:
		Neste campo define-se os valores mínimos e máximos para os quais uma notificação será enviada a um administrador, caso a memória a ser usada pelos processos do autopsy atinja ou ultrapasse os mesmos.
		Os parâmetros "min" e "max" correspodem a valores de memória em MBytes.
			Ex.: "min": "5000" -> minimo = 5000 MB
			
	Notify:
		Neste campo são definidos todos os parâmetros relativos ao servidor SMTP a ser usado para o envio de todos os emails criados pela aplicação
		O parâmetro "SMTP Server" corresponde ao URL do servidor de SMTP.
			Ex.: "SMTPServer": "smtp.gmail.com" -> URL do servidor SMTP correspode a smtp.gmail.com
		
		O parâmetro "sender mail" corresponde ao email de login no servidor de SMTP bem como ao remetente de todos os emails a serem enviados pela aplicação
			Ex.: "senderEmail": "monautopsy.notify@gmail.com" -> Email do remetente e username para o servidor de SMTP correspode a monautopsy.notify@gmail.com
			
		O parâmetro "receiverEmail" corresponde ao email do destinatário de todos os emails a serem enviados pela aplicação
			Ex.: "receiverEmail": "123456@mail.com" -> Email do destinatário correspode a 123456@mail.com
			
	Time Interval:
		Neste campo define-se os intervalos de tempo (em segundos) da monitorização dos processos do autopsy bem como do envio do relatório periódico relativo à monitorização.
		O parâmetro "process" correspode ao intervalo de tempo da monitorização dos processos do autopsy.
			Ex.: "process": "5" -> Monitorização dos processos do autopsy de 5 em 5 segundos.
		
		O parâmetro "report" correspode ao intervalo de tempo do envio do relatório periódico da monitorização
			Ex.: "report": "120" -> Envio do relatório de 120 em 120 segundos (2 em 2 minutos)
	
----------------------------------
	
##################ENGLISH##################

INSTALATION:
Run "setup.py" file. This file contains every package necessary for the correct execution of the program.

Windows:
	py setup.py install

Linux:
	python3 setup.py instal
	
----------------------------------	

EXECUTION:
Run "monitor.py"

Windows:
	py monitor.py

Linux:
	python3 monitor.py
	
----------------------------------

JSON FILE:
