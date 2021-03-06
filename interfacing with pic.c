#include<stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <GPS_Lib.c>  // include GPS library source file (GPS_Lib.c)

void command(int a);
void data(char b);
void string(char c[]);
void main()
 {
   int16 value,p;
   char b[20]="AlcoholLevel=";
   char c[20]="Alert";
   char str[20];
   char lat[20];
   char long[20];
   int a,i ;
   setup_adc_ports(ALL_ANALOG);
   setup_adc(ADC_CLOCK_INTERNAL);
   setup_spi(SPI_SS_DISABLED);
   setup_timer_0(RTCC_INTERNAL|RTCC_DIV_1);
   setup_timer_1(T1_DISABLED);
   setup_timer_2(T2_DISABLED,0,1);
   setup_comparator(NC_NC_NC_NC);
   setup_vref(FALSE);
   set_tris_A(0xff);
   set_tris_C(0x00);
   set_tris_B(0x00);
   command(0x38);
   command(0x01);
   command(0x06);
   command(0x80);
   command(0xc0);
   command(0x0e);
   delay_ms(10);
   while(1)
      {
       set_adc_channel(0);
       delay_ms(500);
       value=read_adc();
       sprintf(str,"%ld",value);
       output_b(value);
       data(value);
       if(value<=500)
          {
          output_b(str);
          string(str);
          delay_ms(1000);
          command(0x01);
          p=1;
          }
       else
          {
           printf("\nstring=%s\n",str);
           output_b(str);
           string(str);
           delay_ms(1000);
           command(0x01);
          delay_ms(1000);
          string(c);
          delay_ms(1000);
          command(0x01);
          p=0;
          }
        if(GPSRead()) 
            {

              printf("S");
              printf("%d",p);
              printf(",");
            // Latitude
              printf("Latitude  :  %.6f\r\n", Latitude());
            printf(",");
            // Longitude
              printf("Longitude :  %.6f\r\n", Longitude());
            printf(",");
            printf("A");
            lat=Latitude();
              string(lat);
              delay_ms(2000);
              command(0x01);
            long=longitude();
              string(long);
              delay_ms(2000);
              command(0x01);
             }
        }

void command(int a)
    {
    output_b(a);
    output_bit(PIN_C0,0);
    output_bit(PIN_C1,0);
    delay_ms(10);
    output_bit(PIN_C2,0);
    delay_ms(10);
    output_bit(PIN_C2,1);
    delay_ms(10);
    }

void data(char b)
    {
    output_b(b);
    output_bit(PIN_C0,1);
    output_bit(PIN_C1,0);
    delay_ms(10);
    output_bit(PIN_C2,0);
    delay_ms(10);
    output_bit(PIN_C2,1);
    delay_ms(10);
    }

void string(char c[])
    {
    int i=0;
    while(c[i]!='\0')
        {
        data(c[i]);
        i++;
        }
    }
