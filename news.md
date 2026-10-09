---
title: "News"
permalink: /news/
---
# News

## From the university news archive

These are dated summaries of announcements on the existing website. They retain their historical context rather than being presented as new updates.

<div class="news-list">
{% for item in site.data.news %}<article><time>{{ item.date }}</time><p>{{ item.summary }}</p></article>{% endfor %}
</div>

Source and older announcements: [CORE news archive](https://corelab.engin.umich.edu/news/).
