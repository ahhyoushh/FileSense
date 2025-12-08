---
title: "Documentation Template"
permalink: /wiki/template/
---

# 📝 FileSense Documentation Template

Use this template when creating new wiki pages.

---

## Basic Page Structure

```markdown
---
title: "Page Title"
permalink: /wiki/page-slug/

---

# 🎯 Page Title

Brief introduction explaining what this page covers.

---

## Section Heading

Content goes here.

### Subsection

More detailed content.

---

## Code Examples

\`\`\`python
# Python code
def example():
    return "Hello World"
\`\`\`

\`\`\`bash
# Bash commands
python scripts/script.py --dir ./files
\`\`\`

---

## Tables

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

---

## Notice Blocks

> **Info Block**
>
> **Success Block**
>
> **Warning Block**
>
> **Danger Block**

---

## Mermaid Diagrams

\`\`\`mermaid
flowchart LR
    A[Start] --> B[Process]
    B --> C[End]
\`\`\`

---

## Links

- Internal: [Getting Started](/FileSense/wiki/getting-started/)
- External: [GitHub](https://github.com/ahhyoushh/FileSense)

---

[← Back to Home](/FileSense/wiki/)
\`\`\`

---

## Styling Guidelines

### Emojis for Visual Hierarchy

Use emojis to make sections visually distinct:

- 🎯 Goals/Objectives
- 📊 Data/Metrics
- 🔧 Technical Details
- 💡 Tips/Insights
- ⚠️ Warnings
- ✅ Success/Best Practices
- ❌ Failures/Don'ts
- 🚀 Quick Start/Actions
- 📚 Resources/References
- 🎓 Learning/Education

### Notice Blocks

```markdown
> **This is important information**
>
> **This worked well**
>
> **Be careful about this**
>
> **This is critical - don't ignore**
```

### Code Blocks with Language

Always specify the language for syntax highlighting:

```markdown
\`\`\`python
# Python code
\`\`\`

\`\`\`bash
# Bash commands
\`\`\`

\`\`\`json
{
  "key": "value"
}
\`\`\`

\`\`\`yaml
key: value
\`\`\`
```

### Tables

Use tables for structured data:

```markdown
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
```

### Mermaid Diagrams

For flowcharts and diagrams:

```markdown
\`\`\`mermaid
flowchart TD
    A[Input] --> B[Process]
    B --> C{Decision}
    C -->|Yes| D[Output A]
    C -->|No| E[Output B]
\`\`\`
```

---

## Page Types

### Tutorial Pages

Structure:
1. Introduction
2. Prerequisites
3. Step-by-step instructions
4. Expected output
5. Troubleshooting
6. Next steps

### Reference Pages

Structure:
1. Overview
2. API/Function list
3. Parameters
4. Return values
5. Examples
6. Related functions

### Concept Pages

Structure:
1. What is it?
2. Why does it matter?
3. How does it work?
4. When to use it?
5. Examples
6. Further reading

---

## Checklist for New Pages

- [ ] Title and permalink set
- [ ] TOC enabled
- [ ] Introduction paragraph
- [ ] Sections with clear headings
- [ ] Code examples (if applicable)
- [ ] Tables for structured data
- [ ] Notice blocks for important info
- [ ] Links to related pages
- [ ] Back to home link at bottom
- [ ] Spell-checked
- [ ] Tested locally

---

## Example Pages

**Good Examples:**
- [Getting Started](/FileSense/wiki/getting-started/) - Tutorial style
- [Architecture](/FileSense/wiki/pipeline/) - Technical reference
- [Lessons Learned](/FileSense/wiki/lessons-learned/) - Concept/insight page

---

## Tips for Writing

### Be Concise

❌ Bad:
> "In this section, we will discuss the various different ways in which you can potentially configure the system settings to optimize performance."

✅ Good:
> "Configure these settings to optimize performance:"

### Use Active Voice

❌ Bad:
> "The file is processed by the system."

✅ Good:
> "FileSense processes the file."

### Show, Don't Just Tell

❌ Bad:
> "FileSense is fast."

✅ Good:
> "FileSense processes 75 files in 5 seconds (0.27s per file)."

### Use Examples

Always include:
- Code examples
- Command examples
- Expected output
- Common use cases

---

## Markdown Cheatsheet

### Headers

```markdown
# H1
## H2
### H3
#### H4
```

### Emphasis

```markdown
*italic*
**bold**
***bold italic***
~~strikethrough~~
```

### Lists

```markdown
- Unordered item
- Another item
  - Nested item

1. Ordered item
2. Another item
   1. Nested item
```

### Links

```markdown
[Link text](URL)
[Internal link](/FileSense/wiki/page/)
```

### Images

```markdown
![Alt text](/path/to/image.png)
```

### Blockquotes

```markdown
> This is a quote
```

### Horizontal Rule

```markdown
---
```

---

## Publishing Workflow

1. **Create** the markdown file in `wiki/`
2. **Add** to navigation in `_data/navigation.yml`
3. **Test** locally (if possible)
4. **Commit** and push to GitHub
5. **Verify** on GitHub Pages

---

## Questions?

- Check existing pages for examples
- Review [Contrast Theme documentation](https://github.com/niklasbuschmann/contrast)
- Ask in GitHub discussions

---

[← Back to Home](/FileSense/wiki/)
