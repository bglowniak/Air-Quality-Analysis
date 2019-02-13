const electron = require('electron')
const app = electron.app
const BrowserWindow = electron.BrowserWindow

function createWindow() {
    let win = new BrowserWindow({ width: 800, height: 600 })

    win.loadFile('./app/templates/base.html')
}

app.on('ready', createWindow)