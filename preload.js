const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  showSaveDialog: () => ipcRenderer.invoke('show-save-dialog'),
  
  // Platform information
  platform: process.platform,
  
  // App information
  isElectron: true,
  
  // Utility functions
  openExternal: (url) => {
    // This will be handled by the main process
    window.open(url, '_blank');
  }
});

// Add some styling for Electron
document.addEventListener('DOMContentLoaded', () => {
  // Add Electron-specific CSS class
  document.body.classList.add('electron-app');
  
  // Add platform-specific class
  document.body.classList.add(`platform-${process.platform}`);
  
  // Disable drag and drop of files
  document.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.stopPropagation();
  });
  
  document.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
  });
  
  // Add custom title bar controls for Windows/Linux
  if (process.platform !== 'darwin') {
    const style = document.createElement('style');
    style.textContent = `
      .electron-app {
        -webkit-app-region: no-drag;
      }
      
      .electron-app .header {
        -webkit-app-region: drag;
      }
      
      .electron-app .header button,
      .electron-app .header input,
      .electron-app .header select {
        -webkit-app-region: no-drag;
      }
    `;
    document.head.appendChild(style);
  }
});
