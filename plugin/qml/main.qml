import MuseScore 3.0

// QtQuick
import QtQuick 2.0

import QtQuick.Layouts 1.0
import QtQuick.Controls 1.4
import QtQuick.Dialogs 1.2

// 
//import Qt.labs.platform 1.0
//import FileIO 3.0

MuseScore {
      menuPath: "Plugins.pluginName"
      description: "Creates suggestions for continuations,"+
                  " based on a possible database and the selected score"
      version: "1.0"
      requiresScore: true

      pluginType: "dock"
      dockArea:   "right"
      width:  200
      id: mainApplication

      // if nothing is selected process whole score
      property bool processAll: false

      onRun: {
            if (!curScore) {
                  console.log("Quitting: no score");
                  Qt.quit();
            }

            mainApplication.visible = true
            console.log(curScore.selection)
            //Qt.quit()
      }
      
      GridLayout {

        
        Button {
          id: bUnloadProject
          visible: true
          text: qsTr("Unload project")
          width: 100
          onClicked: {
                resettingElements()
          }
          y: 595
          x: 10
        }
      
    
      }    
}


