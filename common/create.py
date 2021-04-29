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
