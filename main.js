const { app, BrowserWindow, Menu, Tray, shell, ipcMain, dialog, nativeImage } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// Keep a global reference of the window object
let mainWindow;
let tray = null;
let pythonProcess = null;
const isDev = process.env.NODE_ENV === 'development';

// Enable live reload for development
if (isDev) {
  require('electron-reload')(__dirname, {
    electron: path.join(__dirname, '..', 'node_modules', '.bin', 'electron'),
    hardResetMethod: 'exit'
  });
}

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    icon: getIconPath(),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    show: false, // Don't show until ready
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default'
  });

  // Start Python backend
  startPythonBackend();

  // Load the web interface
  setTimeout(() => {
    mainWindow.loadURL('http://localhost:5000');
  }, 3000); // Wait for Python backend to start

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Focus on window
    if (isDev) {
      mainWindow.webContents.openDevTools();
    }
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Prevent navigation away from the app
  mainWindow.webContents.on('will-navigate', (event, navigationUrl) => {
    const parsedUrl = new URL(navigationUrl);
    
    if (parsedUrl.origin !== 'http://localhost:5000') {
      event.preventDefault();
      shell.openExternal(navigationUrl);
    }
  });
}

function startPythonBackend() {
  const pythonPath = getPythonPath();
  const scriptPath = getPythonScriptPath();
  
  console.log('Starting Python backend...');
  console.log('Python path:', pythonPath);
  console.log('Script path:', scriptPath);
  
  // Check if Python script exists
  if (!fs.existsSync(scriptPath)) {
    console.error('Python script not found:', scriptPath);
    showErrorDialog('Python script not found', `Could not find the Python backend at: ${scriptPath}`);
    return;
  }
  
  // Start Python process
  pythonProcess = spawn(pythonPath, [scriptPath, '--host', '127.0.0.1', '--port', '5000'], {
    cwd: path.dirname(scriptPath),
    stdio: ['pipe', 'pipe', 'pipe']
  });
  
  pythonProcess.stdout.on('data', (data) => {
    console.log('Python stdout:', data.toString());
  });
  
  pythonProcess.stderr.on('data', (data) => {
    console.error('Python stderr:', data.toString());
  });
  
  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
    if (code !== 0 && mainWindow) {
      showErrorDialog('Backend Error', 'The Python backend has stopped unexpectedly.');
    }
  });
  
  pythonProcess.on('error', (err) => {
    console.error('Failed to start Python process:', err);
    showErrorDialog('Startup Error', `Failed to start Python backend: ${err.message}`);
  });
}

function getPythonPath() {
  // Try different Python executables
  const pythonCommands = ['python3', 'python', 'py'];
  
  if (process.platform === 'win32') {
    return pythonCommands.map(cmd => `${cmd}.exe`);
  }
  
  return pythonCommands;
}

function getPythonScriptPath() {
  if (isDev) {
    return path.join(__dirname, 'hackathon_monitor_web.py');
  } else {
    return path.join(process.resourcesPath, 'python', 'hackathon_monitor_web.py');
  }
}

function getIconPath() {
  const iconName = process.platform === 'win32' ? 'icon.ico' : 
                   process.platform === 'darwin' ? 'icon.icns' : 'icon.png';
  
  return path.join(__dirname, 'assets', iconName);
}

function createTray() {
  const iconPath = path.join(__dirname, 'assets', 'tray-icon.png');
  
  // Create tray icon
  tray = new Tray(nativeImage.createFromPath(iconPath).resize({ width: 16, height: 16 }));
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show Hackathon Monitor',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        }
      }
    },
    {
      label: 'Scrape Once',
      click: () => {
        if (mainWindow) {
          mainWindow.webContents.executeJavaScript('scrapeOnce()');
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        app.quit();
      }
    }
  ]);
  
  tray.setToolTip('Hackathon Monitor');
  tray.setContextMenu(contextMenu);
  
  // Show window on tray click
  tray.on('click', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
        mainWindow.focus();
      }
    }
  });
}

function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Scrape Once',
          accelerator: 'CmdOrCtrl+R',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.executeJavaScript('scrapeOnce()');
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Open Data Folder',
          click: () => {
            const dataPath = isDev ? __dirname : path.join(process.resourcesPath, 'python');
            shell.openPath(dataPath);
          }
        },
        { type: 'separator' },
        {
          role: 'quit'
        }
      ]
    },
    {
      label: 'Monitor',
      submenu: [
        {
          label: 'Start Monitoring',
          accelerator: 'CmdOrCtrl+S',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.executeJavaScript('startMonitoring()');
            }
          }
        },
        {
          label: 'Stop Monitoring',
          accelerator: 'CmdOrCtrl+T',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.executeJavaScript('stopMonitoring()');
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Test Notification',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.executeJavaScript('testNotification()');
            }
          }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'close' }
      ]
    },
    {
      role: 'help',
      submenu: [
        {
          label: 'About Hackathon Monitor',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About Hackathon Monitor',
              message: 'Hackathon Monitor v1.0',
              detail: 'Cross-platform hackathon monitoring application\n\nMonitors DevPost, MLH, and Unstop for new hackathons\nSends notifications and saves data to Excel\n\nBuilt with Electron and Python'
            });
          }
        }
      ]
    }
  ];

  // macOS specific menu adjustments
  if (process.platform === 'darwin') {
    template.unshift({
      label: app.getName(),
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideOthers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' }
      ]
    });

    // Window menu
    template[4].submenu = [
      { role: 'close' },
      { role: 'minimize' },
      { role: 'zoom' },
      { type: 'separator' },
      { role: 'front' }
    ];
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

function showErrorDialog(title, content) {
  dialog.showErrorBox(title, content);
}

// App event handlers
app.whenReady().then(() => {
  createWindow();
  createMenu();
  createTray();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  // Kill Python process
  if (pythonProcess) {
    pythonProcess.kill();
  }
});

// IPC handlers
ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('show-save-dialog', async () => {
  const result = await dialog.showSaveDialog(mainWindow, {
    filters: [
      { name: 'Excel Files', extensions: ['xlsx'] },
      { name: 'CSV Files', extensions: ['csv'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  return result;
});

// Handle certificate errors (for development)
app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
  if (isDev) {
    event.preventDefault();
    callback(true);
  } else {
    callback(false);
  }
});
