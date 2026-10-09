using System;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;
using System.Threading;
using System.Web.Script.Serialization;

namespace PPTXTranslatorApp
{
    public class MainForm : Form
    {
        private TextBox txtPath;
        private Button btnBrowse;
        private CheckBox chkUA;
        private CheckBox chkEN;
        private Button btnStart;
        private ProgressBar progressBar;
        private TextBox txtLog;
        private Label lblTitle;
        private GroupBox grpFolder;
        private GroupBox grpOptions;
        private GroupBox grpLog;

        private string defaultWorkDir = @"c:\Users\tczvlnau\Desktop\Instr Zoid rack";
        private string dictUaPath;
        private string dictEnPath;

        public MainForm()
        {
            InitializeComponent();
            SetupPaths();
        }

        private void SetupPaths()
        {
            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            dictUaPath = Path.Combine(baseDir, @"src\dictionaries\dict_ua.json");
            dictEnPath = Path.Combine(baseDir, @"src\dictionaries\dict_en.json");

            if (!File.Exists(dictUaPath))
            {
                dictUaPath = @"c:\Users\tczvlnau\Desktop\Instr Zoid rack\Translator_for_isnt\src\dictionaries\dict_ua.json";
            }
            if (!File.Exists(dictEnPath))
            {
                dictEnPath = @"c:\Users\tczvlnau\Desktop\Instr Zoid rack\Translator_for_isnt\src\dictionaries\dict_en.json";
            }
        }

        private void InitializeComponent()
        {
            this.Text = "PPTX Manufacturing Instruction Translator";
            this.Size = new Size(860, 640);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.BackColor = Color.FromArgb(245, 246, 248);
            this.Font = new Font("Segoe UI", 9F, FontStyle.Regular);

            // Title
            lblTitle = new Label();
            lblTitle.Text = "PPTX Manufacturing Instruction Translator";
            lblTitle.Font = new Font("Segoe UI", 14F, FontStyle.Bold);
            lblTitle.ForeColor = Color.FromArgb(33, 37, 41);
            lblTitle.Location = new Point(20, 15);
            lblTitle.Size = new Size(600, 30);
            this.Controls.Add(lblTitle);

            // Folder Group
            grpFolder = new GroupBox();
            grpFolder.Text = " Папка с файлами инструкций (.pptx) ";
            grpFolder.Location = new Point(20, 50);
            grpFolder.Size = new Size(800, 75);
            this.Controls.Add(grpFolder);

            txtPath = new TextBox();
            txtPath.Text = Directory.Exists(defaultWorkDir) ? defaultWorkDir : AppDomain.CurrentDomain.BaseDirectory;
            txtPath.Location = new Point(15, 30);
            txtPath.Size = new Size(650, 25);
            grpFolder.Controls.Add(txtPath);

            btnBrowse = new Button();
            btnBrowse.Text = "Обзор...";
            btnBrowse.Location = new Point(675, 28);
            btnBrowse.Size = new Size(110, 28);
            btnBrowse.BackColor = Color.FromArgb(230, 235, 245);
            btnBrowse.Click += (s, e) => {
                using (FolderBrowserDialog fbd = new FolderBrowserDialog())
                {
                    fbd.SelectedPath = txtPath.Text;
                    if (fbd.ShowDialog() == DialogResult.OK)
                    {
                        txtPath.Text = fbd.SelectedPath;
                    }
                }
            };
            grpFolder.Controls.Add(btnBrowse);

            // Options Group
            grpOptions = new GroupBox();
            grpOptions.Text = " Параметры перевода и целевые языки ";
            grpOptions.Location = new Point(20, 135);
            grpOptions.Size = new Size(800, 70);
            this.Controls.Add(grpOptions);

            chkUA = new CheckBox();
            chkUA.Text = "Украинский перевод (UA) -> папка translated_UA";
            chkUA.Checked = true;
            chkUA.Location = new Point(20, 25);
            chkUA.Size = new Size(350, 25);
            grpOptions.Controls.Add(chkUA);

            chkEN = new CheckBox();
            chkEN.Text = "Английский перевод (EN) -> папка translated_EN";
            chkEN.Checked = true;
            chkEN.Location = new Point(400, 25);
            chkEN.Size = new Size(350, 25);
            grpOptions.Controls.Add(chkEN);

            // Start Button
            btnStart = new Button();
            btnStart.Text = "▶ ЗАПУСТИТЬ ПЕРЕВОД";
            btnStart.Location = new Point(20, 215);
            btnStart.Size = new Size(800, 42);
            btnStart.BackColor = Color.FromArgb(0, 120, 215);
            btnStart.ForeColor = Color.White;
            btnStart.Font = new Font("Segoe UI", 11F, FontStyle.Bold);
            btnStart.FlatStyle = FlatStyle.Flat;
            btnStart.Click += BtnStart_Click;
            this.Controls.Add(btnStart);

            // Progress Bar
            progressBar = new ProgressBar();
            progressBar.Location = new Point(20, 262);
            progressBar.Size = new Size(800, 10);
            progressBar.Style = ProgressBarStyle.Continuous;
            this.Controls.Add(progressBar);

            // Log Group
            grpLog = new GroupBox();
            grpLog.Text = " Лог выполнения процесса ";
            grpLog.Location = new Point(20, 280);
            grpLog.Size = new Size(800, 300);
            this.Controls.Add(grpLog);

            txtLog = new TextBox();
            txtLog.Multiline = true;
            txtLog.ScrollBars = ScrollBars.Vertical;
            txtLog.ReadOnly = true;
            txtLog.BackColor = Color.FromArgb(30, 30, 30);
            txtLog.ForeColor = Color.FromArgb(220, 220, 220);
            txtLog.Font = new Font("Consolas", 9.5F);
            txtLog.Location = new Point(10, 20);
            txtLog.Size = new Size(780, 270);
            grpLog.Controls.Add(txtLog);
        }

        private void AppendLog(string message)
        {
            if (this.InvokeRequired)
            {
                this.Invoke(new Action<string>(AppendLog), message);
                return;
            }
            txtLog.AppendText(message + "\r\n");
            txtLog.SelectionStart = txtLog.TextLength;
            txtLog.ScrollToCaret();
        }

        private void SetProgress(int value, int max)
        {
            if (this.InvokeRequired)
            {
                this.Invoke(new Action<int, int>(SetProgress), value, max);
                return;
            }
            progressBar.Maximum = max;
            progressBar.Value = value;
        }

        private void SetUiState(bool running)
        {
            if (this.InvokeRequired)
            {
                this.Invoke(new Action<bool>(SetUiState), running);
                return;
            }
            btnStart.Enabled = !running;
            btnBrowse.Enabled = !running;
        }

        private void BtnStart_Click(object sender, EventArgs e)
        {
            string srcDir = txtPath.Text.Trim();
            if (!Directory.Exists(srcDir))
            {
                MessageBox.Show("Выбранная папка не существует!", "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            if (!chkUA.Checked && !chkEN.Checked)
            {
                MessageBox.Show("Выберите хотя бы один целевой язык!", "Предупреждение", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            SetUiState(true);
            txtLog.Clear();

            Thread worker = new Thread(() => {
                try
                {
                    RunBatchTranslation(srcDir, chkUA.Checked, chkEN.Checked);
                }
                catch (Exception ex)
                {
                    AppendLog("\r\n[ERROR] Ошибка выполнения: " + ex.Message);
                    MessageBox.Show("Произошла ошибка:\n" + ex.Message, "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
                finally
                {
                    SetUiState(false);
                }
            });
            worker.IsBackground = true;
            worker.Start();
        }

        private void RunBatchTranslation(string srcDir, bool doUA, bool doEN)
        {
            string[] files = Directory.GetFiles(srcDir, "*.pptx");
            List<string> validFiles = new List<string>();
            foreach (string f in files)
            {
                string name = Path.GetFileName(f);
                if (!name.StartsWith("~") && !name.StartsWith("translated_"))
                {
                    validFiles.Add(f);
                }
            }

            if (validFiles.Count == 0)
            {
                AppendLog("[!] В выбранной папке не найдено файлов .pptx!");
                return;
            }

            AppendLog("==================================================");
            AppendLog("НАЧАЛО ПАКЕТНОГО ПЕРЕВОДА ИНСТРУКЦИЙ");
            AppendLog(string.Format("Найдено файлов для обработки: {0}", validFiles.Count));
            AppendLog(string.Format("Рабочая папка: {0}\r\n", srcDir));

            DictionaryMaps uaMaps = LoadDictionary(dictUaPath);
            DictionaryMaps enMaps = LoadDictionary(dictEnPath);

            string uaDir = Path.Combine(srcDir, "translated_UA");
            string enDir = Path.Combine(srcDir, "translated_EN");

            if (doUA && !Directory.Exists(uaDir)) Directory.CreateDirectory(uaDir);
            if (doEN && !Directory.Exists(enDir)) Directory.CreateDirectory(enDir);

            SetProgress(0, validFiles.Count);

            Type pptType = Type.GetTypeFromProgID("PowerPoint.Application");
            if (pptType == null)
            {
                AppendLog("[ERROR] Microsoft PowerPoint не найден в системе!");
                return;
            }

            dynamic pptApp = Activator.CreateInstance(pptType);
            try
            {
                for (int i = 0; i < validFiles.Count; i++)
                {
                    string srcFile = validFiles[i];
                    string fileName = Path.GetFileName(srcFile);
                    string baseName = Path.GetFileNameWithoutExtension(srcFile);
                    string cleanBase = baseName.EndsWith(" PL") ? baseName.Substring(0, baseName.Length - 3).Trim() : baseName;

                    AppendLog(string.Format("[{0}/{1}] Обработка: {2}", i + 1, validFiles.Count, fileName));

                    if (doUA)
                    {
                        string uaName = cleanBase + " UA.pptx";
                        string uaTarget = Path.Combine(uaDir, uaName);
                        int count = TranslatePresentationFile(pptApp, srcFile, uaTarget, uaMaps);
                        AppendLog(string.Format("  -> [UA] Переведено блоков: {0} -> {1}", count, uaName));
                    }

                    if (doEN)
                    {
                        string enName = cleanBase + " EN.pptx";
                        string enTarget = Path.Combine(enDir, enName);
                        int count = TranslatePresentationFile(pptApp, srcFile, enTarget, enMaps);
                        AppendLog(string.Format("  -> [EN] Переведено блоков: {0} -> {1}", count, enName));
                    }

                    SetProgress(i + 1, validFiles.Count);
                }

                AppendLog("\r\n==================================================");
                AppendLog("ВСЕ ПРЕЗЕНТАЦИИ УСПЕШНО ПЕРЕВЕДЕНЫ И СОХРАНЕНЫ!");
                MessageBox.Show("Перевод всех презентаций успешно завершен!", "Готово", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            finally
            {
                try { pptApp.Quit(); } catch { }
            }
        }

        private int TranslatePresentationFile(dynamic pptApp, string srcFile, string targetFile, DictionaryMaps maps)
        {
            File.Copy(srcFile, targetFile, true);
            dynamic pres = pptApp.Presentations.Open(targetFile, 0, 0, 0); // ReadOnly=False, Untitled=False, WithWindow=False
            int count = 0;

            try
            {
                // Slide Master
                dynamic master = pres.SlideMaster;
                for (int i = 1; i <= master.Shapes.Count; i++)
                {
                    dynamic sh = master.Shapes.Item(i);
                    count += ProcessShapeRecursive(sh, maps);
                }

                // Slides
                for (int s = 1; s <= pres.Slides.Count; s++)
                {
                    dynamic slide = pres.Slides.Item(s);
                    for (int shIdx = 1; shIdx <= slide.Shapes.Count; shIdx++)
                    {
                        dynamic sh = slide.Shapes.Item(shIdx);
                        count += ProcessShapeRecursive(sh, maps);
                    }
                }

                pres.Save();
            }
            finally
            {
                pres.Close();
            }

            return count;
        }

        private int ProcessShapeRecursive(dynamic sh, DictionaryMaps maps)
        {
            int count = 0;
            try
            {
                int shapeType = (int)sh.Type;
                if (shapeType == 6) // msoGroup = 6
                {
                    for (int g = 1; g <= sh.GroupItems.Count; g++)
                    {
                        count += ProcessShapeRecursive(sh.GroupItems.Item(g), maps);
                    }
                }
                else
                {
                    // TextFrame
                    if (sh.HasTextFrame != 0 && sh.TextFrame.HasText != 0)
                    {
                        string t = sh.TextFrame.TextRange.Text;
                        string trans = maps.FindTranslation(t);
                        if (trans != null)
                        {
                            UpdateTextSafely(sh.TextFrame.TextRange, trans);
                            count++;
                        }
                    }

                    // Table
                    if (sh.HasTable != 0)
                    {
                        dynamic table = sh.Table;
                        for (int r = 1; r <= table.Rows.Count; r++)
                        {
                            for (int c = 1; c <= table.Columns.Count; c++)
                            {
                                dynamic cell = table.Cell(r, c);
                                if (cell.Shape.TextFrame.HasText != 0)
                                {
                                    string t = cell.Shape.TextFrame.TextRange.Text;
                                    string trans = maps.FindTranslation(t);
                                    if (trans != null)
                                    {
                                        UpdateTextSafely(cell.Shape.TextFrame.TextRange, trans);
                                        count++;
                                    }
                                }
                            }
                        }
                    }
                }
            }
            catch { }
            return count;
        }

        private void UpdateTextSafely(dynamic textRange, string newText)
        {
            try
            {
                if (textRange.Runs().Count > 0)
                {
                    dynamic firstRun = textRange.Runs(1);
                    string fontName = firstRun.Font.Name;
                    float fontSize = (float)firstRun.Font.Size;
                    int fontBold = (int)firstRun.Font.Bold;
                    int fontColor = (int)firstRun.Font.Color.RGB;

                    textRange.Text = newText;

                    textRange.Font.Name = fontName;
                    textRange.Font.Size = fontSize;
                    textRange.Font.Bold = fontBold;
                    textRange.Font.Color.RGB = fontColor;
                }
                else
                {
                    textRange.Text = newText;
                }
            }
            catch
            {
                try { textRange.Text = newText; } catch { }
            }
        }

        private DictionaryMaps LoadDictionary(string jsonPath)
        {
            DictionaryMaps maps = new DictionaryMaps();
            if (File.Exists(jsonPath))
            {
                string json = File.ReadAllText(jsonPath, Encoding.UTF8);
                JavaScriptSerializer js = new JavaScriptSerializer();
                Dictionary<string, object> dict = js.Deserialize<Dictionary<string, object>>(json);
                if (dict != null)
                {
                    foreach (KeyValuePair<string, object> kv in dict)
                    {
                        if (kv.Value != null)
                        {
                            maps.Add(kv.Key, kv.Value.ToString());
                        }
                    }
                }
            }
            return maps;
        }

        [STAThread]
        public static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new MainForm());
        }
    }

    public class DictionaryMaps
    {
        public Dictionary<string, string> DirectMap = new Dictionary<string, string>(StringComparer.Ordinal);
        public Dictionary<string, string> NormMap = new Dictionary<string, string>(StringComparer.Ordinal);

        public void Add(string key, string val)
        {
            DirectMap[key] = val;
            DirectMap[key.Trim()] = val;
            string n = NormalizeText(key);
            NormMap[n] = val;
        }

        public string FindTranslation(string rawText)
        {
            if (string.IsNullOrEmpty(rawText) || rawText.Trim().Length == 0) return null;
            if (DirectMap.ContainsKey(rawText)) return DirectMap[rawText];
            string trimmed = rawText.Trim();
            if (DirectMap.ContainsKey(trimmed)) return DirectMap[trimmed];
            string n = NormalizeText(rawText);
            if (NormMap.ContainsKey(n)) return NormMap[n];
            return null;
        }

        public static string NormalizeText(string text)
        {
            if (string.IsNullOrEmpty(text)) return "";
            string t = text.Replace('\u00a0', ' ').Replace('–', '-').Replace('—', '-');
            t = t.Replace('\r', ' ').Replace('\n', ' ');
            t = Regex.Replace(t, @"\s+", " ").Trim();
            return t;
        }
    }
}
