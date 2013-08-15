import math

class QubAngleConstraint :
    def __init__(self,angle) :
        self.__xPixelSize = 0
        self.__yPixelSize = 0
        self.setAngle(angle)

    def setXPixelSize(self,size) :
        try:
            self.__xPixelSize = abs(size)
        except:
            self.__xPixelSize = 0

    def setYPixelSize(self,size) :
        try:
            self.__yPixelSize = abs(size)
        except:
            self.__yPixelSize = 0

    def setAngle(self,angle) :
        self.__contraintAngle = angle * math.pi / 180
        while(self.__contraintAngle > math.pi) :
            self.__contraintAngle -= math.pi * 2
        while(self.__contraintAngle < -math.pi) :
            self.__contraintAngle += math.pi * 2

    def calc(self,x1,y1,x2,y2) :
        if(abs(self.__contraintAngle) == math.pi / 2  or
           abs(self.__contraintAngle) == 3 * math.pi / 2) :
            x2 = x1                 # 90 or 270 deg
        elif(abs(self.__contraintAngle) == math.pi or not self.__contraintAngle) :
            y2 = y1
        else:
            if((math.pi / 4 <= abs(self.__contraintAngle)) or
               (abs(self.__contraintAngle) >= 3 * math.pi / 4)) :
                Y = y2 - y1
                if self.__yPixelSize :
                    Y *= self.__yPixelSize
                Y = Y ** 2
                X = math.sqrt((Y * math.cos(self.__contraintAngle) ** 2) /
                              (1 - math.cos(self.__contraintAngle) ** 2))
                if self.__xPixelSize:
                    X /= self.__xPixelSize
                if self.__contraintAngle > math.pi / 2 :
                    X = -X
                if y2 - y1 < 0 :
                    X = -X
                x2 = X + x1
            else:
                X = x2 - x1
                if self.__xPixelSize :
                    X *= self.__xPixelSize
                X = X ** 2
                Y = math.sqrt((X / (math.cos(self.__contraintAngle) ** 2)) - X)
                if self.__yPixelSize :
                    Y /= self.__yPixelSize
                if x2 - x1 < 0:
                    Y = -Y
                y2 = Y + y1
        return (x1,y1,x2,y2)
