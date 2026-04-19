# HTML 简历模板参考（基于 Claude Design 方法论）

## 设计原则

基于 `designer` agent 的 Claude Design 方法论，所有模板遵循以下原则：

1. **反AI味**：禁止大面积渐变、emoji装饰、圆角容器+左边框强调色、SVG插画
2. **oklch 配色**：所有颜色用 oklch 色彩空间定义，确保视觉和谐
3. **现代CSS**：CSS Grid 布局、`text-wrap: pretty`、CSS 自定义属性管理设计 token
4. **排版驱动**：用字号、字重、间距建立视觉层次，不依赖颜色和装饰
5. **Tweaks 调参**：通过 CSS 变量暴露设计参数，支持实时调整
6. **反填充**：每个元素都必须"挣到"它的位置，留白优于填充

---

## 文件结构

```
{输出目录}/
├── {姓名}_简历.html           # 主HTML文件（默认现代简约风格）
└── templates/                  # 模板目录
    ├── resume_modern.html      # 现代简约
    ├── resume_classic.html     # 经典传统
    ├── resume_creative.html    # 创意设计
    └── resume_tech.html        # 科技暗黑
```

---

## 4种模板风格

| 模板 | 文件名 | 字体风格 | 主色调 | 适用场景 |
|------|--------|----------|--------|----------|
| 现代简约 | resume_modern.html | 无衬线 | oklch蓝 | 互联网、科技公司 |
| 经典传统 | resume_classic.html | 衬线 | 深炭+深蓝 | 国企、金融、政府 |
| 创意设计 | resume_creative.html | 几何无衬线 | 珊瑚色 | 设计、创意、广告 |
| 科技暗黑 | resume_tech.html | 等宽字体 | 终端绿 | 程序员、技术岗 |

---

## Tweaks CSS 变量系统

每个模板通过 CSS 自定义属性暴露设计参数，并提供浏览器内浮动面板实时调整。

### CSS 变量（设计 token）

```css
:root {
    /* 色彩系统 */
    --c-primary: oklch(0.45 0.15 260);
    --c-text: oklch(0.2 0 0);
    --c-text-secondary: oklch(0.45 0 0);
    --c-bg: oklch(1 0 0);
    --c-surface: oklch(0.97 0 0);
    --c-border: oklch(0.88 0 0);

    /* 排版 */
    --f-base: 14px;
    --f-lg: 18px;
    --f-xl: 24px;
    --f-2xl: 32px;

    /* 间距 */
    --s-1: 4px;
    --s-2: 8px;
    --s-3: 16px;
    --s-4: 24px;
    --s-5: 32px;
    --s-6: 48px;

    /* 布局 */
    --layout-width: 800px;
    --sidebar-width: 220px;
}
```

### 浮动 Tweaks 面板

每个模板的 HTML 包含一个右下角浮动面板，点击工具栏"Tweaks"按钮切换显示。

面板提供以下调整项：

| 调整项 | 控件类型 | 作用 |
|--------|----------|------|
| 主色 | `<input type="color">` | 修改 `--c-primary` CSS 变量 |
| 正文字号 | `<input type="range">` | 修改 `--f-base` CSS 变量 |
| 行距 | `<input type="range">` | 修改 body.lineHeight |
| 布局 | `<select>` | 切换双栏/单栏布局 |

面板默认隐藏（`display: none`），不干扰简历预览。打印时自动隐藏。

### EDITMODE 持久化标记

面板默认值用注释标记包裹，支持外部工具回写：

```javascript
const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
    "primaryColor": "oklch(0.45 0.15 260)",
    "fontSize": "13px",
    "lineHeight": "1.7",
    "layout": "sidebar"
}/*EDITMODE-END*/;
```

---

## 模板一：现代简约 (Modern)

### 设计特点
- 白底双栏布局（CSS Grid），左窄右宽
- 左栏：联系方式 + 技能，右栏：经历主体
- 纯排版驱动，无渐变、无装饰
- 字体：`"Noto Sans SC", "Source Han Sans SC", "Helvetica Neue", "PingFang SC", sans-serif`

### 完整模板代码

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{姓名}} - {{职位}} | 现代简约</title>
    <style>
        :root {
            --c-primary: oklch(0.45 0.15 260);
            --c-primary-light: oklch(0.92 0.05 260);
            --c-text: oklch(0.18 0.01 260);
            --c-text-secondary: oklch(0.5 0.01 260);
            --c-bg: oklch(1 0 0);
            --c-surface: oklch(0.97 0.005 260);
            --c-border: oklch(0.88 0.01 260);
            --f-base: 13px;
            --f-sm: 11px;
            --f-lg: 15px;
            --f-xl: 20px;
            --f-2xl: 28px;
            --s-3: 12px;
            --s-4: 20px;
            --s-5: 28px;
            --s-6: 40px;
            --sidebar-width: 220px;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: "Noto Sans SC", "Source Han Sans SC", "Helvetica Neue", "PingFang SC", sans-serif;
            font-size: var(--f-base);
            line-height: 1.7;
            color: var(--c-text);
            background: oklch(0.95 0 0);
            text-wrap: pretty;
        }

        /* 工具栏 */
        .toolbar {
            position: fixed;
            top: 16px;
            right: 16px;
            display: flex;
            gap: 8px;
            z-index: 1000;
        }

        .toolbar button {
            padding: 8px 16px;
            border: 1px solid var(--c-border);
            background: var(--c-bg);
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            font-family: inherit;
            color: var(--c-text-secondary);
            transition: all 0.15s;
        }

        .toolbar button:hover {
            background: var(--c-text);
            color: var(--c-bg);
        }

        .toolbar button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        /* 主容器 */
        .resume {
            max-width: 800px;
            margin: 24px auto;
            background: var(--c-bg);
            display: grid;
            grid-template-columns: var(--sidebar-width) 1fr;
            min-height: 100vh;
        }

        /* 左栏 */
        .sidebar {
            background: var(--c-surface);
            padding: var(--s-6) var(--s-4);
            border-right: 1px solid var(--c-border);
        }

        .sidebar-name {
            font-size: var(--f-xl);
            font-weight: 700;
            color: var(--c-primary);
            margin-bottom: 4px;
            letter-spacing: -0.02em;
        }

        .sidebar-title {
            font-size: var(--f-base);
            color: var(--c-text-secondary);
            margin-bottom: var(--s-5);
        }

        .sidebar-section {
            margin-bottom: var(--s-5);
        }

        .sidebar-label {
            font-size: var(--f-sm);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--c-primary);
            margin-bottom: var(--s-2);
        }

        .sidebar-list {
            list-style: none;
            font-size: var(--f-sm);
        }

        .sidebar-list li {
            padding: 3px 0;
            color: var(--c-text-secondary);
        }

        .sidebar-list li::before {
            content: "";
        }

        .contact-list {
            list-style: none;
            font-size: var(--f-sm);
        }

        .contact-list li {
            padding: 3px 0;
            color: var(--c-text-secondary);
            word-break: break-all;
        }

        /* 右栏 */
        .main {
            padding: var(--s-6) var(--s-5);
        }

        .section {
            margin-bottom: var(--s-6);
        }

        .section-title {
            font-size: var(--f-lg);
            font-weight: 700;
            color: var(--c-text);
            padding-bottom: var(--s-2);
            border-bottom: 2px solid var(--c-primary);
            margin-bottom: var(--s-4);
            letter-spacing: -0.01em;
        }

        .entry {
            margin-bottom: var(--s-5);
        }

        .entry-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: var(--s-2);
        }

        .entry-title {
            font-size: var(--f-lg);
            font-weight: 600;
            color: var(--c-text);
        }

        .entry-subtitle {
            font-size: var(--f-base);
            color: var(--c-text-secondary);
        }

        .entry-time {
            font-size: var(--f-sm);
            color: var(--c-text-secondary);
            white-space: nowrap;
        }

        .entry-content {
            font-size: var(--f-base);
            color: var(--c-text-secondary);
        }

        .entry-content ul {
            padding-left: 16px;
        }

        .entry-content li {
            margin-bottom: 4px;
        }

        .entry-content strong {
            color: var(--c-text);
            font-weight: 600;
        }

        .highlight {
            color: var(--c-primary);
            font-weight: 600;
        }

        .skill-tag {
            display: inline-block;
            font-size: var(--f-sm);
            padding: 2px 8px;
            margin: 2px 4px 2px 0;
            background: var(--c-surface);
            border: 1px solid var(--c-border);
            color: var(--c-text-secondary);
        }

        /* 模板弹窗 */
        .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: oklch(0 0 0 / 0.4);
            z-index: 2000;
            justify-content: center;
            align-items: center;
        }

        .modal-overlay.active { display: flex; }

        .modal {
            background: var(--c-bg);
            padding: var(--s-5);
            max-width: 480px;
            width: 90%;
        }

        .modal h3 {
            font-size: var(--f-lg);
            font-weight: 600;
            margin-bottom: var(--s-4);
            text-align: center;
        }

        .template-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        .template-option {
            padding: var(--s-3);
            border: 1px solid var(--c-border);
            cursor: pointer;
            text-align: center;
            transition: all 0.15s;
        }

        .template-option:hover,
        .template-option.active {
            border-color: var(--c-primary);
        }

        .template-option.active {
            background: var(--c-primary-light);
        }

        .template-option .t-name {
            font-size: var(--f-base);
            font-weight: 600;
            color: var(--c-text);
        }

        .template-option .t-desc {
            font-size: var(--f-sm);
            color: var(--c-text-secondary);
            margin-top: 4px;
        }

        .modal-close {
            display: block;
            width: 100%;
            margin-top: var(--s-4);
            padding: 10px;
            background: var(--c-text);
            color: var(--c-bg);
            border: none;
            cursor: pointer;
            font-size: var(--f-base);
            font-family: inherit;
        }

        /* Tweaks 面板 */
        .tweaks-panel {
            display: none;
            position: fixed;
            bottom: 16px;
            right: 16px;
            width: 240px;
            background: var(--c-bg);
            border: 1px solid var(--c-border);
            padding: 16px;
            z-index: 1500;
            font-size: 12px;
        }

        .tweaks-panel.visible { display: block; }

        .tweaks-panel h4 {
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--c-text-secondary);
            margin-bottom: 12px;
        }

        .tweak-row {
            margin-bottom: 10px;
        }

        .tweak-row label {
            display: block;
            font-size: 11px;
            color: var(--c-text-secondary);
            margin-bottom: 3px;
        }

        .tweak-row input[type="color"] {
            width: 100%;
            height: 28px;
            border: 1px solid var(--c-border);
            background: var(--c-bg);
            cursor: pointer;
            padding: 2px;
        }

        .tweak-row input[type="range"] {
            width: 100%;
            cursor: pointer;
        }

        .tweak-row select {
            width: 100%;
            padding: 4px;
            border: 1px solid var(--c-border);
            background: var(--c-bg);
            font-family: inherit;
            font-size: 12px;
        }

        /* 打印 */
        @media print {
            * {
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            .toolbar, .modal-overlay, .tweaks-panel { display: none !important; }
            body { background: white; }
            .resume {
                margin: 0;
                box-shadow: none;
                max-width: 100%;
            }
            .entry, .section {
                break-inside: avoid;
                page-break-inside: avoid;
            }
            .section-title {
                break-after: avoid;
                page-break-after: avoid;
            }
            @page { size: A4; margin: 10mm 8mm; }
        }

        /* 响应式 */
        @media (max-width: 700px) {
            .resume {
                grid-template-columns: 1fr;
                margin: 0;
            }
            .sidebar {
                border-right: none;
                border-bottom: 1px solid var(--c-border);
                padding: var(--s-4);
            }
            .main { padding: var(--s-4); }
            .toolbar { top: 8px; right: 8px; flex-wrap: wrap; }
            .toolbar button { padding: 6px 10px; font-size: 11px; }
            .tweaks-panel { width: 200px; bottom: 8px; right: 8px; }
        }
    </style>
</head>
<body>
    <div class="toolbar">
        <button onclick="openModal()">切换模板</button>
        <button onclick="exportPDF()">导出 PDF</button>
        <button onclick="exportPNG()">导出 PNG</button>
        <button onclick="toggleTweaks()">Tweaks</button>
    </div>

    <!-- Tweaks 浮动面板 -->
    <div class="tweaks-panel" id="tweaksPanel">
        <h4>Tweaks</h4>
        <div class="tweak-row">
            <label>主色</label>
            <input type="color" id="tweakPrimary" onchange="applyTweak('--c-primary', this.value)">
        </div>
        <div class="tweak-row">
            <label>正文字号</label>
            <input type="range" id="tweakFontSize" min="11" max="16" value="13" onchange="applyTweak('--f-base', this.value + 'px')">
        </div>
        <div class="tweak-row">
            <label>行距</label>
            <input type="range" id="tweakLineHeight" min="14" max="22" value="17" step="1" onchange="document.body.style.lineHeight = (this.value / 10).toFixed(1)">
        </div>
        <div class="tweak-row">
            <label>布局</label>
            <select id="tweakLayout" onchange="switchLayout(this.value)">
                <option value="sidebar">双栏（侧边栏）</option>
                <option value="single">单栏</option>
            </select>
        </div>
    </div>

    <div class="modal-overlay" id="templateModal">
        <div class="modal">
            <h3>选择模板风格</h3>
            <div class="template-grid">
                <div class="template-option active" onclick="selectTemplate('modern')">
                    <div class="t-name">现代简约</div>
                    <div class="t-desc">双栏布局 / 适合互联网</div>
                </div>
                <div class="template-option" onclick="selectTemplate('classic')">
                    <div class="t-name">经典传统</div>
                    <div class="t-desc">衬线字体 / 适合国企金融</div>
                </div>
                <div class="template-option" onclick="selectTemplate('creative')">
                    <div class="t-name">创意设计</div>
                    <div class="t-desc">非对称排版 / 适合设计岗</div>
                </div>
                <div class="template-option" onclick="selectTemplate('tech')">
                    <div class="t-name">科技暗黑</div>
                    <div class="t-desc">等宽字体 / 适合程序员</div>
                </div>
            </div>
            <button class="modal-close" onclick="closeModal()">关闭</button>
        </div>
    </div>

    <div class="resume" id="resumeContainer">
        <aside class="sidebar">
            <div class="sidebar-name">{{姓名}}</div>
            <div class="sidebar-title">{{职位}} | {{工作年限}}年经验</div>

            <div class="sidebar-section">
                <div class="sidebar-label">联系方式</div>
                <ul class="contact-list">
                    <li>{{手机}}</li>
                    <li>{{邮箱}}</li>
                    <li>{{城市}}</li>
                </ul>
            </div>

            <div class="sidebar-section">
                <div class="sidebar-label">专业技能</div>
                {{#each 技能分组}}
                <div style="margin-bottom: 8px;">
                    <div style="font-size: var(--f-sm); font-weight: 600; color: var(--c-text);">{{类别名}}</div>
                    <div>{{#each 技能列表}}<span class="skill-tag">{{技能名}}</span>{{/each}}</div>
                </div>
                {{/each}}
            </div>
        </aside>

        <main class="main">
            <section class="section">
                <h2 class="section-title">工作经历</h2>
                {{#each 工作经历}}
                <div class="entry">
                    <div class="entry-header">
                        <div>
                            <span class="entry-title">{{公司名称}}</span>
                            <span class="entry-subtitle"> / {{职位}}</span>
                        </div>
                        <span class="entry-time">{{时间}}</span>
                    </div>
                    <div class="entry-content">
                        <ul>
                            {{#each 工作内容}}
                            <li>{{{this}}}</li>
                            {{/each}}
                        </ul>
                    </div>
                </div>
                {{/each}}
            </section>

            <section class="section">
                <h2 class="section-title">项目经历</h2>
                {{#each 项目经历}}
                <div class="entry">
                    <div class="entry-header">
                        <div>
                            <span class="entry-title">{{项目名称}}</span>
                            <span class="entry-subtitle"> / {{角色}}</span>
                        </div>
                        <span class="entry-time">{{时间}}</span>
                    </div>
                    <div class="entry-content">
                        <p style="margin-bottom: 6px;"><strong>背景：</strong>{{背景描述}}</p>
                        <ul>
                            {{#each 核心工作}}
                            <li>{{{this}}}</li>
                            {{/each}}
                        </ul>
                        <p style="margin-top: 6px;"><span class="highlight">成果：</span>{{量化成果}}</p>
                    </div>
                </div>
                {{/each}}
            </section>

            <section class="section">
                <h2 class="section-title">教育背景</h2>
                {{#each 教育背景}}
                <div class="entry">
                    <div class="entry-header">
                        <div>
                            <span class="entry-title">{{学校}}</span>
                            <span class="entry-subtitle"> / {{专业}} / {{学历}}</span>
                        </div>
                        <span class="entry-time">{{时间}}</span>
                    </div>
                </div>
                {{/each}}
            </section>
        </main>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
    <script>
        const templates = {
            modern: './templates/resume_modern.html',
            classic: './templates/resume_classic.html',
            creative: './templates/resume_creative.html',
            tech: './templates/resume_tech.html'
        };

        function openModal() {
            document.getElementById('templateModal').classList.add('active');
        }

        function closeModal() {
            document.getElementById('templateModal').classList.remove('active');
        }

        function selectTemplate(name) {
            if (templates[name]) {
                window.location.href = templates[name];
            }
        }

        function replaceOklchColors(doc) {
            var c = document.createElement('canvas'); c.width = c.height = 1;
            var ctx = c.getContext('2d');
            function convert(s) {
                try {
                    ctx.clearRect(0,0,1,1); ctx.fillStyle = '#000'; ctx.fillStyle = s; ctx.fillRect(0,0,1,1);
                    var d = ctx.getImageData(0,0,1,1).data;
                    if (d[3] === 0) return s;
                    if (d[3] < 255) return 'rgba(' + d[0] + ',' + d[1] + ',' + d[2] + ',' + (d[3]/255).toFixed(2) + ')';
                    return 'rgb(' + d[0] + ',' + d[1] + ',' + d[2] + ')';
                } catch(e) { return s; }
            }
            doc.querySelectorAll('style').forEach(function(s) {
                s.textContent = s.textContent.replace(/oklch\([^)]+\)/g, convert);
            });
            var rs = doc.documentElement.getAttribute('style');
            if (rs) doc.documentElement.setAttribute('style', rs.replace(/oklch\([^)]+\)/g, convert));
        }

        async function exportPDF() {
            const btn = event.target;
            const originalText = btn.textContent;
            btn.textContent = '生成中...';
            btn.disabled = true;

            const toolbar = document.querySelector('.toolbar');
            toolbar.style.display = 'none';

            try {
                const container = document.getElementById('resumeContainer');
                const canvas = await html2canvas(container, {
                    scale: 2,
                    useCORS: true,
                    backgroundColor: '#ffffff',
                    logging: false,
                    allowTaint: true,
                    foreignObjectRendering: false,
                    onclone: function(clonedDoc) { replaceOklchColors(clonedDoc); }
                });

                const { jsPDF } = window.jspdf;
                const pdfWidth = 210;
                const pdfHeight = 297;
                const imgWidth = canvas.width;
                const imgHeight = canvas.height;
                const ratio = (pdfWidth - 24) / (imgWidth / 2);
                const scaledWidth = pdfWidth - 24;
                const scaledHeight = (imgHeight / 2) * ratio;

                const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

                if (scaledHeight > pdfHeight - 24) {
                    const pageHeight = pdfHeight - 24;
                    let position = 0;
                    let remainingHeight = scaledHeight;

                    while (remainingHeight > 0) {
                        if (position > 0) pdf.addPage();
                        const sourceY = position * (imgHeight / scaledHeight);
                        const sourceHeight = Math.min(pageHeight, remainingHeight) * (imgHeight / scaledHeight);
                        const pageCanvas = document.createElement('canvas');
                        pageCanvas.width = imgWidth;
                        pageCanvas.height = sourceHeight;
                        const ctx = pageCanvas.getContext('2d');
                        ctx.drawImage(canvas, 0, sourceY, imgWidth, sourceHeight, 0, 0, imgWidth, sourceHeight);
                        const pageImgData = pageCanvas.toDataURL('image/png');
                        const pageScaledHeight = Math.min(pageHeight, remainingHeight);
                        pdf.addImage(pageImgData, 'PNG', 12, 12, scaledWidth, pageScaledHeight);
                        position += pageHeight;
                        remainingHeight -= pageHeight;
                    }
                } else {
                    const imgData = canvas.toDataURL('image/png');
                    pdf.addImage(imgData, 'PNG', 12, 12, scaledWidth, scaledHeight);
                }

                pdf.save(`{{姓名}}_简历_${new Date().toISOString().slice(0,10)}.pdf`);
                btn.textContent = '已保存';
                setTimeout(() => { btn.textContent = originalText; }, 2000);
            } catch (error) {
                console.error('PDF导出失败:', error);
                alert('导出失败: ' + error.message);
                btn.textContent = originalText;
            }

            toolbar.style.display = 'flex';
            btn.disabled = false;
        }

        async function exportPNG() {
            const btn = event.target;
            const originalText = btn.textContent;
            btn.textContent = '生成中...';
            btn.disabled = true;

            document.querySelector('.toolbar').style.display = 'none';

            try {
                const container = document.getElementById('resumeContainer');
                const canvas = await html2canvas(container, {
                    scale: 2,
                    useCORS: true,
                    backgroundColor: '#ffffff',
                    logging: false,
                    allowTaint: true,
                    onclone: function(clonedDoc) { replaceOklchColors(clonedDoc); }
                });

                const link = document.createElement('a');
                link.download = `{{姓名}}_简历_${new Date().toISOString().slice(0,10)}.png`;
                link.href = canvas.toDataURL('image/png');
                link.click();

                btn.textContent = '已保存';
                setTimeout(() => { btn.textContent = originalText; }, 2000);
            } catch (error) {
                console.error('PNG导出失败:', error);
                btn.textContent = originalText;
            }

            document.querySelector('.toolbar').style.display = 'flex';
            btn.disabled = false;
        }

        document.getElementById('templateModal').addEventListener('click', function(e) {
            if (e.target === this) closeModal();
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') closeModal();
        });

        // ===== Tweaks 面板逻辑 =====

        const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
            "primaryColor": "oklch(0.45 0.15 260)",
            "fontSize": "13px",
            "lineHeight": "1.7",
            "layout": "sidebar"
        }/*EDITMODE-END*/;

        function toggleTweaks() {
            const panel = document.getElementById('tweaksPanel');
            panel.classList.toggle('visible');
        }

        function applyTweak(cssVar, value) {
            document.documentElement.style.setProperty(cssVar, value);

            // 如果改了主色，同步派生色
            if (cssVar === '--c-primary') {
                document.documentElement.style.setProperty('--c-primary-light', value.replace(/oklch\(([^)]+)\)/, (m, l, c, h) => {
                    return `oklch(0.92 0.05 ${h || '260'})`;
                }));
            }
        }

        function switchLayout(mode) {
            const resume = document.getElementById('resumeContainer');
            if (!resume) return;
            const sidebar = resume.querySelector('.sidebar');
            const main = resume.querySelector('.main');

            if (mode === 'single') {
                resume.style.gridTemplateColumns = '1fr';
                if (sidebar) {
                    sidebar.style.borderRight = 'none';
                    sidebar.style.borderBottom = '1px solid var(--c-border)';
                }
            } else {
                resume.style.gridTemplateColumns = 'var(--sidebar-width) 1fr';
                if (sidebar) {
                    sidebar.style.borderRight = '1px solid var(--c-border)';
                    sidebar.style.borderBottom = 'none';
                }
            }
        }
    </script>
</body>
</html>
```

---

## 模板二：经典传统 (Classic)

### 设计特点
- 传统单栏布局，横线分隔
- 衬线字体，正式感
- 米白底色，深炭文字
- 字体：`"Noto Serif SC", "Source Han Serif SC", Georgia, "Times New Roman", serif`

### 样式差异（仅列出与 Modern 不同的 CSS）

```css
:root {
    --c-primary: oklch(0.3 0.08 250);
    --c-text: oklch(0.2 0.01 60);
    --c-text-secondary: oklch(0.45 0.01 60);
    --c-bg: oklch(0.98 0.005 80);
    --c-surface: oklch(0.96 0.005 80);
    --c-border: oklch(0.82 0.01 80);
    --c-accent: oklch(0.35 0.06 250);
}

body {
    font-family: "Noto Serif SC", "Source Han Serif SC", Georgia, "Times New Roman", serif;
    background: oklch(0.93 0.005 80);
}

/* 单栏布局 */
.resume {
    max-width: 700px;
    display: block;
    padding: var(--s-6);
}

/* 头部 - 名字居中 */
.header {
    text-align: center;
    margin-bottom: var(--s-5);
    padding-bottom: var(--s-4);
    border-bottom: 1px solid var(--c-text);
}

.header-name {
    font-size: var(--f-2xl);
    font-weight: 700;
    letter-spacing: 0.15em;
    color: var(--c-text);
}

.header-contact {
    font-size: var(--f-sm);
    color: var(--c-text-secondary);
    margin-top: var(--s-2);
}

/* 分隔线用细横线 */
.section-title {
    font-size: var(--f-lg);
    font-weight: 700;
    border-bottom: 1px solid var(--c-border);
    padding-bottom: var(--s-1);
    margin-bottom: var(--s-4);
    letter-spacing: 0.05em;
}

.entry-header {
    border-bottom: none;
}

.entry-title {
    font-size: var(--f-base);
    font-weight: 700;
}
```

### HTML 结构差异

Classic 使用单栏布局，结构如下：

```html
<div class="resume" id="resumeContainer">
    <header class="header">
        <h1 class="header-name">{{姓名}}</h1>
        <p class="header-contact">{{职位}} | {{手机}} | {{邮箱}} | {{城市}}</p>
    </header>

    <section class="section">
        <h2 class="section-title">工作经历</h2>
        <!-- entries... -->
    </section>

    <section class="section">
        <h2 class="section-title">项目经历</h2>
        <!-- entries... -->
    </section>

    <section class="section">
        <h2 class="section-title">专业技能</h2>
        <!-- skills... -->
    </section>

    <section class="section">
        <h2 class="section-title">教育背景</h2>
        <!-- education... -->
    </section>
</div>
```

---

## 模板三：创意设计 (Creative)

### 设计特点
- 非对称布局，强烈的字号和字重对比
- 大面积留白，关键元素用大字号突出
- 珊瑚色强调，大胆的排版节奏
- 字体：`"Noto Sans SC", "Helvetica Neue", "PingFang SC", -apple-system, sans-serif`（极粗+极细对比）

### 样式差异

```css
:root {
    --c-primary: oklch(0.55 0.18 25);
    --c-text: oklch(0.15 0 0);
    --c-text-secondary: oklch(0.5 0 0);
    --c-bg: oklch(1 0 0);
    --c-border: oklch(0.9 0 0);
    --f-2xl: 36px;
    --f-xl: 24px;
    --f-lg: 15px;
    --f-base: 13px;
}

body {
    font-family: "Noto Sans SC", "Helvetica Neue", "PingFang SC", -apple-system, sans-serif;
}

/* 非对称布局：左侧大名字 + 右侧内容 */
.resume {
    display: grid;
    grid-template-columns: 280px 1fr;
    gap: 0;
}

/* 左栏 - 大号名字 + 联系方式 */
.sidebar {
    padding: 48px 32px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.sidebar-name {
    font-size: 48px;
    font-weight: 900;
    line-height: 1.1;
    letter-spacing: -0.03em;
    color: var(--c-text);
}

.sidebar-title {
    font-size: var(--f-lg);
    font-weight: 300;
    color: var(--c-primary);
    margin-top: 8px;
    letter-spacing: 0.1em;
}

/* 分隔线用颜色块 */
.section-title {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--c-primary);
    padding: 8px 16px;
    background: oklch(0.55 0.18 25 / 0.08);
    display: inline-block;
    margin-bottom: 24px;
}

/* 大号年份时间标记 */
.entry-time {
    font-size: 28px;
    font-weight: 900;
    color: oklch(0.92 0 0);
    letter-spacing: -0.02em;
    position: absolute;
    right: 0;
    top: -8px;
}

.entry {
    position: relative;
}
```

---

## 模板四：科技暗黑 (Tech)

### 设计特点
- 深色背景，终端/IDE视觉语言
- 等宽字体，代码风格排版
- 终端绿/青色强调，高对比度
- 字体：`"JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", monospace`

### 完整样式

```css
:root {
    --c-primary: oklch(0.72 0.19 155);
    --c-text: oklch(0.88 0.005 260);
    --c-text-secondary: oklch(0.6 0.01 260);
    --c-bg: oklch(0.15 0.01 260);
    --c-surface: oklch(0.2 0.01 260);
    --c-border: oklch(0.3 0.01 260);
    --c-accent: oklch(0.72 0.15 195);
}

body {
    font-family: "JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", monospace;
    background: oklch(0.1 0 0);
    font-size: 13px;
}

.resume {
    background: var(--c-bg);
}

/* 顶部 - 仿终端标题栏 */
.terminal-bar {
    background: var(--c-surface);
    padding: 8px 16px;
    border-bottom: 1px solid var(--c-border);
    display: flex;
    gap: 8px;
    align-items: center;
}

.terminal-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
}

.terminal-dot.red { background: oklch(0.65 0.2 25); }
.terminal-dot.yellow { background: oklch(0.75 0.17 90); }
.terminal-dot.green { background: oklch(0.72 0.19 155); }

.terminal-title {
    font-size: 11px;
    color: var(--c-text-secondary);
    margin-left: 8px;
}

/* 名字用 > 符号模拟命令行 */
.header-name {
    font-size: 24px;
    color: var(--c-primary);
    margin-bottom: 4px;
}

.header-name::before {
    content: "> ";
    color: var(--c-text-secondary);
}

/* section标题用 // 注释风格 */
.section-title::before {
    content: "// ";
    color: var(--c-text-secondary);
}

.section-title {
    color: var(--c-primary);
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--c-border);
}

/* 强调色用于关键词 */
.highlight {
    color: var(--c-primary);
}

/* 代码标签风格的技能展示 */
.skill-tag {
    background: var(--c-surface);
    border: 1px solid var(--c-border);
    color: var(--c-primary);
    font-size: 11px;
    padding: 2px 8px;
    display: inline-block;
    margin: 2px;
}

/* 工具栏适配深色 */
.toolbar button {
    background: var(--c-surface);
    color: var(--c-text);
    border-color: var(--c-border);
}

.toolbar button:hover {
    background: var(--c-primary);
    color: var(--c-bg);
}

/* 打印时改为白色背景 */
@media print {
    :root {
        --c-bg: oklch(1 0 0);
        --c-surface: oklch(0.97 0 0);
        --c-border: oklch(0.85 0 0);
        --c-text: oklch(0.15 0 0);
        --c-text-secondary: oklch(0.45 0 0);
        --c-primary: oklch(0.35 0.15 155);
    }
}
```

---

## 模板选择弹窗（统一）

所有模板使用相同的弹窗结构，无emoji，纯文字描述：

```html
<div class="modal-overlay" id="templateModal">
    <div class="modal">
        <h3>选择模板风格</h3>
        <div class="template-grid">
            <div class="template-option active" onclick="selectTemplate('modern')">
                <div class="t-name">现代简约</div>
                <div class="t-desc">双栏布局 / 适合互联网</div>
            </div>
            <div class="template-option" onclick="selectTemplate('classic')">
                <div class="t-name">经典传统</div>
                <div class="t-desc">衬线字体 / 适合国企金融</div>
            </div>
            <div class="template-option" onclick="selectTemplate('creative')">
                <div class="t-name">创意设计</div>
                <div class="t-desc">非对称排版 / 适合设计岗</div>
            </div>
            <div class="template-option" onclick="selectTemplate('tech')">
                <div class="t-name">科技暗黑</div>
                <div class="t-desc">等宽字体 / 适合程序员</div>
            </div>
        </div>
        <button class="modal-close" onclick="closeModal()">关闭</button>
    </div>
</div>
```

---

## JavaScript 代码（通用）

所有模板共享以下 JavaScript：

```javascript
const templates = {
    modern: './templates/resume_modern.html',
    classic: './templates/resume_classic.html',
    creative: './templates/resume_creative.html',
    tech: './templates/resume_tech.html'
};

function openModal() {
    document.getElementById('templateModal').classList.add('active');
}

function closeModal() {
    document.getElementById('templateModal').classList.remove('active');
}

function selectTemplate(name) {
    if (templates[name]) {
        window.location.href = templates[name];
    }
}

// html2canvas 不支持 oklch，导出前在克隆文档中转换为 rgb
function replaceOklchColors(doc) {
    var c = document.createElement('canvas'); c.width = c.height = 1;
    var ctx = c.getContext('2d');
    function convert(s) {
        try {
            ctx.clearRect(0,0,1,1); ctx.fillStyle = '#000'; ctx.fillStyle = s; ctx.fillRect(0,0,1,1);
            var d = ctx.getImageData(0,0,1,1).data;
            if (d[3] === 0) return s;
            if (d[3] < 255) return 'rgba(' + d[0] + ',' + d[1] + ',' + d[2] + ',' + (d[3]/255).toFixed(2) + ')';
            return 'rgb(' + d[0] + ',' + d[1] + ',' + d[2] + ')';
        } catch(e) { return s; }
    }
    doc.querySelectorAll('style').forEach(function(s) {
        s.textContent = s.textContent.replace(/oklch\([^)]+\)/g, convert);
    });
    var rs = doc.documentElement.getAttribute('style');
    if (rs) doc.documentElement.setAttribute('style', rs.replace(/oklch\([^)]+\)/g, convert));
}

async function exportPDF() {
    const btn = event.target;
    const originalText = btn.textContent;
    btn.textContent = '生成中...';
    btn.disabled = true;

    const toolbar = document.querySelector('.toolbar');
    toolbar.style.display = 'none';

    try {
        const container = document.getElementById('resumeContainer');
        const canvas = await html2canvas(container, {
            scale: 2,
            useCORS: true,
            backgroundColor: '#ffffff',
            logging: false,
            allowTaint: true,
            foreignObjectRendering: false,
            onclone: function(clonedDoc) {
                replaceOklchColors(clonedDoc);
                const cloned = clonedDoc.getElementById('resumeContainer');
                if (cloned) cloned.style.transform = 'none';
            }
        });

        const { jsPDF } = window.jspdf;
        const pdfWidth = 210;
        const pdfHeight = 297;
        const imgWidth = canvas.width;
        const imgHeight = canvas.height;
        const ratio = (pdfWidth - 24) / (imgWidth / 2);
        const scaledWidth = pdfWidth - 24;
        const scaledHeight = (imgHeight / 2) * ratio;

        const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

        if (scaledHeight > pdfHeight - 24) {
            const pageHeight = pdfHeight - 24;
            let position = 0;
            let remainingHeight = scaledHeight;

            while (remainingHeight > 0) {
                if (position > 0) pdf.addPage();
                const sourceY = position * (imgHeight / scaledHeight);
                const sourceHeight = Math.min(pageHeight, remainingHeight) * (imgHeight / scaledHeight);
                const pageCanvas = document.createElement('canvas');
                pageCanvas.width = imgWidth;
                pageCanvas.height = sourceHeight;
                const ctx = pageCanvas.getContext('2d');
                ctx.drawImage(canvas, 0, sourceY, imgWidth, sourceHeight, 0, 0, imgWidth, sourceHeight);
                const pageImgData = pageCanvas.toDataURL('image/png');
                const pageScaledHeight = Math.min(pageHeight, remainingHeight);
                pdf.addImage(pageImgData, 'PNG', 12, 12, scaledWidth, pageScaledHeight);
                position += pageHeight;
                remainingHeight -= pageHeight;
            }
        } else {
            const imgData = canvas.toDataURL('image/png');
            pdf.addImage(imgData, 'PNG', 12, 12, scaledWidth, scaledHeight);
        }

        pdf.save(`{{姓名}}_简历_${new Date().toISOString().slice(0,10)}.pdf`);
        btn.textContent = '已保存';
        setTimeout(() => { btn.textContent = originalText; }, 2000);
    } catch (error) {
        console.error('PDF导出失败:', error);
        alert('导出失败: ' + error.message);
        btn.textContent = originalText;
    }

    toolbar.style.display = 'flex';
    btn.disabled = false;
}

async function exportPNG() {
    const btn = event.target;
    const originalText = btn.textContent;
    btn.textContent = '生成中...';
    btn.disabled = true;

    document.querySelector('.toolbar').style.display = 'none';

    try {
        const container = document.getElementById('resumeContainer');
        const canvas = await html2canvas(container, {
            scale: 2,
            useCORS: true,
            backgroundColor: '#ffffff',
            logging: false,
            allowTaint: true,
            onclone: function(clonedDoc) { replaceOklchColors(clonedDoc); }
        });

        const link = document.createElement('a');
        link.download = `{{姓名}}_简历_${new Date().toISOString().slice(0,10)}.png`;
        link.href = canvas.toDataURL('image/png');
        link.click();

        btn.textContent = '已保存';
        setTimeout(() => { btn.textContent = originalText; }, 2000);
    } catch (error) {
        console.error('PNG导出失败:', error);
        btn.textContent = originalText;
    }

    document.querySelector('.toolbar').style.display = 'flex';
    btn.disabled = false;
}

document.getElementById('templateModal').addEventListener('click', function(e) {
    if (e.target === this) closeModal();
});

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeModal();
});
```

---

## 生成注意事项

1. **路径区分**：
   - 主HTML文件（`{姓名}_简历.html`）：模板路径用 `./templates/xxx.html`
   - templates目录下的模板：模板路径用 `./xxx.html`

2. **当前模板标记**：每个模板文件中，对应的模板项添加 `active` 类

3. **Tech模板打印**：深色模板打印时需切换为白色背景，通过 `@media print` 中覆盖 CSS 变量实现

4. **文件名**：
   - PDF：`{姓名}_简历_{日期}.pdf`
   - PNG：`{姓名}_简历_{日期}.png`

5. **oklch 兼容**：oklch 在现代浏览器中已广泛支持。如需兼容旧浏览器，提供 `rgb()` 回退值

6. **字体加载**：Noto Sans SC / Noto Serif SC / JetBrains Mono 可通过 Google Fonts CDN 加载：
   ```html
   <link rel="preconnect" href="https://fonts.googleapis.com">
   <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Noto+Sans+SC:wght@300;400;500;700;900&family=Noto+Serif+SC:wght@400;600;700&display=swap" rel="stylesheet">
   ```
