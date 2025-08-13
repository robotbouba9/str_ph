const {
  app,
  BrowserWindow,
  Menu,
  dialog,
  shell,
  ipcMain,
} = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const axios = require("axios");
const Store = require("electron-store");

// إعداد التخزين المحلي
const store = new Store();

class PhoneStoreApp {
  constructor() {
    this.mainWindow = null;
    this.flaskProcess = null;
    this.serverPort = 5000;
    this.serverUrl = `http://127.0.0.1:${this.serverPort}`;
    this.isServerReady = false;

    // إعدادات التطبيق
    this.appSettings = {
      windowWidth: store.get("windowWidth", 1200),
      windowHeight: store.get("windowHeight", 800),
      windowMaximized: store.get("windowMaximized", false),
      serverPort: store.get("serverPort", 5000),
      autoStartServer: store.get("autoStartServer", true),
      theme: store.get("theme", "light"),
    };
  }

  async init() {
    // إعداد التطبيق
    app.setName("برنامج إدارة مخزون محل الهواتف");

    // إعداد الأحداث
    app.whenReady().then(() => this.createWindow());
    app.on("window-all-closed", () => this.onWindowAllClosed());
    app.on("activate", () => this.onActivate());
    app.on("before-quit", () => this.cleanup());

    // إعداد IPC
    this.setupIPC();
  }

  async createWindow() {
    // إنشاء النافذة الرئيسية
    this.mainWindow = new BrowserWindow({
      width: this.appSettings.windowWidth,
      height: this.appSettings.windowHeight,
      minWidth: 800,
      minHeight: 600,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        preload: path.join(__dirname, "preload.js"),
      },
      icon: path.join(__dirname, "assets", "icon.png"),
      title: "برنامج إدارة مخزون محل الهواتف",
      show: false, // لا تظهر حتى يكون الخادم جاهز
      titleBarStyle: "default",
    });

    // استعادة حالة النافذة
    if (this.appSettings.windowMaximized) {
      this.mainWindow.maximize();
    }

    // إعداد الأحداث
    this.setupWindowEvents();

    // إعداد القائمة
    this.createMenu();

    // بدء الخادم
    await this.startServer();

    // تحميل التطبيق
    await this.loadApp();
  }

  setupWindowEvents() {
    // حفظ حالة النافذة
    this.mainWindow.on("resize", () => {
      if (!this.mainWindow.isMaximized()) {
        const [width, height] = this.mainWindow.getSize();
        store.set("windowWidth", width);
        store.set("windowHeight", height);
      }
    });

    this.mainWindow.on("maximize", () => {
      store.set("windowMaximized", true);
    });

    this.mainWindow.on("unmaximize", () => {
      store.set("windowMaximized", false);
    });

    // إظهار النافذة عند الجاهزية
    this.mainWindow.once("ready-to-show", () => {
      this.mainWindow.show();

      // التركيز على النافذة
      if (process.platform === "darwin") {
        app.dock.show();
      }
    });

    // منع إغلاق النافذة بدون تنظيف
    this.mainWindow.on("close", (event) => {
      if (!app.isQuiting) {
        event.preventDefault();
        this.gracefulShutdown();
      }
    });
  }

  async startServer() {
    if (this.flaskProcess) {
      return;
    }

    try {
      console.log("🚀 بدء تشغيل خادم Flask...");

      // تحديد مسار Python
      const pythonCmd = process.platform === "win32" ? "python" : "python3";
      const scriptPath = path.join(__dirname, "..", "secure_app.py");

      // بدء العملية
      this.flaskProcess = spawn(pythonCmd, [scriptPath], {
        cwd: path.join(__dirname, ".."),
        stdio: ["pipe", "pipe", "pipe"],
      });

      // معالجة المخرجات
      this.flaskProcess.stdout.on("data", (data) => {
        console.log(`Flask: ${data.toString()}`);
      });

      this.flaskProcess.stderr.on("data", (data) => {
        console.error(`Flask Error: ${data.toString()}`);
      });

      this.flaskProcess.on("close", (code) => {
        console.log(`Flask process exited with code ${code}`);
        this.flaskProcess = null;
        this.isServerReady = false;
      });

      // انتظار بدء الخادم
      await this.waitForServer();
    } catch (error) {
      console.error("خطأ في بدء الخادم:", error);
      this.showErrorDialog("خطأ في بدء الخادم", error.message);
    }
  }

  async waitForServer(maxAttempts = 30) {
    for (let i = 0; i < maxAttempts; i++) {
      try {
        const response = await axios.get(`${this.serverUrl}/api/status`, {
          timeout: 1000,
        });

        if (response.status === 200) {
          console.log("✅ الخادم جاهز");
          this.isServerReady = true;
          return true;
        }
      } catch (error) {
        // انتظار ثانية واحدة قبل المحاولة التالية
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
    }

    throw new Error("فشل في الاتصال بالخادم");
  }

  async loadApp() {
    if (!this.isServerReady) {
      await this.waitForServer();
    }

    // تحميل التطبيق
    await this.mainWindow.loadURL(this.serverUrl);

    // إضافة CSS مخصص للتطبيق
    await this.mainWindow.webContents.insertCSS(`
            /* تحسينات خاصة بتطبيق Electron */
            body {
                -webkit-user-select: none;
                user-select: none;
            }
            
            input, textarea, [contenteditable] {
                -webkit-user-select: text;
                user-select: text;
            }
            
            /* شريط التمرير المخصص */
            ::-webkit-scrollbar {
                width: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: #f1f1f1;
            }
            
            ::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: #555;
            }
        `);
  }

  createMenu() {
    const template = [
      {
        label: "ملف",
        submenu: [
          {
            label: "الصفحة الرئيسية",
            accelerator: "CmdOrCtrl+H",
            click: () => this.navigateTo("/"),
          },
          { type: "separator" },
          {
            label: "نسخة احتياطية",
            accelerator: "CmdOrCtrl+B",
            click: () => this.createBackup(),
          },
          {
            label: "استعادة نسخة احتياطية",
            click: () => this.restoreBackup(),
          },
          { type: "separator" },
          {
            label: "إعدادات",
            accelerator: "CmdOrCtrl+,",
            click: () => this.showSettings(),
          },
          { type: "separator" },
          {
            label: "خروج",
            accelerator: process.platform === "darwin" ? "Cmd+Q" : "Ctrl+Q",
            click: () => this.gracefulShutdown(),
          },
        ],
      },
      {
        label: "إدارة",
        submenu: [
          {
            label: "المنتجات",
            accelerator: "CmdOrCtrl+P",
            click: () => this.navigateTo("/products"),
          },
          {
            label: "العملاء",
            accelerator: "CmdOrCtrl+C",
            click: () => this.navigateTo("/customers"),
          },
          {
            label: "الموردين",
            accelerator: "CmdOrCtrl+S",
            click: () => this.navigateTo("/suppliers"),
          },
          {
            label: "المبيعات",
            accelerator: "CmdOrCtrl+L",
            click: () => this.navigateTo("/sales"),
          },
        ],
      },
      {
        label: "تقارير",
        submenu: [
          {
            label: "التقارير والإحصائيات",
            accelerator: "CmdOrCtrl+R",
            click: () => this.navigateTo("/reports"),
          },
          { type: "separator" },
          {
            label: "تصدير البيانات",
            click: () => this.exportData(),
          },
        ],
      },
      {
        label: "عرض",
        submenu: [
          {
            label: "إعادة تحميل",
            accelerator: "CmdOrCtrl+R",
            click: () => this.mainWindow.reload(),
          },
          {
            label: "ملء الشاشة",
            accelerator: process.platform === "darwin" ? "Ctrl+Cmd+F" : "F11",
            click: () => {
              this.mainWindow.setFullScreen(!this.mainWindow.isFullScreen());
            },
          },
          { type: "separator" },
          {
            label: "تكبير",
            accelerator: "CmdOrCtrl+Plus",
            click: () => {
              const currentZoom = this.mainWindow.webContents.getZoomLevel();
              this.mainWindow.webContents.setZoomLevel(currentZoom + 0.5);
            },
          },
          {
            label: "تصغير",
            accelerator: "CmdOrCtrl+-",
            click: () => {
              const currentZoom = this.mainWindow.webContents.getZoomLevel();
              this.mainWindow.webContents.setZoomLevel(currentZoom - 0.5);
            },
          },
          {
            label: "الحجم الطبيعي",
            accelerator: "CmdOrCtrl+0",
            click: () => {
              this.mainWindow.webContents.setZoomLevel(0);
            },
          },
        ],
      },
      {
        label: "مساعدة",
        submenu: [
          {
            label: "دليل الاستخدام",
            click: () => this.showHelp(),
          },
          {
            label: "اختصارات لوحة المفاتيح",
            click: () => this.showShortcuts(),
          },
          { type: "separator" },
          {
            label: "حول البرنامج",
            click: () => this.showAbout(),
          },
        ],
      },
    ];

    // إضافة قائمة المطور في وضع التطوير
    if (process.env.NODE_ENV === "development") {
      template.push({
        label: "مطور",
        submenu: [
          {
            label: "أدوات المطور",
            accelerator: "F12",
            click: () => this.mainWindow.webContents.toggleDevTools(),
          },
          {
            label: "إعادة تشغيل الخادم",
            click: () => this.restartServer(),
          },
        ],
      });
    }

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
  }

  setupIPC() {
    // معالجة طلبات من العارض
    ipcMain.handle("get-app-version", () => {
      return app.getVersion();
    });

    ipcMain.handle("get-server-status", () => {
      return {
        isReady: this.isServerReady,
        url: this.serverUrl,
        port: this.serverPort,
      };
    });

    ipcMain.handle("create-backup", () => {
      return this.createBackup();
    });
  }

  // وظائف المساعدة
  navigateTo(path) {
    if (this.mainWindow && this.isServerReady) {
      this.mainWindow.loadURL(`${this.serverUrl}${path}`);
    }
  }

  async createBackup() {
    try {
      const result = await dialog.showSaveDialog(this.mainWindow, {
        title: "حفظ نسخة احتياطية",
        defaultPath: `phone_store_backup_${
          new Date().toISOString().split("T")[0]
        }.db`,
        filters: [
          { name: "قاعدة البيانات", extensions: ["db"] },
          { name: "جميع الملفات", extensions: ["*"] },
        ],
      });

      if (!result.canceled) {
        // نسخ قاعدة البيانات
        const fs = require("fs");
        const sourcePath = path.join(__dirname, "..", "phone_store.db");

        if (fs.existsSync(sourcePath)) {
          fs.copyFileSync(sourcePath, result.filePath);

          dialog.showMessageBox(this.mainWindow, {
            type: "info",
            title: "نجح الحفظ",
            message: "تم إنشاء النسخة الاحتياطية بنجاح",
            detail: `تم حفظ النسخة في: ${result.filePath}`,
          });
        } else {
          throw new Error("قاعدة البيانات غير موجودة");
        }
      }
    } catch (error) {
      this.showErrorDialog("خطأ في النسخ الاحتياطي", error.message);
    }
  }

  async restoreBackup() {
    const result = await dialog.showOpenDialog(this.mainWindow, {
      title: "اختر ملف النسخة الاحتياطية",
      filters: [
        { name: "قاعدة البيانات", extensions: ["db"] },
        { name: "جميع الملفات", extensions: ["*"] },
      ],
      properties: ["openFile"],
    });

    if (!result.canceled && result.filePaths.length > 0) {
      const confirmResult = await dialog.showMessageBox(this.mainWindow, {
        type: "warning",
        title: "تأكيد الاستعادة",
        message: "هل أنت متأكد من استعادة النسخة الاحتياطية؟",
        detail: "سيتم استبدال البيانات الحالية بالكامل",
        buttons: ["نعم", "إلغاء"],
        defaultId: 1,
      });

      if (confirmResult.response === 0) {
        try {
          const fs = require("fs");
          const targetPath = path.join(__dirname, "..", "phone_store.db");

          fs.copyFileSync(result.filePaths[0], targetPath);

          dialog.showMessageBox(this.mainWindow, {
            type: "info",
            title: "نجحت الاستعادة",
            message: "تم استعادة النسخة الاحتياطية بنجاح",
            detail: "سيتم إعادة تحميل التطبيق",
          });

          // إعادة تحميل التطبيق
          this.mainWindow.reload();
        } catch (error) {
          this.showErrorDialog("خطأ في الاستعادة", error.message);
        }
      }
    }
  }

  showSettings() {
    // يمكن إضافة نافذة إعدادات منفصلة
    dialog.showMessageBox(this.mainWindow, {
      type: "info",
      title: "الإعدادات",
      message: "نافذة الإعدادات ستكون متاحة في التحديث القادم",
      detail: "يمكنك تعديل الإعدادات من خلال ملف config.py حالياً",
    });
  }

  showHelp() {
    shell.openExternal("file://" + path.join(__dirname, "..", "README.md"));
  }

  showShortcuts() {
    dialog.showMessageBox(this.mainWindow, {
      type: "info",
      title: "اختصارات لوحة المفاتيح",
      message: "الاختصارات المتاحة:",
      detail: `
Ctrl+H - الصفحة الرئيسية
Ctrl+P - المنتجات
Ctrl+C - العملاء
Ctrl+S - الموردين
Ctrl+L - المبيعات
Ctrl+R - التقارير
Ctrl+B - نسخة احتياطية
F11 - ملء الشاشة
F12 - أدوات المطور (وضع التطوير)
Ctrl+Q - خروج
            `.trim(),
    });
  }

  showAbout() {
    dialog.showMessageBox(this.mainWindow, {
      type: "info",
      title: "حول البرنامج",
      message: "برنامج إدارة مخزون محل الهواتف",
      detail: `
الإصدار: 1.0.0
تطبيق سطح مكتب حديث لإدارة مخزون محلات الهواتف

المميزات:
• إدارة شاملة للمنتجات والعملاء والموردين
• نظام مبيعات متكامل
• تقارير وإحصائيات تفصيلية
• واجهة عربية حديثة
• نظام نسخ احتياطي

تم التطوير باستخدام:
• Electron للواجهة
• Flask للخادم الخلفي
• SQLite لقاعدة البيانات
            `.trim(),
    });
  }

  showErrorDialog(title, message) {
    dialog.showErrorBox(title, message);
  }

  async restartServer() {
    if (this.flaskProcess) {
      this.flaskProcess.kill();
      this.flaskProcess = null;
    }

    await this.startServer();
    this.mainWindow.reload();
  }

  async gracefulShutdown() {
    app.isQuiting = true;

    // إغلاق الخادم
    if (this.flaskProcess) {
      this.flaskProcess.kill();
    }

    // إغلاق التطبيق
    app.quit();
  }

  cleanup() {
    if (this.flaskProcess) {
      this.flaskProcess.kill();
    }
  }

  onWindowAllClosed() {
    if (process.platform !== "darwin") {
      app.quit();
    }
  }

  onActivate() {
    if (BrowserWindow.getAllWindows().length === 0) {
      this.createWindow();
    }
  }
}

// إنشاء وتشغيل التطبيق
const phoneStoreApp = new PhoneStoreApp();
phoneStoreApp.init();
