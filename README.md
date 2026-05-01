# JunSkill

Claude Code 个人技能库，收集自建的工具类 Skill。

## Skills 一览

| Skill | 说明 | 安装方式 |
|-------|------|----------|
| [memory-sync](memory-sync/) | 从历史会话中提炼用户信息，增量更新记忆系统。支持增量/全量两种模式 | 复制到 `~/.claude/skills/memory-sync/` |
| [wenshan](wenshan/) | 方文山风格歌词创作引擎，支持10大风格（中国风、暗黑哥特、甜蜜情歌等） | 复制到 `~/.claude/skills/wenshan/` |
| [bencao-remedy](bencao-remedy/) | 本草纲目健康顾问，根据症状推荐中医药和食疗方案 | 复制到 `~/.claude/skills/bencao-remedy/` |
| [sunzi-strategy](sunzi-strategy/) | 孙子兵法与三十六计谋略顾问，适用于商业竞争、职场、谈判等场景 | 复制到 `~/.claude/skills/sunzi-strategy/` |
| [interview-resume-generator](interview-resume-generator/) | 访谈式简历生成器，通过智能问答引导生成专业简历 | 复制到 `~/.claude/skills/interview-resume-generator/` |
| [deploying-to-production](deploying-to-production/) | 一键部署 Next.js 项目到 Vercel，自动创建 GitHub 仓库和 CI/CD | 复制到 `~/.claude/skills/deploying-to-production/` |

## 安装方法

将任意 Skill 目录复制到 Claude Code 的 skills 目录即可：

```bash
# 方式一：手动复制
cp -r memory-sync ~/.claude/skills/

# 方式二：克隆整个仓库后软链接
git clone git@github.com:jun7799/junskill.git
ln -s $(pwd)/junskill/memory-sync ~/.claude/skills/memory-sync
```

安装后在 Claude Code 中触发对应关键词即可使用。

## Skill 结构

每个 Skill 遵循统一结构：

```
skill-name/
├── SKILL.md          # 主文件（触发条件、工作流）
└── references/       # 参考文档（可选）
```

## 贡献

欢迎提交 Issue 和 PR 添加新 Skill 或改进现有 Skill。

## License

MIT
