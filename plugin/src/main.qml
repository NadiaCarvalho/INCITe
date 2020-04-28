import QtQuick 2.3
import MuseScore 3.0

MuseScore {
      menuPath: "Plugins.pluginName"
      description: "Description goes here"
      version: "1.0"
      onRun: {
            if (typeof curScore === 'undefined')
                  Qt.quit();
                  
            console.log(curScore.selection.title)
            Qt.quit()
            }
      }
