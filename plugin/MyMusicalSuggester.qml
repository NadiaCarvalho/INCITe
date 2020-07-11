import MuseScore 3.0

// QtQuick
import QtQuick 2.2
import QtQuick.Dialogs 1.1

import FileIO 3.0

MuseScore {
  menuPath: "Plugins.Suggester"
  description: "Learn from selection and suggest new sequences to follow.\n\n"+
               "Requires to install Suggester (Free and OpenSource).\nMoreover at TODO"
  version: "1.0"
  requiresScore: true


  //for Linux and MacOS users
  property string nixSuggesterCommand : "MyMusicalSuggester "; //add -r, or more, for debug infos

  //for  Windows users
  property string winSuggesterCommand :  "MyMusicalSuggester.exe "; //add -r, or more, for debug infos

  property string xmlPath : "";
  property string SuggesterCommand : Qt.platform.os == "windows" ?  winSuggesterCommand:nixSuggesterCommand;
  // values for Qt.platform.os are at https://doc.qt.io/qt-5/qml-qtqml-qt.html#platform-prop

   QProcess {
    id: proc
  }

  FileIO {
    id: xmlFile
  }

  function runSuggester(){
      var path =  Qt.resolvedUrl(".");
      // remove prefixed "file:///"
      var path = path.replace(/^(file:\/{3})/,"");
      // unescape html codes like '%23' for '#'
      var cleanPath = decodeURIComponent(path);
      console.log(cleanPath);

      var cmd =  cleanPath + SuggesterCommand + "" +  xmlPath + '.mxl' +  " /K";
      console.log("Running Suggester with cmd: " + cmd);
      proc.start(cmd);
  }

  onRun: {
      if (typeof curScore === 'undefined')
         Qt.quit();

      //init paths
      xmlFile.source = xmlFile.tempPath() + "/" + curScore.scoreName + '_SEL';
      xmlPath = '"' + xmlFile.source + '"';

      console.log(xmlPath);

      // Call Suggester
      console.log("Starting Process for " + curScore.title + " from file " + curScore.scoreName + " in file " + xmlFile.source)
      var res = writeScore(curScore,  xmlFile.source,  'mxl')
      if (res) {
            runSuggester()
       }

       xmlFile.remove();

      Qt.quit();
   } // end onRun
}


