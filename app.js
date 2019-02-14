const electron = require('electron')
const app = electron.app
const BrowserWindow = electron.BrowserWindow
const ejse = require('ejs-electron')

function createWindow() {
    let win = new BrowserWindow({ width: 1000, height: 500, resizable: false, webPreferences: { nodeIntegration: false } })

    win.loadFile('./app/views/index.ejs')
}

app.on('ready', createWindow)