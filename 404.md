---
site:
  description: This page is not found
signs: false
---

# Not Found

```markdown remark type=danger
This page is not found
```

Return to the <a href="/">home</a> page.

```html markup
<script>
for (const item of JSON.parse('{{ document.get_plugin('redirect').items | tojson }}')) {
  if (location.href === item.prev) {
    location.href = item.next`;
  } else if (location.pathname === `/${item.prev}.html`) {
    location.href = `/${item.next}.html`;
  }
}
</script>
```
