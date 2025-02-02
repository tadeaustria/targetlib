
from PIL import Image, ImageDraw, ImageFont
import io, math, numpy as np
from operator import attrgetter
# from numpy.core.numeric import NaN
from pathlib import Path

def toPixel(mms, factor):
    # return (int(mms[0]*factor), int(mms[1]*factor))
    return tuple(int(m*factor) for m in mms)

def drawTarget(draw:ImageDraw, midx, midy, factor, backgroundColor, targetColor, space = 250):
    #Draw outer rings black
    for i in range(9, 6, -1):
        draw.ellipse([toPixel((midx-i*space-25, midy-i*space-25), factor), toPixel((midx+i*space+25, midy+i*space+25), factor)], outline=targetColor)

    #Draw 4-Point ring with black fill
    draw.ellipse([toPixel((midx-6*space-25, midy-6*space-25), factor), toPixel((midx+6*space+25, midy+6*space+25), factor)], outline=targetColor, fill=targetColor)

    #Draw inner rings white
    for i in range(5, 0, -1):
        draw.ellipse([toPixel((midx-i*space-25, midy-i*space-25), factor), toPixel((midx+i*space+25, midy+i*space+25), factor)], outline=backgroundColor)
    
    #Draw 10-Point ring
    draw.ellipse([toPixel((midx-25, midy-25), factor), toPixel((midx+25, midy+25), factor)], outline=backgroundColor, fill=backgroundColor)
        
def drawText(draw:ImageDraw, midx, midy, factor, backgroundColor, targetColor, space = 250):
    font = ImageFont.truetype("arial.ttf", size=48)
    
    #Mid to right text
    for i in range(9, 6, -1):
        draw.text(toPixel((midx+(i-0.4)*space, midy), factor), str(10-i), fill=targetColor, anchor="mm", font=font)
    for i in range(6, 1, -1):
        draw.text(toPixel((midx+(i-0.4)*space, midy), factor), str(10-i), fill=backgroundColor, anchor="mm", font=font)

    #Mid to left text
    for i in range(9, 6, -1):
        draw.text(toPixel((midx-(i-0.4)*space, midy), factor), str(10-i), fill=targetColor, anchor="mm", font=font)
    for i in range(6, 1, -1):
        draw.text(toPixel((midx-(i-0.4)*space, midy), factor), str(10-i), fill=backgroundColor, anchor="mm", font=font)
        
    #Mid to bottom text
    for i in range(9, 6, -1):
        draw.text(toPixel((midx, midy+(i-0.4)*space), factor), str(10-i), fill=targetColor, anchor="mm", font=font)
    for i in range(6, 1, -1):
        draw.text(toPixel((midx, midy+(i-0.4)*space), factor), str(10-i), fill=backgroundColor, anchor="mm", font=font)
        
    #Mid to top text
    for i in range(9, 6, -1):
        draw.text(toPixel((midx, midy-(i-0.4)*space), factor), str(10-i), fill=targetColor, anchor="mm", font=font)
    for i in range(6, 1, -1):
        draw.text(toPixel((midx, midy-(i-0.4)*space), factor), str(10-i), fill=backgroundColor, anchor="mm", font=font)

def drawLogo(image:Image, factor):
    ImageWidth= 750
    ImageBorder = 50
    logo = Image.open(Path(__file__).with_name('schuetzenlogo.png'))
    logo.thumbnail(toPixel((ImageWidth, ImageWidth),factor), Image.LANCZOS)
    # image.paste(thumb, toPixel((image.height//factor - ImageWidth - ImageBorder, ImageBorder, image.height//factor - ImageBorder, ImageHeight + ImageBorder), factor), logo)
    image.paste(logo, toPixel((image.width//factor - ImageWidth - ImageBorder, ImageBorder), factor), logo)

def getAngleBetweenVectors(vec1, vec2):
    unit_vector_1 = vec1 / np.linalg.norm(vec1)
    unit_vector_2 = vec2 / np.linalg.norm(vec2)
    dot_product = np.dot(unit_vector_1, unit_vector_2)
    if np.cross(unit_vector_1, unit_vector_2) < 0:
        return np.arccos(dot_product)
    else:
        return 2*math.pi - np.arccos(dot_product)

#Use a normal calculated shot
class Shot():
    def __init__(self, xcoord, ycoord):
        self.xcoord = xcoord
        self.ycoord = ycoord
        self.teiler = math.sqrt(xcoord**2 + ycoord**2)

    def getColor(self):
        if self.teiler <= 251.0:
            return '#ff0000bb'
        elif self.teiler <= 500.0:
            return '#ffff00bb'
        else:
            return '#ffffffbb'

    def getValue(self, tenth=False):
        value = round(self.teiler / (-250.4829786 ) + 10.97176989,1)  #Estimated linear function but is not equal reality
        if tenth:
            return max(min(value, 10.9),0.0)
        else:
            return max(min(math.floor(value), 10), 0)

#Used to set all values separately
class Shot2(Shot):
    def __init__(self, xcoord, ycoord, teiler, value):
        super().__init__(xcoord, ycoord)
        self.teiler = teiler
        self.value = value

    def getColor(self):
        if self.value >= 10.0:
            return '#ff0000bb'
        elif self.value >= 9.0:
            return '#ffff00bb'
        else:
            return '#ffffffbb'

    def getValue(self, tenth=False):
        if tenth:
            return max(min(self.value, 10.9),0.0)
        else:
            return max(min(math.floor(self.value), 10), 0)


class Target():
    def __init__(self, width, height, noOfShots = 0, type='b', headline = '', transparent = True):

        self.tenthMM2PixelFactor = width / 5000 #50.00 mm
        self.midx = width  // 2 / self.tenthMM2PixelFactor
        self.midy = height // 2 / self.tenthMM2PixelFactor
        self.SHOTSIZE = 225
        self.shots = []
        self.cellsize = 720            #75mm per square cell
        self.headlinesize = 400
        self.margin = 250

        margins = toPixel((self.cellsize, self.margin, self.headlinesize), self.tenthMM2PixelFactor)

        totalHeight = height
        if type == 'r':
            totalHeight += 1 * margins[0] + margins[1]
        elif noOfShots > 0:
            totalHeight += ((noOfShots-1)//5+2) * margins[0] + margins[1]

        self.bottom_target = 2 * self.midy
        if headline:
            totalHeight += margins[2] + margins[1]
            self.bottom_target += self.headlinesize + self.margin
            self.midy += self.headlinesize + self.margin

        self.backgroundColor = '#f6dda5'
        self.targetColor = '#014c2d' if type == 'g' else '#712227' if type == 'r' else 'black'

        self.canvas = Image.new('RGB', (width, totalHeight), color=self.backgroundColor)
        # noise = np.asarray(Image.effect_noise((width, height), 10))

        # self.canvas = Image.fromarray(np.asarray(self.canvas)+noise)
        # self.canvas.alpha_composite(self.test)
        # self.test.show()
        if transparent:
            self.draw = ImageDraw.Draw(self.canvas, 'RGBA')
        else:
            self.draw = ImageDraw.Draw(self.canvas, 'RGB')

        # draw headline text
        if headline:
            self.draw.text((margins[1], margins[1]), headline, fill='black', anchor="lt", font=ImageFont.truetype("arial.ttf", size=168))

        # draw all the target rings
        drawTarget(self.draw, self.midx, self.midy, self.tenthMM2PixelFactor, self.backgroundColor, self.targetColor)
        # draw target ring description numbers
        drawText(self.draw, self.midx, self.midy, self.tenthMM2PixelFactor, self.backgroundColor, self.targetColor)
        # draw logo
        drawLogo(self.canvas, self.tenthMM2PixelFactor)
  
    def getPicture(self, format='PNG'):
        temp = io.BytesIO()
        self.canvas.save(temp, format=format)
        return temp.getvalue()
        
    def drawShot(self, shot):
        self.shots.append(shot)
        self.draw.ellipse([toPixel((self.midx+shot.xcoord-self.SHOTSIZE, self.midy+shot.ycoord-self.SHOTSIZE), self.tenthMM2PixelFactor), toPixel((self.midx+shot.xcoord+self.SHOTSIZE, self.midy+shot.ycoord+self.SHOTSIZE), self.tenthMM2PixelFactor)], outline='black', fill=shot.getColor())

    def drawShotByCoordinates(self, x, y):
        self.drawShot(Shot(x, y))

    def drawShotByAllInfo(self, x, y, teiler, value):
        self.drawShot(Shot2(x, y, teiler, value))

    def drawCenter(self):
        if not self.shots:
            return
        if self.isTeilerOnly():
            return
        x = 0
        y = 0
        crosssize = 50 #2mm cross
        for shot in self.shots:
            x += shot.xcoord
            y += shot.ycoord
        x = x // len(self.shots)
        y = y // len(self.shots)
        self.draw.line([toPixel((self.midx+x-crosssize, self.midy+y), self.tenthMM2PixelFactor), toPixel((self.midx+x+crosssize, self.midy+y), self.tenthMM2PixelFactor)], fill='#3333FF', width=2)
        self.draw.line([toPixel((self.midx+x, self.midy+y-crosssize), self.tenthMM2PixelFactor), toPixel((self.midx+x, self.midy+y+crosssize), self.tenthMM2PixelFactor)], fill='#3333FF', width=2)

    def drawArrow(self,x,y,shot):
        base = np.array([1,0])
        shotdirection = np.array([-shot.xcoord, -shot.ycoord]) #Negative because we want the arrow to the middle not away from it
        angle = getAngleBetweenVectors(base, shotdirection)
        if math.isnan(angle):
            return
        rotationMatrix = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])

        #arror design points at right direction
        arraySize=60
        end=np.array([-arraySize,0]).dot(rotationMatrix)
        point=np.array([arraySize,0]).dot(rotationMatrix)
        rightwing=np.array([0,arraySize]).dot(rotationMatrix)
        leftwing=np.array([0,-arraySize]).dot(rotationMatrix)

        self.draw.line([toPixel((x+end[0], y+end[1]), self.tenthMM2PixelFactor), toPixel((x+point[0], y+point[1]), self.tenthMM2PixelFactor)], fill='black', width=2)
        self.draw.line([toPixel((x+point[0], y+point[1]), self.tenthMM2PixelFactor), toPixel((x+rightwing[0], y+rightwing[1]), self.tenthMM2PixelFactor)], fill='black', width=2)
        self.draw.line([toPixel((x+point[0], y+point[1]), self.tenthMM2PixelFactor), toPixel((x+leftwing[0], y+leftwing[1]), self.tenthMM2PixelFactor)], fill='black', width=2)

    def isTeilerOnly(self):
        return self.targetColor == '#712227' #When red, only Teiler should be printed

    def drawTable(self, tenth=False):
        margin = self.midx - 2250 #225mm is half of the ring and the table should be 45mm width
        cellsize = self.cellsize
        fontmargin = 40
        font = ImageFont.truetype("arial.ttf", size=142)

        if self.isTeilerOnly():
            specialColumn = 1200
            lines = 0
            #draw sum special cell
            self.draw.rectangle([toPixel((margin+cellsize*4, self.bottom_target), self.tenthMM2PixelFactor), toPixel((margin + cellsize * 4 + specialColumn, self.bottom_target+(lines+1)*cellsize), self.tenthMM2PixelFactor)], outline='black', width=6)
            #self.draw.line([toPixel((margin+cellsize*5, self.bottom_target+lines*cellsize), self.tenthMM2PixelFactor), toPixel((margin + cellsize * 5 + specialColumn, self.bottom_target+lines*cellsize), self.tenthMM2PixelFactor)], fill='black', width=6)
            #Sum Cell with extra text 
            #find smallest Teiler
            teiler = round(min(self.shots, key=attrgetter('teiler')).teiler, 1)
            self.draw.text(toPixel((margin+4*cellsize - fontmargin, self.bottom_target+cellsize//2 + cellsize * lines), self.tenthMM2PixelFactor), "Teiler:", fill='black', anchor="rm", font=font)    
            self.draw.text(toPixel((margin+4*cellsize + specialColumn - fontmargin, self.bottom_target+cellsize//2 + cellsize * lines), self.tenthMM2PixelFactor), str(teiler), fill='black', anchor="rm", font=font)
        else:
            specialColumn = 900
            lines = ((len(self.shots) - 1) // 5) + 1
            #draw table rows
            for i in range(0, lines):
                self.draw.rectangle([toPixel((margin, self.bottom_target + i*cellsize), self.tenthMM2PixelFactor), toPixel((margin + cellsize * 5 + specialColumn, self.bottom_target+cellsize + i*cellsize), self.tenthMM2PixelFactor)], outline='black')
            #draw column separators
            for i in range(1, 5):
                x = margin + i * cellsize
                self.draw.line([toPixel((x, self.bottom_target), self.tenthMM2PixelFactor), toPixel((x, self.bottom_target + lines*cellsize), self.tenthMM2PixelFactor)], fill='black')
            #draw sum special cell
            self.draw.rectangle([toPixel((margin+cellsize*5, self.bottom_target), self.tenthMM2PixelFactor), toPixel((margin + cellsize * 5 + specialColumn, self.bottom_target+(lines+1)*cellsize), self.tenthMM2PixelFactor)], outline='black', width=6)
            self.draw.line([toPixel((margin+cellsize*5, self.bottom_target+lines*cellsize), self.tenthMM2PixelFactor), toPixel((margin + cellsize * 5 + specialColumn, self.bottom_target+lines*cellsize), self.tenthMM2PixelFactor)], fill='black', width=6)

            #draw text
            if tenth:
                partSum = 0.0
                sum = 0.0
            else:
                partSum = 0
                sum = 0
            i = 0
            for shot in self.shots:
                value = shot.getValue(tenth)
                self.draw.text(toPixel((margin+(i%5+1)*cellsize - fontmargin, self.bottom_target+cellsize//2 + cellsize * (i//5)), self.tenthMM2PixelFactor), str(value), fill='black', anchor="rm", font=font)
                self.drawArrow(margin+(i%5+1)*cellsize - fontmargin*2, self.bottom_target+fontmargin*2 + cellsize * (i//5), shot)
                partSum += value
                sum += value
                #Partial Sum Cell
                if (i+1)%5 == 0:
                    partSum = round(partSum, 1)
                    self.draw.text(toPixel((margin+5*cellsize + specialColumn - fontmargin, self.bottom_target+cellsize//2 + cellsize * (i//5)), self.tenthMM2PixelFactor), str(partSum), fill='black', anchor="rm", font=font)
                    partSum = 0.0 if tenth else 0
                i += 1
            #Sum Cell with extra text
            sum = round(sum, 1)
            self.draw.text(toPixel((margin+5*cellsize - fontmargin, self.bottom_target+cellsize//2 + cellsize * lines), self.tenthMM2PixelFactor), "Summe:", fill='black', anchor="rm", font=font)    
            self.draw.text(toPixel((margin+5*cellsize + specialColumn - fontmargin, self.bottom_target+cellsize//2 + cellsize * lines), self.tenthMM2PixelFactor), str(sum), fill='black', anchor="rm", font=font)
