# Blog

```html markup
{% for item in document.get_plugin('blog').items %}
<div class="livemark-blog-item">
  <h2><a href="{{ item.relpath }}.html">{{ item.document.name }}</a></h2>
  <div class="row">
    <div class="col-8">
      <p>
        <strong>
          By {{ item.document.get_plugin('blog').author }}
          on {{ item.document.get_plugin('blog').date }}
        </strong>
      </p>
      {{ item.document.get_plugin('blog').description }}
      <a href="{{ item.relpath }}.html">Read more &raquo;</a>
    </div>
    <div class="col-4">
      <img src="{{ item.document.get_plugin('blog').image }}" />
    </div>
  </div>
</div>
{% endfor %}
```
