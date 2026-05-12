# Boss直聘职位猎手 - Claude Code Skill

Boss直聘职位搜索、智能匹配与飞书多维表格收录的 Claude Code Skill。

## 功能

- 多城市职位搜索：通过 web-access 直连用户 Chrome，搜索指定城市的 Boss 直聘职位
- 智能匹配打分：根据用户简历自动给职位打推荐指数（1-5 分）
- 飞书多维表格收录：一键将职位数据批量导入飞书多维表格

## 前置依赖

- Claude Code
- [web-access](../web-access/) Skill（CDP Proxy）
- Chrome 浏览器已登录 Boss 直聘

## 安装

将整个 `boss-job-hunter/` 目录放入 `~/.claude/skills/` 即可：

```
~/.claude/skills/boss-job-hunter/
  SKILL.md
  README.md
```

## 使用

在 Claude Code 中通过 `/boss-job-hunter` 触发，或自然语言：

- "帮我搜一下广州的 AI 产品经理职位"
- "找工作，深圳+杭州，关键词产品总监"
- "Boss直聘搜职位"

## 支持城市

北京、上海、广州、深圳、杭州、惠州、东莞、佛山、珠海、成都、武汉、长沙等

## License

MIT
