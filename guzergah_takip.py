#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Şerit Takip Etme
"""

import cv2
import numpy as np
import rospy
from sensor_msgs.msg import Image, LaserScan
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge

class SeritTakip():
        
        
    def __init__(self):
        rospy.init_node("serit_takip")
        self.bridge = CvBridge()
        rospy.Subscriber("camera/rgb/image_raw",Image,self.kameraCallback)
        def lidar_data(veri):

            bolgeler = {
                
                'on1':  min(min(veri.ranges[0:9]), 1),
                'on2': min(min(veri.ranges[349:359]), 1),
                'on_sol':  min(min(veri.ranges[10:49]), 1),
                'sol':  min(min(veri.ranges[50:89]), 1),
                'arka':   min(min(veri.ranges[90:268]), 1),
                'sag':   min(min(veri.ranges[269:308]), 1),
                'on_sag':   min(min(veri.ranges[309:348]), 1),
            }
            global bolge
            bolge = {}
            bolge = bolgeler
            print(bolgeler)
        rospy.Subscriber('/scan', LaserScan, lidar_data)
        self.pub = rospy.Publisher("cmd_vel",Twist,queue_size = 10)
        self.hiz_mesaji = Twist()
        rospy.spin()
        


        
    def kameraCallback(self,mesaj):
        global hiz
        global donus
        img = self.bridge.imgmsg_to_cv2(mesaj,"bgr8")
        hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        alt_sari = np.array([30,25,25])
        ust_sari = np.array([78,255,255])
        maske = cv2.inRange(hsv,alt_sari,ust_sari)
        sonuc = cv2.bitwise_and(img,img,mask=maske)
        h,w,d = img.shape
        cv2.circle(img,(int(w/2),int(h/2)),5,(0,0,255),-1)
        M = cv2.moments(maske)
        if (M['m00'] > 0) and (bolge['on1'] and bolge['on2'] > 0.8) :
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            cv2.circle(img,(cx,cy),5,(255,0,0),-1)
            sapma = cx - w/2
            print(sapma)
            hiz = 0.3
            donus = -sapma/100
            self.hiz_mesaji.linear.x = 0.3
            self.hiz_mesaji.angular.z = -sapma/100
            self.pub.publish(self.hiz_mesaji)
            
            if bolge['on_sag'] - bolge['on_sol'] > 1.0:    
                
                print ('DONUS:SAG')    
                hiz = 0.2
                donus = -0.4
                                     
            elif bolge['on_sol'] - bolge['on_sag'] > 1.0:    
                
                print ('DONUS:SOL')
                hiz = 0.2
                donus = 0.4
            
            self.hiz_mesaji.linear.x = hiz
            self.hiz_mesaji.angular.z = donus
            self.pub.publish(self.hiz_mesaji)
            
            #else:
            #    print('DONUS:0')
            #    hiz = 0.3
            #    donus = -sapma/100
        else:
            print('DUR')
            hiz = 0.0
            donus = 0.0
            
        self.hiz_mesaji.linear.x = hiz
        self.hiz_mesaji.angular.z = donus
        self.pub.publish(self.hiz_mesaji)

        cv2.imshow("Orjinal",img)
        cv2.imshow("Maske",maske)
        cv2.imshow("Sonuc",sonuc)
        cv2.waitKey(1)
        
SeritTakip()
