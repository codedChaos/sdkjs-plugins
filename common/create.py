#!/usr/bin/env python
import shutil
import uuid
import json
import os
import re
import base64

def readFile(path):
  if os.path.exists(path):
    with open(path, "r") as file:
      filedata = file.read()
    return filedata
  return ''

def writeFile(path, content):
  if (os.path.isfile(path)):
    os.remove(path)

  with open(path, "w") as file:
    file.write(content)
  return

class EditorApi(object):
  def __init__(self):
    self.records = []
    self.init = False
    self.folder = "word"
    self.type = "CDE"
    self.numfile = 0
    self.files = []
    return

  def initFiles(self, type, files):
    self.folder = type
    if "word" == self.folder:
      self.type = "CDE"
    elif "slide" == self.folder:
      self.type = "CPE"
    else:
      self.type = "CSE"
    self.files = files
    return

  def getAlias(self, description):
    value = re.search(r'@alias.+', description)
    if (None != value):
      return value.group().lstrip('@alias ')
    return ''

  def check_record(self, recordData):
    rec = recordData
    rec = rec.replace("\n\t", "")
    rec = rec.replace('\n\n    ', '\n\n')
    indexEndDecoration = rec.find("*/")
    decoration = ""
    codeCorrect = ""
    alias = self.getAlias(rec[0:indexEndDecoration + 2])
    if ('' != alias):
      alias = '* @typedef {"' + alias + '"} ' + alias + '\n\n'
      decoration = "/**" + rec[0:indexEndDecoration] + alias + ' */'
      decoration = decoration.replace("@return ", "@returns ")
      decoration = decoration.replace("@returns {?", "@returns {")

    if ('' != decoration):
      self.append_record(decoration, codeCorrect)
    return

  def append_record(self, decoration, code, init=False):
    if init:
      if not self.init:
        self.init = True
        self.records.append(decoration + "\n\n" + code + "\n\n")
      return
    # check on private
    if -1 != code.find(".prototype.private_"):
      return
    # add records only for current editor
    index_type_editors = decoration.find("@typeofeditors")
    if -1 != index_type_editors:
      index_type_editors_end = decoration.find("]", index_type_editors)
      if -1 != index_type_editors_end:
        editors_support = decoration[index_type_editors:index_type_editors_end]
        if -1 == editors_support.find(self.type):
          return
    # optimizations for first file
    if 0 == self.numfile:
      self.records.append(decoration + "\n\n" + code + "\n\n")
      return
    # check override js classes
    if 0 == code.find("function "):
      index_end_name = code.find("(")
      function_name = code[9:index_end_name].strip(" ")
      for rec in range(len(self.records)):
        if -1 != self.records[rec].find("function " + function_name + "("):
          self.records[rec] = ""
        elif -1 != self.records[rec].find("function " + function_name + " ("):
          self.records[rec] = ""
        elif -1 != self.records[rec].find("\n\n" + function_name + ".prototype."):
          self.records[rec] = ""

    self.records.append(decoration + "\n\n" + code + "\n\n")
    return

  def generate(self):
    for file in self.files:
      file_content = readFile(file)
      arrRecords = file_content.split("/**")
      arrRecords = arrRecords[1:-1]
      for record in arrRecords:
        self.check_record(record)
      self.numfile += 1
    correctContent = ''.join(self.records)
    correctContent += "\n\n"
    writeFile(old_cur + "/lib/api.js", correctContent)
    return

def convert_to_interface(arrFiles, sEditorType):
  editor = EditorApi()
  editor.initFiles(sEditorType, arrFiles)
  editor.generate()
  return

def create_imgs(oImgs):
  if True == os.path.isdir(old_cur + '/resources'):
    shutil.rmtree(old_cur + '/resources', ignore_errors=True)
    os.mkdir(old_cur + '/resources')
  for sType in oImgs:
    os.mkdir(old_cur + '/resources/' + sType)
    for sImgSize in oImgs[sType]:
      with open(old_cur + '/resources/' + sType + '/' + sImgSize + ".png", "wb") as fh:
        fh.write(base64.decodebytes(oImgs[sType][sImgSize]))

imgs = {
  "light" : {
    "icon" : b'iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAYAAAByDd+UAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAIbSURBVHgB3ZW/TsMwEMaduAMbGZkqaF8ANphI/0kwASMTXZlon6DhDWBkQrwBjKitEjY2eICqzQhTOzK0Ct8hBzmukziUBT7Jiu2c75dz7mzG/rssE6Nms+nicYT2MBgMghQbD4+eNOXB9rIQEE46wokTRVE4HA63VoGRSiwd5ilOglVhJNvQCbNt+1rvIh8m/OmBOhg56vf7ryxHGbCeFpgGm8/nadFlSrtTWS8JhmaVSqWpvC05gCx/iQgjFQbQnbSolwKV58gmoqbAvm143BmPx0+VSoW6LhM/fzQazTDnYLwrzFyMLdgGIooOkukNJfMq1umUSKSlOmy1WvtIkCd5Do792CHV42Kx2EH0cY2SumjrLBntEkwL1Ml1XQcAHzAHsBr6bQnGLMvq4CONEssIKKCb9FRh0D2iOGGGsk0NgyAIVRhtL0qmywqImxqqaS7+JW2vh0TajhPpV4CampoBticivmBK9q4E1BUwojvlnK+heytNG0F5URjk4Zq6geNQqVEjKC8Kk+sKjh8BoDty2xTKC8Ao/c9V23K5HOC0OUB3wwTKTWAiIw/DMPxQ7WkO0EcU/zGakwdNFD6OtTac32pgNapDliE6GJC1L+g6yqsuduYqHiQKH45V45kJjEQ2iLBGa1jyg6fyOLGlk8nkWboxvtLf9/1nZihs31u1Wn1H91hMUUbnn7H1er3daDTO2A+16vq/rU++/CrZkTCylwAAAABJRU5ErkJggg==',
    "icon@1.5x" : b'iVBORw0KGgoAAAANSUhEUgAAACoAAAAqCAYAAADFw8lbAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAOUSURBVHgB7Zg7U9wwFIXvPpjZkjIVeIE+pEuqeHnNltCRCvgHpEyFqTKpQqqUIb8goQozPLx06dh0aQCnI92WzPDKOWAWr2zZkpwiGTgzHtmyrvRZupKuLPKoB6qKlNDMzIyPhNfT3d3dBQu7AMmakh2gjnWdTV0c4SqVytL19bXHPNyvWtgHYglJWYEmGwFkP//8/HzL1j6hQkiqKobSNEJ1O51OJG72RpCUEWgOJId9U8xkBRm32VchaB4kZTrsikwgB9rMBS2CZIMmw67KFpKq2hokZOxfmrqt2qzaGsRyhoy1psIWtZkCNYVEudW5ubklMVegPPdhdStC8mFgZ7KATJZbR16QYyO+7w/Dl3uwW5M0sLadZEYt+TA2NvZSbrfEPEjuQm+THLCrHB8fd7KM+FHVavUby9Ae6Y2NWECmQNHYgaaivrHnec+xdraV936z2fROTk62VEi573nfAFbr+5lBiTJEKWO830SS8k9sq5t7e3sreWWurq68/f39X2IpbfQUw2auefS5er0e4nZSedW9uLho4d1GFiS0gfpei4OcwzzAerVaLYQbeHIPuQDIQLIhu4B8Jo4yDkpUcUe6vLxsYbgjPsaQXyTbJSL2tJRQqcCZYs8i6Wlc4QaSH+Sy1SZlHTirajQaApDDuyBaUY+QTKWknIeearfbHkBCDSR7cwU9PT80NHTIslJCzkNfBCm3y9sBrvCmoUolwuRrbW9vR+IgJ1ATSPTkZ0ygQ9wP9xsrAWs99AaQXwnJMklIijbMd3EDK9DZ2dlJ9lIOJNfSlbOzM+5AmQVoyzpYl1jIeOhZMRpJ9VICYGAZytgQVPXwrrWzs9MVA5ke7nwbSIr3iJr4U0K3NA2zzunp6XkxUK2owNTU1DK+nDtOQ1cGQC0EGj/VfERjp+Pj479xq4NpoO5FRF4RIq8f4gpKSEB8yivDvyQYPu1JFLDdohgUdcwXwWpBGSCjgo+SL4aA7wrK5MW5fRE2LwCvaSADGYzis8SQ7Y0YKoZtSkY8kJD2tJACxexeRvJe8tW1+Xt3p5GRkQ5ciaeDJznF/ImJiejo6GjADVKzHrNX8lQmZOMBj+FgHBpqlcWQ6lE4tNb5E8vQqTgqiqLe6OjoFn0SV9ZyF+A480GKQCmN8zNke1E2rryDxfAyYFmUwWVPe7jTznoVFr35KgzD7/KXlLHGlvv7wrUUu4fNH5F/qv5H/ff6A2dFIEM3+cz2AAAAAElFTkSuQmCC',
    "icon@2x" : b'iVBORw0KGgoAAAANSUhEUgAAADgAAAA4CAYAAACohjseAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAATFSURBVHgB7Vm7UiNHFL1CUOVQoSNKBoqYzezIIx5VCtlsHS2EjtB+AeMvWBzZmUW4ERAZiofYbDNw5oDHOFtHljMHgHyOdmZLOzvdfXumZyOdKkmjmds9ffrevo9ukSmmmGKKGtGQGrG+vh7h5/uzs7OfxBNoG+Nn1/A41vY5K4ERRVFrdna2h8sdfFqj0WhLPBGKHBFMg3livAdyyfn5+Tc+/YQkR1TWYGqGHFBU8DgWv75iCUiOqETQNiBq7/Hx8a0E6EtKkiNmpCQcAyIugUT0qEQuHc9nKEVQQU6gvVIznoMPucLxeBPUkIN59j21V4iq5Agvghpy405nZvryBaAZj5qglhwQn56eqp1LWagnWxTwIVfW21neKxXG4yboSw4Bvy3hsJsn6UOOsBL0JUd5ZDP3ppl39WG4T5Kj7GMZT1x0s2kQLkVuQj5aWlpq3d7enijaj9O8i4uLk4WFhfFf8Ydxadg0OBJlx0WT8fT01FtbW/vN1UGq9X/4mw4yFj9Y171Rg3d3d28dMzruuNvttkHmoEig0WisoI/N+fn5N0mS/Jd/DlJ9+ZCcj98D2Qb79NCk06k1bQ8tJD92fHNzM4QMq4dvDd18jbjYXV5ePqHsuDOYJEz4V1y+zMn6kFR5bFW5hJmm+cW2jiEzsAxoiOxmG6XTYVpWUXbFIEvzbmNN/iUB0NQITWjy0jRrMMMjmOQLfFq5R0Pc66DdJc0Z/38XCzlgDxPxRgIh6JYFY2Cz2RyAUJv/WTLBPJ8js7kmOSTgA9xrW7q4xkQ8k4AoXS4VgQk2CckHk2Q92NGSo/zDw8NzCYxaNp1Y5WOwCQlvbGzQHA9c5DgZISqQPGrdVSM5DJ4OpWURG69RalpqQFATncTq6uqWghy116uLHFELQZLDWmQW03KIxvCY+1yjMOue1IDgBJlypeRc+BhPsV6ZCb0umaRboYqDWngk6Icg9yMvkK/uYQ1upvfHmQzi7qUEQjANasml4WA7awNyOzmRXU2SrkUQL5pqYcclNxkO0jX32iLbh+wryA6lAioTTCuClwrRITT3LIuNIHClaHONNp0qJEubKJNmkOMgNeSoke0skEMzkeiwMjc3d5XmsKVQysloKoJJwHx7cCr72f/7+/t3jhJrEjyh2kS5dZSVWz7wNlFl0jwJY93mKLE+ASYpQSLfOT4+TsQDXibqSw6D6tuK0jS5VmUxfCff7Wuuag2W0Jyq9MmXWAp45a4qDdLrYbavtOR8Sh86HoYOXGrXF9fkAKFpUyOs2fiNNElzhjKlTyrrUwu2oMUDkHR6cKsXZdLMjnD5lSiBPLSD/ZQ/xRNIz5J2u/0v3tfVtmGK50rtbBu/PXTwi3iA4QBr40hKIg0fvIw8mnGTOcEm8x9FDwtNFGtuSyxplAE8VfpZKiL1uvs+bbAkjM9mfBsYsBfyVAl9bYkyfEhaU5oeFhLEGuqLfgudW4mvJDCYg9JhOcScm79GL6o5J6hrJ4xggk1vbCGp2tkuu3U/GQ7eS03AecYQDoSnxS/kU0+uPmh1JtsGkpzd7+rY5it4//vFxcW/cZkFdq9TZN+t+4hf0N4Pg8HgnXwh4P3XiJE8qziEQ6nsqY1g4NdkD1NMMcUUGf4Hxtvg3yDPFOgAAAAASUVORK5CYII='
  },
  "dark" : {
    "icon" : b'iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAYAAAByDd+UAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAGWSURBVHgB7ZbRccIwDIblHI9lALpGF+gAdIBc380AZQ0GIAO07z3eyQBlAQagA2SAVAoKNapsy2lfesd/p/ORyPosW3IAuAnV9/0D2guNCR+P9hGYh1LhpBptzwHe/wI2SwXBIZx4MPo1zrkGIqqMQUhvoCsLCzOujDAKdISMEjAdGINBPLuktHhV6iXDSHtL1YU+kXjxomHYDm2sTqpEbduaILCPLOwy55IhBxpfDIePdoLr7fQiixqHUxhQg4WLdPItNTc6HMSzLQ5j0xPgGa0OMtugzUEvttRidCFwjvZKzY+2UBq9tsZyVkcMek8D2hNcZ9JiFmtjGL3x1ZWdz1PC6NkGCmQGKmVOsBVZyUU9szgpsI5hlPGSfcBSINkzjDTwmqFb8TxbldUEGAVtuXXkledz21tNgH03sXNUMLsSaMnnqY1sF0GPVqgzwobbBYEd6AukHqXzXIhXP85Ufp5kn42wVQw2rPrco1S10sfLW0hu6Z343THsEzJKQLvkRHFPPkKhaJeK/7nxpCVM1G/n/299AYHqPd6BjDeeAAAAAElFTkSuQmCC',
    "icon@1.5x" : b'iVBORw0KGgoAAAANSUhEUgAAACoAAAAqCAYAAADFw8lbAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAKXSURBVHgB7ZjNUQMxDIW1Ga4UAAVAATSQAqAA4L4UEAoId+BO7oEC4E4KoIIUAAXAPeglWuI4/pG0HGDgzXic7NrSt7bslZfoX39UDfXQYrE44grloGmaS0O/lqs2ujxhG5Ncnx3yw51w2ZPLN4b+ZkjIBJpxAs1IIS8kNCClCpBzdvTm7K+ChFSgBUjokXQyQYrPL1VBK5DQjOzSQOpBFZATzbTHskJCA2uHQOr4ytg2+RxYO4jckKI2hq353ALVQnK7Uy7HpNckB5vbEcI/jRMybFcdXW6/y23eFfY3/IQX1PtoAHkaOWtzMSeQuPeMWpzXQib54BtvJgFZOtd0jmD3uM1VArIN2pR8FP0kk5La1PL9MVep+HzsYAttTjxbWvJdHzx1bs9DEnIgJdQh4pHrUQbywQO55CCnGGifqztaZ1BzWgFeUBoSOcEZOdU3H+1gX7mMaT3SsXD/HCufnOoFCgksAACcg7zwTnknc+Kc0T2tQyAUHgCh8EE9ZdlHt5SI01jYAYZcpti+qIfcoApI7BYYUSywZds+sK4YVUI+cZly2Q2uu+PVPKIKyBmtIO8iSMg9siZQdoBVPS1AYi+9qpgB7L3YUks99WI4NUqdNqZVMfLv0n5OCmkPd0cWSIh/49pIgFKCLYTBkL4DVJLjEiR0mVogMlq3hX6wea1JwGuHOxgYU1k3penjezhO13LQcQ02G6OSII+oLPXZSZndZ+2VDnc1yAfLAU/aPlWaZU8LqcMdPn7Vnhwpm/rDWCD0qa3yNhUGnlfocoWTQ5Lm4fNk/zdTJfi7bcifV662LTxoDhZxuhUipcUUBz/gzvrmlYH91AvE92EDsFxepAzpm4X1ENjXnPerxixfRH6U/X/9en0Cm5eV/TOS4w8AAAAASUVORK5CYII=',
    "icon@2x" : b'iVBORw0KGgoAAAANSUhEUgAAADgAAAA4CAYAAACohjseAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAOWSURBVHgB7ZrPddpAEMYHXq4UkBTgBmjABYQCcO64gHCPuNu5m3vMPeYOBYQGKAAX4ALIfPIsWSvSamY18svL0+89PRm02p1v/84MJhoYGBjokRH1yPl8nvJtOhqN1mSE313wbdHweK2tc0zOsGETGMfXjj8+8HUiI17iwAdyAsL4NpdrIl+f2JgtGfAUBzoLlGkIg6Y1j03GeIsDnQS2GISpeSCfurLEgew12GIQOLBRz6Snkzix5y+yBCrEgawer9ZhEOcjUCnuyTh6tXQVB0wCleKAaefMRWOPWqBBHKaVenPJRWuPSqBRnMfai9vtYk+7QKs4Lv+R/FhURVrEgaQvmiEulDePpNXwJhuqX44dGqyKA+j5r6QEbp4Ylzu9Gzu0q7NdJy4w5++/tVUg7+5wzxSZnC1dpmgQ94n//pmo5sjXLZd9qam/4NvnmjrdNrXkCCZ69FIx30982ySqueLrId58JKQq6K04sDCMpGqdqwLeSo/WVsxlEPtNG6rA6K34vb2EVSh7Rc3MPDwhoI7ow3bd1Gti+CNf1WMC4jBFjzKd7ygtbsNl78kJ15SFCMDoBJGYvstIXPysjiOXvSFH3HMyLKRcc/Rn5J6V4k6hPDnSS9JJovyTiINgTLl3Fwf6zqqF0Zwkil3WKPWAe1YtwOJwBLSJA/d9iQO9CBRxBbWLw5GzxRrla0494JY2DGR6IeXREfmkbriOoEHcPggRpzyci4umGDAXt03GIA475hf4pol3kNNZkQMuU1RGQbOGwnHwImuuqUNm/Bz373VOuoXOI9jgNNcBQ2+is/FR8U5jJKKlS+IXEQGM1IgDq+ggnyrfQUf86JIGyU38aiKCGJx1+/CB/0Z4tVG+W7p5uSJzEr9oECOnFbcWQW+QiEGbXswWaU38apzmmG3Lubak13WmIUukJR60ilOFPhn1mnxXbeK3XOwGI3AcqLJqkvK4pVfDNZTrn2261hTWJH6x42mc5oA59BGRS9IDW+7E502SFGiICGKWOXGd/J5hTVUUba5dKvELT6MgG51CH9ltrc72IjWStQL5hRkp11BE7XFgRXZdt5/fvKKJjWeYw3UVpD8+ypiy6eG4oYEn0k+Vg2eaLwI7a9tazs9sK7PL1t1PjTjYKZGqzHZu6h5cQh/qCTk+sBdU23D9oZXkX7N+Rdfu7PtDZ1v7s6ht14g/biQWeU3vjIjUhmb/cCMDAwP/Fb8BVncxghHI9pgAAAAASUVORK5CYII='
  }
}

config = '{\n\
  "name": "hello world",\n\
  "guid": "asc.{' + str(uuid.uuid4()) + '}",\n\
  "baseUrl": "",\n\
  "variations": [\n\
    {\n\
      "description": "hello world",\n\
      "url": "index.html",\n\
      "icons": [ "resources/light/icon.png", "resources/light/icon@2x.png" ],\n\
      "icons2": [\n\
          {\n\
              "style" : "light",\n\
\n\
              "100%": {\n\
                  "normal": "resources/light/icon.png"\n\
              },\n\
              "150%": {\n\
                  "normal": "resources/light/icon@1.5x.png"\n\
              },\n\
              "200%": {\n\
                  "normal": "resources/light/icon@2x.png"\n\
              }\n\
          },\n\
          {\n\
              "style" : "dark",\n\
\n\
              "100%": {\n\
                  "normal": "resources/dark/icon.png"\n\
              },\n\
              "150%": {\n\
                  "normal": "resources/dark/icon@1.5x.png"\n\
              },\n\
              "200%": {\n\
                  "normal": "resources/dark/icon@2x.png"\n\
              }\n\
          }\n\
      ],\n\
      "isViewer": false,\n\
      "EditorsSupport": ["word"],\n\
      "isVisual": false,\n\
      "isModal": true,\n\
      "isInsideMode": false,\n\
      "initDataType": "none",\n\
      "initData": "",\n\
      "isUpdateOleOnResize": true,\n\
      "buttons": []\n\
    },\n\
    {\n\
      "description": "About",\n\
      "url": "index_about.html",\n\
      "icons": [ "resources/light/icon.png", "resources/light/icon@2x.png" ],\n\
      "icons2": [\n\
          {\n\
              "style" : "light",\n\
\n\
              "100%": {\n\
                  "normal": "resources/light/icon.png"\n\
              },\n\
              "150%": {\n\
                  "normal": "resources/light/icon@1.5x.png"\n\
              },\n\
              "200%": {\n\
                  "normal": "resources/light/icon@2x.png"\n\
              }\n\
          },\n\
          {\n\
              "style" : "dark",\n\
\n\
              "100%": {\n\
                  "normal": "resources/dark/icon.png"\n\
              },\n\
              "150%": {\n\
                  "normal": "resources/dark/icon@1.5x.png"\n\
              },\n\
              "200%": {\n\
                  "normal": "resources/dark/icon@2x.png"\n\
              }\n\
          }\n\
      ],\n\
      "isViewer": false,\n\
      "EditorsSupport": ["word"],\n\
      "isVisual": true,\n\
      "isModal": true,\n\
      "isInsideMode": false,\n\
      "initDataType": "none",\n\
      "initData": "",\n\
      "isUpdateOleOnResize": true,\n\
      "buttons": [\n\
        {\n\
          "text": "Ok",\n\
          "primary": true\n\
        }\n\
      ],\n\
\n\
      "size": [392, 147]\n\
    }\n\
  ]\n\
}'

index_html = '<!--\n\
 (c) Copyright Ascensio System SIA 2020\n\
\n\
 Licensed under the Apache License, Version 2.0 (the "License");\n\
 you may not use this file except in compliance with the License.\n\
 You may obtain a copy of the License at\n\
\n\
     http://www.apache.org/licenses/LICENSE-2.0\n\
\n\
 Unless required by applicable law or agreed to in writing, software\n\
 distributed under the License is distributed on an "AS IS" BASIS,\n\
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n\
 See the License for the specific language governing permissions and\n\
 limitations under the License.\n\
 -->\n\
<!DOCTYPE html>\n\
<html>\n\
<head>\n\
    <meta charset="UTF-8" />\n\
    <title>Hello world</title>\n\
    <script type="text/javascript" src="https://onlyoffice.github.io/sdkjs-plugins/v1/plugins.js"></script>\n\
    <script type="text/javascript" src="https://onlyoffice.github.io/sdkjs-plugins/v1/plugins-ui.js"></script>\n\
    <link rel="stylesheet" href="https://onlyoffice.github.io/sdkjs-plugins/v1/plugins.css">\n\
    <script type="text/javascript" src="scripts/code.js"></script>\n\
</head>\n\
<body>\n\
</body>\n\
</html>'

index_about = '<!--\n\
 (c) Copyright Ascensio System SIA 2020\n\
\n\
 Licensed under the Apache License, Version 2.0 (the "License");\n\
 you may not use this file except in compliance with the License.\n\
 You may obtain a copy of the License at\n\
\n\
     http://www.apache.org/licenses/LICENSE-2.0\n\
\n\
 Unless required by applicable law or agreed to in writing, software\n\
 distributed under the License is distributed on an "AS IS" BASIS,\n\
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n\
 See the License for the specific language governing permissions and\n\
 limitations under the License.\n\
 -->\n\
<!DOCTYPE html>\n\
<html lang="en">\n\
<head>\n\
    <meta charset="UTF-8">\n\
    <title>About</title>\n\
    <style>\n\
        p, a{\n\
            font-size: 12px;\n\
            font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;\n\
        }\n\
\n\
\n\
        a:link {\n\
            color: darkgrey;\n\
        }\n\
\n\
        /* visited link */\n\
        a:visited {\n\
            color: darkgrey;\n\
        }\n\
\n\
        /* mouse over link */\n\
        a:hover {\n\
            color: #8d8d8d;\n\
        }\n\
\n\
        /* selected link */\n\
        a:active {\n\
            color: darkgrey;\n\
        }\n\
    </style>\n\
        <script type="text/javascript" src="https://onlyoffice.github.io/sdkjs-plugins/v1/plugins.js"></script>\n\
        <script type="text/javascript" src="https://onlyoffice.github.io/sdkjs-plugins/v1/plugins-ui.js"></script>\n\
        <link rel="stylesheet" href="https://onlyoffice.github.io/sdkjs-plugins/v1/plugins.css">\n\
    <script type="text/javascript">\n\
        window.Asc.plugin.init = function()\n\
        {\n\
            this.resizeWindow(392, 147, 392, 147, 392, 147);\n\
            // none\n\
        };\n\
\n\
        window.Asc.plugin.button = function(id)\n\
        {\n\
            this.executeCommand("close", "");\n\
        };\n\
\n\
    </script>\n\
</head>\n\
<body style="padding-left: 20px; padding-right: 20px">\n\
<p style="font-size: 15px">Hello World! Add-on</p>\n\
<p style="font-size: 12px">This simple plugin is designed to show the basic functionality of ONLYOFFICE Document Editor plugins. It inserts the "Hello World!" phrase when you press the button.</p>\n\
<p style="font-size: 12px"><a href="https://github.com/ONLYOFFICE/sdkjs-plugins/tree/master/helloworld" target="_blank">Source code.</a></p>\n\
</body>\n\
</html>'

code = '/**\n\
 *\n\
 * (c) Copyright Ascensio System SIA 2020\n\
 *\n\
 * Licensed under the Apache License, Version 2.0 (the "License");\n\
 * you may not use this file except in compliance with the License.\n\
 * You may obtain a copy of the License at\n\
 *\n\
 *     http://www.apache.org/licenses/LICENSE-2.0\n\
 *\n\
 * Unless required by applicable law or agreed to in writing, software\n\
 * distributed under the License is distributed on an "AS IS" BASIS,\n\
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n\
 * See the License for the specific language governing permissions and\n\
 * limitations under the License.\n\
 *\n\
 */\n\
\n\
// Example insert text into editors (different implementations)\n\
(function(window, undefined){\n\
\n\
    var sText = "Hello world!";\n\
\n\
    window.Asc.plugin.init = function()\n\
    {\n\
        var variant = 2;\n\
\n\
        switch (variant)\n\
        {\n\
            case 0:\n\
            {\n\
                // serialize command as text\n\
                var sScript = "var oDocument = Api.GetDocument();";\n\
                sScript += "oParagraph = Api.CreateParagraph();";\n\
                sScript += "oParagraph.AddText(" + sText + ");";\n\
                sScript += "oDocument.InsertContent([oParagraph]);";\n\
                this.info.recalculate = true;\n\
                this.executeCommand("close", sScript);\n\
                break;\n\
            }\n\
            case 1:\n\
            {\n\
                // call command without external variables\n\
                this.callCommand(function() {\n\
                    var oDocument = Api.GetDocument();\n\
                    var oParagraph = Api.CreateParagraph();\n\
                    oParagraph.AddText("Hello world!");\n\
                    oDocument.InsertContent([oParagraph]);\n\
                }, true);\n\
                break;\n\
            }\n\
            case 2:\n\
            {\n\
                // call command with external variables\n\
                Asc.scope.text = sText; // export variable to plugin scope\n\
                this.callCommand(function() {\n\
                    var oDocument = Api.GetDocument();\n\
                    var oParagraph = Api.CreateParagraph();\n\
                    oParagraph.AddText(Asc.scope.text); // or oParagraph.AddText(scope.text);\n\
                    oDocument.InsertContent([oParagraph]);\n\
                }, true);\n\
                break;\n\
            }\n\
            default:\n\
                break;\n\
        }\n\
    };\n\
\n\
    window.Asc.plugin.button = function(id)\n\
    {\n\
    };\n\
\n\
})(window, undefined);'

readme = '## Overview\n\
\n\
This simple plugin is designed to show the basic functionality of ONLYOFFICE Document Editor plugins. It inserts the "Hello World!" phrase when you press the button.\n\
\n\
It is without interface plugin and is not installed by default in cloud, [self-hosted](https://github.com/ONLYOFFICE/DocumentServer) and [desktop version](https://github.com/ONLYOFFICE/DesktopEditors) of ONLYOFFICE editors. \n\
\n\
## How to use\n\
\n\
1. Open the Plugins tab and press "hello world".\n\
\n\
If you need more information about how to use or write your own plugin, please see this https://api.onlyoffice.com/plugin/basic'


writeFile('./config.json', config)
writeFile('./index.html', index_html)
writeFile('./index_about.html', index_about)
writeFile('./README.md', readme)

if True == os.path.isdir('./scripts'):
  shutil.rmtree('./scripts', ignore_errors=True)
os.mkdir('./scripts')
writeFile('./scripts/code.js', code)

# documentation
old_cur = os.getcwd()
#os.chdir("../../../sdkjs")
#if True == os.path.isdir(old_cur + '/lib'):
#  shutil.rmtree(old_cur + '/lib', ignore_errors=True)
#os.mkdir(old_cur + '/lib')
#convert_to_interface(["common/apiBase_plugins.js", "word/api_plugins.js", "slide/api_plugins.js", "cell/api_plugins.js" ], "common")


create_imgs(imgs)