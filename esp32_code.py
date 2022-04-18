#!/usr/bin/env python
# /etc/init.d/esp32_wifi.py
### BEGIN INIT INFO
# Provides:          esp32_wifi.py
# Required-Start:    $remote_fs $syslog $named
# Required-Stop:     $remote_fs $syslog $named
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: ESP32 server for sleep IoT devices
# Description:       Servidor para conexiones de dispositivos IoT para evaluacion del sueno.
### END INIT INFO

import socket
import time
import psycopg2, psycopg2.extras
import multiprocessing as mp #Process, Manager, Value

#manager data,flag_process_save,pop_index

flag_delay = mp.Value('i',0)
flag_process_save = mp.Value('i',0)
man = mp.Manager()
comming_data = man.list()
rem_data = man.list()

def data_processing(data):
	mac_addr = ''
	data_ = ''
	processed_data = []
	remain_data = []
	#print 'data_processing --> data: ',data
	for i in range(len(data)):
		#print 'data_processing--> len_data: ',len(data[i])
		data_ += data[i]
		#print 'data_processing --> data_',data_
		flag = 0
		if len(data_)==0:
			continue
		while True:
			try:
				init = data_.index('x')
                		end = data_.index('X')
			except:
				if mac_addr != '':
					processed_data.append([mac_addr,list(row)])
					mac_addr = ''
					row = []
					remain_data.append(data_)
					data_ = ''
				flag = 0
				break
			#print 'data_processing --> end-init: ',end-init
			if end-init==163:
				if flag == 0:
                   			mac_addr = 'mac_'+data_[init+2:init+4]+data_[init+5:init+7]+data_[init+8:init+10]+data_[init+11:init+13]+data_[init+14:init+16]+data_[init+17:init+19]
                        		row = [[]]
                        	
					flag = 1
				else:
					row.append([])
				j = 19
				while j<=157:
					row[-1].append(int(data_[j:j+3],16))
					j+=6
                        	data_ = data_[end+1:]
	#print 'data_processing --> END'
	return processed_data,remain_data

def data_database_saving(processed_data,cursor,db,content):
	if len(processed_data)>0:
		t = time.time()
		for i in range(len(processed_data)):
			mac_addr = processed_data[i][0]
			row_data = processed_data[i][1]
			cursor.execute("CREATE TABLE IF NOT EXISTS "+mac_addr+' '+content)
        		db.commit()
        		strs="INSERT INTO "+mac_addr+" (s0,s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,s14,s15,s16,s17,s18,s19,s20,s21,s22,s23) "
        		args_str = ','.join(cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", x) for x in row_data)
        		cursor.execute(strs+' VALUES '+args_str)
        		db.commit()
		#print 'Time database saving: ',time.time()-t
		# escribe en un archivo:
		#with open(mac_addr+'-'+time.strftime('%y%m%d'), "a") as myfile:
		#	for x2 in row_data:
		#		myfile.write(str(time.time())+', '+str(x2)+'\n') #strs+' VALUES '+args_str)


def delay_s(number):
	while True:
		if flag_delay.value==0:
			time.sleep(number)
			flag_delay.value = 1

def data_processing_saving():
	#db = psycopg2.connect(host="127.0.0.1", database="somno", user="postgres", password="somno2019", port="9001")
	db = psycopg2.connect(host="152.74.29.160", database="somno", user="postgres", password="somno2019", port="9001")
	cursor = db.cursor()

	content = '(Time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,';
	for i in range(0,24):
		if i<23:
			content+='s'+str(i)+' INT,'
		else:
	    		content+='s'+str(i)+' INT)'
	while True:
		if flag_process_save.value:
			for i in range(len(comming_data)):
				rem_data[i]+=comming_data[i]
			#print '2'
			#if len(data):
			#	for i in range(len(comming_data)):
			#		data[i]+=comming_data[i]
			#else:
			#	for i in range(len(comming_data)):
			#		data.append(comming_data[i])
			#print '3'
			#print 'processing saving --> RD: ',rem_data
			pd,rd = data_processing(rem_data);
			for i in range(len(pd)):
				row_data_2 = pd[i][1]
				print 'processed_data: ',row_data_2[0]
				
			#print 'processed_data: ',pd
			#print 'processed_data: ',pd[0][1][0][0]
			#print 'remain_data: ',rd
			rem_data[:] = rd
			#print 'processing saving --> RD: ',rem_data
			#for i in range(len(rd)):
                        #                data[i]=rd[i]
			#print 'data: ',data
                	data_database_saving(pd,cursor,db,content);
			
			flag_process_save.value = 0;
			#print 'end processing and saving'


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

hostname = socket.gethostname()
host_addr = socket.gethostbyname(hostname + ".local")

#s.bind((host_addr, 8092))
s.bind(('192.168.1.103', 8092)) # INGRESAR DIRECCIÓN IP DE SERVIDOR UDEC A ENVIAR INFORMACION

s.settimeout(0.5)

s.listen(0)

clients = []
times = []


Fs = 50
'''
c,a = s.accept()
c.settimeout(0.1)
try:
	d = c.recv(164*10)
except:
	print 'Time out'
c.close()
s.close()
'''
t2 = 0
count = 0
data = []
flag_new_client = 0
saving_process = mp.Process(target=data_processing_saving)
saving_process.start()

delay_process = mp.Process(target=delay_s,args=(1,))
delay_process.start()


while True:
	t_ = time.time()

	flag_delay.value = 0
	try:
		clients.append(s.accept())
		flag_new_client = 1
		print 'Accepted client: ',clients[-1][0],clients[-1][1]
		times.append(time.time())
		clients[-1][0].settimeout(0.1)
		data.append('')
		#rem_data.append('')
		#print 'len comming, data, rem_data: ',len(comming_data),len(data),len(rem_data)
		#print 'OK'
	except KeyboardInterrupt:
		print 'keyboard interrupt'
		if len(clients):
			for i in range(len(clients)):
				print 'Pop client'
				clients[i][0].close()
				print 'Pop client: ',clients.pop(i)
		s.close()
		break
	except:
        
		#print 'No new clients'
		a = 1
	while not flag_delay.value:
		pass
	if flag_new_client:
		rem_data.append('')
		flag_new_client = 0
	#print 'Time passed accepting: ',time.time()-t_

	if len(clients):
		t_ = time.time()
		#print 'Still clients'
		#print count
		#print 'len_clients: ',len(clients)
		#t = time.time()
		idx_pop = []
		for i in range(len(clients)):
			#print 'i: ',i
			try:
				#print 'time between reads: ',time.time()-t2
				#t = time.time()
				d=clients[i][0].recv(164*Fs)
				#164*50
				#print 'type: ',type(d)
				#print 'd: ',d
				#print 'len d: ',len(d)
				#print 'd init: ',d[0:165]
				#print 'd end: ',d[-165:]
				data[i]=d
				#print 'data: ',data[i]
				#print 'read time: ',time.time()-t
				#t2 = time.time()
				#print 'len d: ',len(d)
				#count+=1
				#print 'd: ',d[0:25]
			except KeyboardInterrupt:
				print 'keyboard interrupt'
				if len(clients):
					for c in range(len(clients)):
						print 'Pop client'
						clients[c][0].close()
						print 'Pop client: ',clients.pop(c)
				s.close()
				break
                        except:
                                print 'Timeout...add client index to pop'
				idx_pop.append(i)
                                #clients[i][0].close()
                                #print time.time()-times[i]
                                #times.pop(i)
                                #print clients.pop(i)
				#rem_data.pop(i)
				#data.pop(i)
		if len(idx_pop):
			cnt = 0
			for l in idx_pop:
				print 'Timeout...Pop client'
                        	clients[l-cnt][0].close()
                        	#print time.time()-times[i]
                                #times.pop(i)
                                print 'Pop client: ',clients.pop(l-cnt)
                                rem_data.pop(l-cnt)
                                data.pop(l-cnt)
				cnt+=1
		#print 'read time: ',time.time()-t
		comming_data[:]=data
		#print 'len comming_data: ',len(comming_data)
		#print 'len remain_data: ',len(rem_data)
		#print 'count: ',count
		if len(comming_data): 
			#if len(comming_data[0])>170:
			flag_process_save.value = 1
			#print 'comming_data[0]: ',comming_data[0][:170]
			#print 'len coming data: ',len(comming_data)
			#print 'flag_process_save: ',flag_process_save.value
			#count+=1
			#print 'count: ',count
			#if count>=2:
			#break
		#print 'Time passed reading: ',time.time()-t_
		'''
		if len(data)==2:
			if len(data[0])>1650:
				print 'Data processing'
				t3 = time.time()
                                #print 'final_data: ',data
                                dp = data_processing(data);
                                print 'process data time: ',time.time()-t3
				print dp
				data_database_saving(dp,cursor,db,content)
				for k in range(len(data)):
					clients[k][0].close()
					s.close()
					print 'Finish'
				break;
		'''
#time.sleep(5)
#if len(clients):
#	for c in range(len(clients)):
#        	print 'Pop client'
#                clients[c][0].close()
#                print clients.pop(i)
#s.close()
#time.sleep(5);
saving_process.terminate()
delay_process.terminate()
