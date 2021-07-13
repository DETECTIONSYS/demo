#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <wiringPi.h>
#include <pthread.h>
#include <wiringSerial.h>
#include "MQTTClient.h"
#define ADDRESS     "broker.hivemq.com:1883"
#define CLIENTID    "i3"
#define SUB         "i4"
#define TOPIC       "deepcrash"
#define SUBTOPIC    "auto1"
#define QOS         1
#define TIMEOUT     10000L

char a[30];
volatile MQTTClient_deliveryToken deliveredtoken;
void delivered(void *context, MQTTClient_deliveryToken dt)
	{
		printf("Message with token value %d delivery confirmed\n", dt);
		deliveredtoken = dt;
	}
int msgarrvd(void *context, char *topicName, int topicLen, MQTTClient_message *message)
	{
		while(1)
		{
			int i;
			char* payloadptr;
			printf("Message arrived\n");
			printf("     topic: %s\n", topicName);
			printf("   message: ");
			payloadptr = message->payload;
			printf("%s\n",payloadptr);
			if(strncmp(payloadptr,"drowsy",6)==0)
			{
				digitalWrite(10,HIGH);
				delay(5000);
				digitalWrite(10,LOW);
			}
			for(i=0; i<message->payloadlen; i++)
			{
				putchar(*payloadptr++);
			}
			putchar('\n');
			//    printf("payloadptr=%s\n",payloadptr);
			MQTTClient_freeMessage(&message);
			MQTTClient_free(topicName);
			return 1;
		}
	}
void connlost(void *context, char *cause)
	{
		printf("\nConnection lost\n");
		printf("     cause: %s\n", cause);
	}
void *sub()
	{
		MQTTClient client;
		MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
		int rc;
		int ch;
		MQTTClient_create(&client, ADDRESS, SUB,
		MQTTCLIENT_PERSISTENCE_NONE, NULL);
		conn_opts.keepAliveInterval = 20;
		conn_opts.cleansession = 1;
		MQTTClient_setCallbacks(client, NULL, connlost, msgarrvd, delivered);
		if ((rc = MQTTClient_connect(client, &conn_opts)) != MQTTCLIENT_SUCCESS)
			{
				printf("Failed to connect, return code %d\n", rc);
				exit(EXIT_FAILURE);
			}
		printf("Subscribing to topic %s\nfor client %s using QoS%d\n\n"
			   "Press Q<Enter> to quit\n\n", TOPIC, CLIENTID, QOS);
		MQTTClient_subscribe(client, SUBTOPIC, QOS);
		do
			{
				ch = getchar();
			} 
		while(ch!='Q' && ch != 'q');
		MQTTClient_disconnect(client, 10000);
		MQTTClient_destroy(&client);

	    //    return rc;
	}

int pub()
	{
		MQTTClient client;
		MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
		MQTTClient_message pubmsg = MQTTClient_message_initializer;
		MQTTClient_deliveryToken token;
		int rc;
		MQTTClient_create(&client, ADDRESS, CLIENTID,
			MQTTCLIENT_PERSISTENCE_NONE, NULL);
		conn_opts.keepAliveInterval = 20;
		conn_opts.cleansession = 1;
		MQTTClient_setCallbacks(client, NULL, connlost, msgarrvd, delivered);
		l2:if ((rc = MQTTClient_connect(client, &conn_opts)) != MQTTCLIENT_SUCCESS)
			{
				printf("Failed to connect, return code %d\n", rc);
				goto l2;
			}
		pubmsg.payload = a;
		pubmsg.payloadlen = strlen(a);
	    pubmsg.qos = QOS;
		pubmsg.retained = 0;
		deliveredtoken = 0;
		MQTTClient_publishMessage(client, TOPIC, &pubmsg, &token);
	    printf("Waiting for publication of \n"
				"on topic %s for client with ClientID: %s\n",
				 TOPIC, CLIENTID);
		while(deliveredtoken != token);
		MQTTClient_disconnect(client, 10000);
		MQTTClient_destroy(&client);
		return rc;
	}
int main(int argc, char* argv[])
	{
		int serial_port,i=0;
		char dat;
		pthread_t thread_id1;
		pthread_create(&thread_id1,NULL,&sub,NULL); //Thread creation for subscription
		wiringPiSetup();

		pinMode(10,OUTPUT);//Buzzer
		pinMode(26,INPUT); //vibration Sensor
		while((system("ping -c1 -w1 google.com> /dev/null 2>&1"))!=0);
		printf("success");
		if ((serial_port = serialOpen ("/dev/ttyS0", 115200)) < 0)      /* open serial port */
			{
				fprintf (stderr, "Unable to open serial device: %s\n", strerror (errno)) ;
				return 1 ;
			}

		if (wiringPiSetup () == -1)
			{
				fprintf (stdout, "Unable to start wiringPi: %s\n", strerror (errno)) ;
				return 1 ;
			}
		while(1)
			{
				if(serialDataAvail (serial_port) )
					{
						while(serialGetchar(serial_port)!='S');
						while(1)
							{
								dat=serialGetchar(serial_port);
								if(dat=='A')
									{
										a[i]='\0';
										break;
									}
								else
									{
										a[i]=dat;
										i++;
									}
							}
						fflush (stdout) ;
					}
				if(a[0]=='1')
					{
					  digitalWrite(6,HIGH);
					  delay(5000);
					  digitalWrite(6,LOW);
					}
				if(digitalRead(26)==1)
					{
						pub();
					}
				i=0;
				a[0]='\0';
			}
	}
