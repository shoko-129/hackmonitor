#!/usr/bin/env node
/**
 * Electron Build Script for Hackathon Monitor
 * Builds the desktop application for all platforms
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Building Hackathon Monitor Desktop App');
console.log('=' * 45);

// Check if Node.js and npm are available
function checkPrerequisites() {
  try {
    execSync('node --version', { stdio: 'pipe' });
    execSync('npm --version', { stdio: 'pipe' });
    console.log('✅ Node.js and npm are available');
    return true;
  } catch (error) {
    console.log('❌ Node.js or npm not found');
    console.log('Please install Node.js from: https://nodejs.org/');
    return false;
  }
}

// Install dependencies
function installDependencies() {
  console.log('📦 Installing Electron dependencies...');
  
  try {
    execSync('npm install', { stdio: 'inherit' });
    console.log('✅ Dependencies installed successfully');
    return true;
  } catch (error) {
    console.log('❌ Failed to install dependencies');
    console.log('Error:', error.message);
    return false;
  }
}

// Create icon files from logo.png
function createIcons() {
  console.log('🎨 Creating application icons...');
  
  const logoPath = 'logo.png';
  const assetsDir = 'assets';
  
  // Create assets directory
  if (!fs.existsSync(assetsDir)) {
    fs.mkdirSync(assetsDir);
  }
  
  // Copy logo as PNG icon
  if (fs.existsSync(logoPath)) {
    fs.copyFileSync(logoPath, path.join(assetsDir, 'icon.png'));
    fs.copyFileSync(logoPath, path.join(assetsDir, 'tray-icon.png'));
    console.log('✅ PNG icons created');
  } else {
    console.log('⚠️ logo.png not found, using default icons');
    createDefaultIcon();
  }
  
  // Note about other icon formats
  console.log('ℹ️ For Windows (.ico) and macOS (.icns) icons:');
  console.log('   Convert logo.png using online tools or:');
  console.log('   - Windows: Use online PNG to ICO converter');
  console.log('   - macOS: Use iconutil or online PNG to ICNS converter');
}

function createDefaultIcon() {
  // Create a simple default icon (SVG that can be converted)
  const defaultIcon = `
<svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
  <rect width="256" height="256" fill="#667eea"/>
  <circle cx="128" cy="128" r="80" fill="white"/>
  <text x="128" y="140" text-anchor="middle" fill="#667eea" font-size="60" font-family="Arial">🎯</text>
</svg>`;
  
  fs.writeFileSync('assets/icon.svg', defaultIcon);
  console.log('✅ Default SVG icon created');
}

// Build for specific platform
function buildForPlatform(platform) {
  console.log(`🔨 Building for ${platform}...`);
  
  const commands = {
    'windows': 'npm run build-win',
    'macos': 'npm run build-mac', 
    'linux': 'npm run build-linux',
    'all': 'npm run build'
  };
  
  try {
    execSync(commands[platform] || commands.all, { stdio: 'inherit' });
    console.log(`✅ ${platform} build completed`);
    return true;
  } catch (error) {
    console.log(`❌ ${platform} build failed`);
    console.log('Error:', error.message);
    return false;
  }
}

// Main build process
function main() {
  const args = process.argv.slice(2);
  const platform = args[0] || 'current';
  
  console.log(`Building for: ${platform}`);
  console.log();
  
  // Check prerequisites
  if (!checkPrerequisites()) {
    process.exit(1);
  }
  
  // Install dependencies
  if (!installDependencies()) {
    process.exit(1);
  }
  
  // Create icons
  createIcons();
  
  // Build application
  let buildSuccess = false;
  
  if (platform === 'all') {
    console.log('🔨 Building for all platforms...');
    buildSuccess = buildForPlatform('all');
  } else if (platform === 'windows') {
    buildSuccess = buildForPlatform('windows');
  } else if (platform === 'macos') {
    buildSuccess = buildForPlatform('macos');
  } else if (platform === 'linux') {
    buildSuccess = buildForPlatform('linux');
  } else {
    // Build for current platform
    const currentPlatform = process.platform === 'win32' ? 'windows' :
                           process.platform === 'darwin' ? 'macos' : 'linux';
    buildSuccess = buildForPlatform(currentPlatform);
  }
  
  if (buildSuccess) {
    console.log();
    console.log('🎉 Build completed successfully!');
    console.log('📦 Check the dist/ folder for your application');
    console.log();
    console.log('📋 Distribution files:');
    
    // List generated files
    const distDir = 'dist';
    if (fs.existsSync(distDir)) {
      const files = fs.readdirSync(distDir);
      files.forEach(file => {
        const filePath = path.join(distDir, file);
        const stats = fs.statSync(filePath);
        const size = (stats.size / (1024 * 1024)).toFixed(1);
        console.log(`   📄 ${file} (${size} MB)`);
      });
    }
    
    console.log();
    console.log('🚀 Your desktop app is ready for distribution!');
  } else {
    console.log();
    console.log('❌ Build failed!');
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = { main, buildForPlatform, createIcons };
