# 访谈式简历生成器 | Interview Resume Generator

通过智能访谈引导用户生成专业简历，支持 Markdown 和 HTML 两种输出格式。

## 功能特点

- **双路径入口**：
  - 路径A：从零开始，通过智能访谈生成全新简历
  - 路径B：已有简历，AI 分析后优化改进（支持纯文本/Markdown/Word/PDF）
- **智能访谈**：使用 AskUserQuestion 工具进行交互式问答
- **简历优化**：AI 自动分析结构完整性、内容质量（STAR法则）、行业适配性，输出优化报告
- **场景适配**：支持社招、校招、转行三种求职场景
- **行业引导**：针对6大行业定制追问策略
  - 技术研发：追问技术深度、架构设计、性能优化
  - 产品：追问用户洞察、数据驱动、竞品分析
  - 设计：追问设计理念、用户研究、设计系统
  - 运营：追问增长数据、活动ROI、用户留存
  - 市场销售：追问业绩数据、客户管理、品牌影响力
  - 职能支持：追问流程优化、成本控制、团队支持
- **质量评估**：根据回答质量自动调整追问深度（STAR法则）
- **双格式输出**：
  - Markdown 简历（适合版本管理）
  - HTML 简历（4种设计模板，基于 Claude Design 方法论，支持PDF/PNG导出）

## 触发方式

- 说"帮我写简历"、"生成简历"、"做一份简历"
- 说"我要找工作，需要简历"
- 使用 `/interview-resume-generator` 命令

## 访谈流程

```
阶段0: 场景识别
    ↓
阶段0.5: 行业识别（定制追问策略）
    ↓
阶段1: 基本信息（姓名/联系方式/求职意向）
    ↓
阶段2: 教育背景
    ↓
阶段3: 工作经历（STAR法则 + 行业定制追问）
    ↓
阶段4: 项目经历
    ↓
阶段5: 技能评估
    ↓
阶段6: 自我评价
    ↓
生成 Markdown 简历
    ↓
阶段7: 生成 HTML 版本（可选）
```

## HTML 模板预览

| 模板 | 风格 | 特点 | 适用场景 |
|------|------|------|----------|
| 现代简约 | 双栏布局 / oklch蓝 | 排版驱动，CSS Grid | 互联网、科技公司 |
| 经典传统 | 衬线字体 / 深色调 | 横线分隔，正式感 | 国企、金融、政府 |
| 创意设计 | 非对称排版 / 珊瑚色 | 强烈字重对比，大胆节奏 | 设计、创意、广告 |
| 科技暗黑 | 等宽字体 / 终端绿 | 终端风格，高对比度 | 程序员、技术岗 |

## 安装方式

将此目录复制到 Claude Code 的 skills 目录：

```bash
# Windows
cp -r interview-resume-generator ~/.claude/skills/

# macOS/Linux
cp -r interview-resume-generator ~/.claude/skills/
```

## 目录结构

```
interview-resume-generator/
├── SKILL.md                    # 核心技能定义
├── README.md                   # 说明文档
├── references/
│   ├── question_bank.md        # 访谈问题库
│   └── quality_indicators.md   # 回答质量判断标准
└── assets/
    ├── templates/              # Markdown 简历模板
    │   ├── social_recruit.md   # 社招模板
    │   ├── campus_recruit.md   # 校招模板
    │   └── career_change.md    # 转行模板
    ├── html-templates/         # HTML 模板参考
    │   └── TEMPLATE_REFERENCE.md
    └── demo-screenshots/       # 演示页面
        ├── case1_social_recruit.html
        ├── case2_campus_recruit.html
        └── case3_career_change.html
```

## 使用示例

```
用户: 帮我写简历
助手: 你好！我是简历小助手，接下来我会通过几个问题帮你生成一份专业简历。
      首先，请问你目前处于什么求职阶段？

用户: 社招 - 有工作经验
助手: [记录场景类型，开始收集基本信息...]
```

## 回答质量评估

系统会根据以下维度评估回答质量：

| 维度 | 分值 | 判断标准 |
|-----|------|---------|
| 具体性 | 0-3分 | 是否有具体的场景、角色、任务描述 |
| 量化程度 | 0-3分 | 是否有数字、比例、具体成果 |
| 完整性 | 0-2分 | 是否回答了问题的核心要点 |
| 亮点度 | 0-2分 | 是否有独特价值、突出成就 |

根据总分自动调整追问策略：
- 0-3分：必须追问，提供示例引导
- 4-6分：适度追问，挖掘更多细节
- 7-8分：简单确认，记录亮点
- 9-10分：深度挖掘，成为简历核心卖点

## 技术栈

- Claude Code Skill System
- AskUserQuestion Tool
- html2canvas (PNG导出)

## License

GPL-3.0
