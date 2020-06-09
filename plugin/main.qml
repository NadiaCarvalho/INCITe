import MuseScore 3.0

// QtQuick
import QtQuick 2.2
import QtQuick.Dialogs 1.1

import FileIO 3.0

MuseScore {
  menuPath: "Plugins.Suggestor"
  description: "Learn from selection and suggest new sequences to follow.\n\n"+
               "Requires to install Suggestor (Free and OpenSource).\nMoreover at TODO"
  version: "1.0"
  requiresScore: true


  //for Linux and MacOS users
  property string nixMMACommand : "mma "; //add -r, or more, for debug infos

  //for  Windows users
  property string winMMACommand :  "APP.exe "; //add -r, or more, for debug infos

  property string xmlPath : "";
  property string mmaCommand : Qt.platform.os == "windows" ?  winMMACommand:nixMMACommand;
  // values for Qt.platform.os are at https://doc.qt.io/qt-5/qml-qtqml-qt.html#platform-prop

   QProcess {
    id: proc
  }

  FileIO {
    id: xmlFile
  }

  MessageDialog {
    id: generationCompleteDialog
    title: "Success"
    text: "MMA accompaniment is ready for you in MuseScore.\nThe source MMA file is available at "+ xmlPath;
    onAccepted: {
        Qt.quit();
    }
    Component.onCompleted: visible = false
  }

  MessageDialog {
    id: midFailureDialog
    title: "Generation incomplete"
    text: "";   /* text is set dynamically later, when error is known.
           "MMA accompaniment is ready for you, but we could not generate the MIDI file from it.\n"+
           "Please fix the following error: \n\n"+err+"\n\n"+
           "The generated MMA file is nevertheless available at "+xmlPath;*/
    onAccepted: {
        Qt.quit();
    }
    Component.onCompleted: visible = false
  }

  MessageDialog {
    id: mmaFailureDialog
    title: "Generation failed"
    text: "Could not generate MMA file ("+xmlPath+")\n\n"+
           "Please make sure the following directory exists and is writeable:\n  "+
           xmlFile.tempPath();
    onAccepted: {
        Qt.quit();
    }
    Component.onCompleted: visible = false
  }

  function runSuggestor(){
      var path =  Qt.resolvedUrl(".");
      // remove prefixed "file:///"
      var path = path.replace(/^(file:\/{3})/,"");
      // unescape html codes like '%23' for '#'
      var cleanPath = decodeURIComponent(path);
      console.log(cleanPath);

      var cmd =  cleanPath + mmaCommand + "" +  xmlPath + '.mxl' +  " /K";
      console.log("Running Suggestor with cmd: " + cmd);
      proc.start(cmd);
  }

  onRun: {
      if (typeof curScore === 'undefined')
         Qt.quit();

      //init paths
      xmlFile.source = xmlFile.tempPath() + "/" + curScore.scoreName + '_SEL';
      xmlPath = '"' + xmlFile.source + '"';

      console.log(xmlPath);

      // Call Suggestor
      console.log("Starting Process for " + curScore.title + " from file " + curScore.scoreName + " in file " + xmlFile.source)
      var res = writeScore(curScore,  xmlFile.source,  'mxl')
      if (res) {
            runSuggestor()
       }

       xmlFile.remove();

      Qt.quit();
   } // end onRun

}


